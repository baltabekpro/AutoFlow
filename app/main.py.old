"""
FastAPI main application - AutoFlow Backend
Auto service management system
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta
from contextlib import asynccontextmanager

from app.database import get_db, init_db
from app.models import User, UserRole, OrderStatus
from app.schemas import (
    Token, UserCreate, UserResponse, UserLogin,
    ClientCreate, ClientResponse, ClientUpdate,
    VehicleCreate, VehicleResponse,
    OrderCreate, OrderResponse, OrderDetailResponse, OrderStatusUpdate,
    InventoryCreate, InventoryResponse, InventoryUpdate,
    OrderItemCreate, OrderItemResponse
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
    title="AutoFlow API",
    description="Auto service management system backend",
    version="1.0.0",
    lifespan=lifespan
)


# ============== Root Endpoint ==============
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "AutoFlow API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# ============== Authentication Endpoints ==============
@app.post("/auth/login", response_model=Token, tags=["Auth"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login endpoint - returns JWT access token
    Use username field for login
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.login},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/auth/register", response_model=UserResponse, tags=["Auth"])
async def register(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Register new user (admin only)
    """
    return crud.create_user(db, user)


# ============== Client Endpoints ==============
@app.get("/clients/", response_model=List[ClientResponse], tags=["Clients"])
async def get_clients(
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of clients with optional search by name or phone
    """
    return crud.get_clients(db, search=search, skip=skip, limit=limit)


@app.post("/clients/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED, tags=["Clients"])
async def create_client(
    client: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new client
    """
    return crud.create_client(db, client)


@app.get("/clients/{client_id}", response_model=ClientResponse, tags=["Clients"])
async def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get client by ID
    """
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@app.patch("/clients/{client_id}", response_model=ClientResponse, tags=["Clients"])
async def update_client(
    client_id: int,
    client_update: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update client information
    """
    client = crud.update_client(db, client_id, client_update)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@app.get("/clients/{client_id}/vehicles", response_model=List[VehicleResponse], tags=["Clients"])
async def get_client_vehicles(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all vehicles for a specific client
    """
    # Verify client exists
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return crud.get_client_vehicles(db, client_id)


# ============== Vehicle Endpoints ==============
@app.post("/vehicles/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED, tags=["Vehicles"])
async def create_vehicle(
    vehicle: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Register a new vehicle
    """
    return crud.create_vehicle(db, vehicle)


@app.get("/vehicles/{vehicle_id}", response_model=VehicleResponse, tags=["Vehicles"])
async def get_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get vehicle by ID
    """
    vehicle = crud.get_vehicle(db, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


# ============== Order Endpoints ==============
@app.get("/orders/", response_model=List[OrderResponse], tags=["Orders"])
async def get_orders(
    status_filter: Optional[OrderStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of orders with optional status filter
    """
    return crud.get_orders(db, status_filter=status_filter, skip=skip, limit=limit)


@app.post("/orders/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, tags=["Orders"])
async def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new order
    """
    return crud.create_order(db, order)


@app.get("/orders/{order_id}", response_model=OrderDetailResponse, tags=["Orders"])
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific order
    """
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.patch("/orders/{order_id}/status", response_model=OrderResponse, tags=["Orders"])
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update order status
    When status is changed to 'closed', inventory is automatically deducted
    """
    order = crud.update_order_status(db, order_id, status_update.status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.post("/orders/{order_id}/add-item", response_model=OrderItemResponse, status_code=status.HTTP_201_CREATED, tags=["Orders"])
async def add_order_item(
    order_id: int,
    item: OrderItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add item (service or part) to order
    Order total price is automatically recalculated
    """
    return crud.add_order_item(db, order_id, item)


# ============== Inventory Endpoints ==============
@app.get("/inventory/", response_model=List[InventoryResponse], tags=["Inventory"])
async def get_inventory(
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get inventory list with optional search by name or article
    """
    return crud.get_inventory(db, search=search, skip=skip, limit=limit)


@app.post("/inventory/", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED, tags=["Inventory"])
async def create_inventory_item(
    item: InventoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new inventory item (admin only)
    """
    return crud.create_inventory_item(db, item)


@app.get("/inventory/{item_id}", response_model=InventoryResponse, tags=["Inventory"])
async def get_inventory_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get inventory item by ID
    """
    item = crud.get_inventory_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return item


@app.put("/inventory/{item_id}", response_model=InventoryResponse, tags=["Inventory"])
async def update_inventory_item(
    item_id: int,
    item_update: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update inventory item
    """
    item = crud.update_inventory_item(db, item_id, item_update)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return item


# ============== Health Check ==============
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
