"""
FastAPI main application - AutoFlow Backend
Auto service management system - AutoMaster ERP API
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta, datetime
from contextlib import asynccontextmanager
import uuid
import json

from app.database import get_db, init_db
from app.models import User, OrderStatus, OrderItemType
from app.schemas import (
    Token, EmployeeCreate, EmployeeResponse, EmployeeInput,
    ClientInput, Client, ClientResponse,
    VehicleCreate, VehicleResponse,
    OrderInput, OrderResponse, OrderDetailResponse, Order,
    InventoryItemInput, InventoryItem, InventoryResponse,
    ServiceInput, Service,
    OrderItemCreate, OrderItem,
    DashboardStats, FinanceReport
)
from app.auth import (
    authenticate_user, create_access_token, get_current_user,
    get_current_admin_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from app import crud


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    init_db()
    yield
    # Shutdown (if needed in the future)


# Initialize FastAPI app
app = FastAPI(
    title="AutoMaster ERP API",
    description="API для управления процессами автосервиса (Заказы, Склад, Клиенты, Сотрудники).",
    version="1.1.0",
    lifespan=lifespan
)


# ============== Root Endpoint ==============
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "AutoMaster ERP API",
        "version": "1.1.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# ============== Authentication Endpoints ==============
@app.post("/api/auth/login", response_model=Token, tags=["Auth"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Вход в систему
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.login},
        expires_delta=access_token_expires
    )
    
    user_response = EmployeeResponse(
        id=user.id,
        name=user.name,
        role=user.role,
        phone=user.phone,
        status=user.status,
        login=user.login
    )
    
    return {"token": access_token, "user": user_response}


@app.get("/api/auth/me", response_model=EmployeeResponse, tags=["Auth"])
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Получить текущего пользователя
    """
    return EmployeeResponse(
        id=current_user.id,
        name=current_user.name,
        role=current_user.role,
        phone=current_user.phone,
        status=current_user.status,
        login=current_user.login
    )


# ============== Dashboard & Finance Endpoints ==============
@app.get("/api/stats", response_model=DashboardStats, tags=["Dashboard"])
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    KPI для дашборда
    """
    return crud.get_dashboard_stats(db)


@app.get("/api/finance/report", response_model=FinanceReport, tags=["Dashboard"])
async def get_finance_report(
    dateFrom: Optional[str] = None,
    dateTo: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Финансовый отчет
    Расчет выручки, расходов и прибыли на стороне сервера.
    """
    return crud.get_finance_report(db, dateFrom, dateTo)


# ============== Orders Endpoints ==============
@app.get("/api/orders", response_model=List[Order], tags=["Orders"])
async def get_orders(
    status: Optional[OrderStatus] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список заказов
    """
    return crud.get_orders(db, status_filter=status, search=search, skip=offset, limit=limit)


@app.post("/api/orders", response_model=Order, status_code=status.HTTP_201_CREATED, tags=["Orders"])
async def create_order(
    order: OrderInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создать новый заказ
    ID генерируется сервером.
    """
    return crud.create_order(db, order)


@app.get("/api/orders/{id}", response_model=Order, tags=["Orders"])
async def get_order(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить заказ по ID
    """
    order = crud.get_order(db, id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.put("/api/orders/{id}", response_model=Order, tags=["Orders"])
async def update_order(
    id: str,
    order: Order,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновить заказ
    """
    updated_order = crud.update_order(db, id, order)
    if not updated_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated_order


# ============== Inventory Endpoints ==============
@app.get("/api/inventory", response_model=List[InventoryItem], tags=["Inventory"])
async def get_inventory(
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список товаров
    """
    return crud.get_inventory(db, search=search, skip=offset, limit=limit)


@app.post("/api/inventory", response_model=InventoryItem, status_code=status.HTTP_201_CREATED, tags=["Inventory"])
async def create_inventory_item(
    item: InventoryItemInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Добавить товар
    """
    return crud.create_inventory_item(db, item)


@app.put("/api/inventory/{id}", tags=["Inventory"])
async def update_inventory_item(
    id: int,
    item: InventoryItem,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновить товар
    """
    updated_item = crud.update_inventory_item_full(db, id, item)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return {"message": "Обновлено"}


@app.delete("/api/inventory/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Inventory"])
async def delete_inventory_item(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удалить товар
    """
    success = crud.delete_inventory_item(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return


# ============== Services Endpoints ==============
@app.get("/api/services", response_model=List[Service], tags=["Services"])
async def get_services(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список услуг
    """
    return crud.get_services(db, search=search)


@app.post("/api/services", status_code=status.HTTP_201_CREATED, tags=["Services"])
async def create_service(
    service: ServiceInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создать услугу
    """
    return crud.create_service(db, service)


@app.put("/api/services/{id}", tags=["Services"])
async def update_service(
    id: int,
    service: Service,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновить услугу
    """
    updated_service = crud.update_service(db, id, service)
    if not updated_service:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"message": "Успешно"}


@app.delete("/api/services/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Services"])
async def delete_service(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удалить услугу
    """
    success = crud.delete_service(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Service not found")
    return


# ============== Clients Endpoints ==============
@app.get("/api/clients", response_model=List[Client], tags=["Clients"])
async def get_clients(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список клиентов
    """
    return crud.get_clients(db, search=search)


@app.post("/api/clients", status_code=status.HTTP_201_CREATED, tags=["Clients"])
async def create_client(
    client: ClientInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создать клиента
    """
    return crud.create_client(db, client)


@app.put("/api/clients/{id}", tags=["Clients"])
async def update_client(
    id: int,
    client: Client,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновить клиента
    """
    updated_client = crud.update_client_full(db, id, client)
    if not updated_client:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Обновлено"}


@app.delete("/api/clients/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Clients"])
async def delete_client(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удалить клиента
    """
    success = crud.delete_client(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Client not found")
    return


# ============== Employees Endpoints ==============
@app.get("/api/employees", response_model=List[EmployeeResponse], tags=["Employees"])
async def get_employees(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список сотрудников
    """
    return crud.get_employees(db)


@app.post("/api/employees", status_code=status.HTTP_201_CREATED, tags=["Employees"])
async def create_employee(
    employee: EmployeeInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Создать сотрудника
    """
    return crud.create_employee(db, employee)


@app.put("/api/employees/{id}", tags=["Employees"])
async def update_employee(
    id: int,
    employee: EmployeeResponse,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Обновить сотрудника
    """
    updated_employee = crud.update_employee(db, id, employee)
    if not updated_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Обновлено"}


@app.delete("/api/employees/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Employees"])
async def delete_employee(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Удалить сотрудника
    """
    success = crud.delete_employee(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Employee not found")
    return


# ============== Health Check ==============
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
