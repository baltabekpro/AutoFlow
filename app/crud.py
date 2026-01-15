"""
CRUD operations for database entities
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from typing import Optional, List
from fastapi import HTTPException, status
from datetime import datetime
import uuid
import json

from app.models import (
    User, Client, Vehicle, Order, Inventory, OrderItem, OrderStatus,
    Service, OrderItemType, ClientType, EmployeeStatus
)
from app.schemas import (
    EmployeeCreate, EmployeeInput, EmployeeResponse,
    ClientInput, Client as ClientSchema,
    VehicleCreate, OrderInput, Order as OrderSchema,
    InventoryItemInput, InventoryItem as InventoryItemSchema,
    ServiceInput, Service as ServiceSchema,
    OrderItemCreate
)
from app.auth import get_password_hash


# ============== Employee/User CRUD ==============
def create_employee(db: Session, employee: EmployeeInput) -> User:
    """Create a new employee"""
    # Generate login from name
    base_login = employee.name.lower().replace(" ", "_")
    login = base_login + str(uuid.uuid4().hex[:4])
    
    # Generate a random secure password
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()"
    password = ''.join(secrets.choice(alphabet) for i in range(16))
    
    db_user = User(
        name=employee.name,
        role=employee.role,
        phone=employee.phone,
        status=employee.status,
        login=login,
        password_hash=get_password_hash(password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # In a real application, you would send this password to the user via email
    # For now, we'll log it (in production, use proper secure password delivery)
    print(f"Created employee {employee.name} with login: {login} and password: {password}")
    
    return db_user


def create_user(db: Session, user: EmployeeCreate) -> User:
    """Create a new user with login and password"""
    existing_user = db.query(User).filter(User.login == user.login).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login already registered"
        )
    
    db_user = User(
        name=user.name,
        role=user.role,
        phone=user.phone,
        status=user.status,
        login=user.login,
        password_hash=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_login(db: Session, login: str) -> Optional[User]:
    """Get user by login"""
    return db.query(User).filter(User.login == login).first()


def get_employees(db: Session) -> List[User]:
    """Get all employees"""
    return db.query(User).all()


def update_employee(db: Session, employee_id: int, employee: EmployeeResponse) -> Optional[User]:
    """Update employee"""
    db_employee = db.query(User).filter(User.id == employee_id).first()
    if not db_employee:
        return None
    
    db_employee.name = employee.name
    db_employee.role = employee.role
    db_employee.phone = employee.phone
    db_employee.status = employee.status
    
    db.commit()
    db.refresh(db_employee)
    return db_employee


def delete_employee(db: Session, employee_id: int) -> bool:
    """Delete employee"""
    db_employee = db.query(User).filter(User.id == employee_id).first()
    if not db_employee:
        return False
    
    db.delete(db_employee)
    db.commit()
    return True


# ============== Client CRUD ==============
def get_clients(db: Session, search: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Client]:
    """Get list of clients with optional search"""
    query = db.query(Client)
    if search:
        query = query.filter(
            or_(
                Client.name.ilike(f"%{search}%"),
                Client.phone.ilike(f"%{search}%"),
                Client.email.ilike(f"%{search}%")
            )
        )
    return query.offset(skip).limit(limit).all()


def create_client(db: Session, client: ClientInput) -> Client:
    """Create a new client"""
    db_client = Client(
        name=client.name,
        phone=client.phone,
        email=client.email,
        type=client.type
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def get_client(db: Session, client_id: int) -> Optional[Client]:
    """Get client by ID"""
    return db.query(Client).filter(Client.id == client_id).first()


def update_client_full(db: Session, client_id: int, client: ClientSchema) -> Optional[Client]:
    """Update client information"""
    db_client = get_client(db, client_id)
    if not db_client:
        return None
    
    db_client.name = client.name
    db_client.phone = client.phone
    db_client.email = client.email
    db_client.type = client.type
    
    db.commit()
    db.refresh(db_client)
    return db_client


def delete_client(db: Session, client_id: int) -> bool:
    """Delete client"""
    db_client = get_client(db, client_id)
    if not db_client:
        return False
    
    db.delete(db_client)
    db.commit()
    return True


# ============== Vehicle CRUD ==============
def get_client_vehicles(db: Session, client_id: int) -> List[Vehicle]:
    """Get all vehicles for a client"""
    return db.query(Vehicle).filter(Vehicle.client_id == client_id).all()


def create_vehicle(db: Session, vehicle: VehicleCreate) -> Vehicle:
    """Create a new vehicle"""
    client = get_client(db, vehicle.client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    db_vehicle = Vehicle(**vehicle.model_dump())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


def get_vehicle(db: Session, vehicle_id: int) -> Optional[Vehicle]:
    """Get vehicle by ID"""
    return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()


# ============== Service CRUD ==============
def get_services(db: Session, search: Optional[str] = None) -> List[Service]:
    """Get services list with optional search"""
    query = db.query(Service)
    if search:
        query = query.filter(Service.name.ilike(f"%{search}%"))
    return query.all()


def create_service(db: Session, service: ServiceInput) -> Service:
    """Create a new service"""
    db_service = Service(
        name=service.name,
        price=service.price,
        duration=service.duration
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


def get_service(db: Session, service_id: int) -> Optional[Service]:
    """Get service by ID"""
    return db.query(Service).filter(Service.id == service_id).first()


def update_service(db: Session, service_id: int, service: ServiceSchema) -> Optional[Service]:
    """Update service"""
    db_service = get_service(db, service_id)
    if not db_service:
        return None
    
    db_service.name = service.name
    db_service.price = service.price
    db_service.duration = service.duration
    
    db.commit()
    db.refresh(db_service)
    return db_service


def delete_service(db: Session, service_id: int) -> bool:
    """Delete service"""
    db_service = get_service(db, service_id)
    if not db_service:
        return False
    
    db.delete(db_service)
    db.commit()
    return True


# ============== Inventory CRUD ==============
def get_inventory(db: Session, search: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Inventory]:
    """Get inventory list with optional search"""
    query = db.query(Inventory)
    if search:
        query = query.filter(
            or_(
                Inventory.name.ilike(f"%{search}%"),
                Inventory.sku.ilike(f"%{search}%")
            )
        )
    return query.offset(skip).limit(limit).all()


def create_inventory_item(db: Session, item: InventoryItemInput) -> Inventory:
    """Create a new inventory item"""
    existing_item = db.query(Inventory).filter(Inventory.sku == item.sku).first()
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SKU already exists"
        )
    
    db_item = Inventory(
        name=item.name,
        sku=item.sku,
        quantity=item.quantity,
        price=item.price,
        location=item.location
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_inventory_item(db: Session, item_id: int) -> Optional[Inventory]:
    """Get inventory item by ID"""
    return db.query(Inventory).filter(Inventory.id == item_id).first()


def update_inventory_item_full(db: Session, item_id: int, item: InventoryItemSchema) -> Optional[Inventory]:
    """Update inventory item"""
    db_item = get_inventory_item(db, item_id)
    if not db_item:
        return None
    
    db_item.name = item.name
    db_item.sku = item.sku
    db_item.quantity = item.quantity
    db_item.price = item.price
    db_item.location = item.location
    
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_inventory_item(db: Session, item_id: int) -> bool:
    """Delete inventory item"""
    db_item = get_inventory_item(db, item_id)
    if not db_item:
        return False
    
    db.delete(db_item)
    db.commit()
    return True


# ============== Order CRUD ==============
def get_orders(db: Session, status_filter: Optional[OrderStatus] = None, search: Optional[str] = None, 
               skip: int = 0, limit: int = 100) -> List[Order]:
    """Get list of orders with optional status filter and search"""
    query = db.query(Order)
    if status_filter:
        query = query.filter(Order.status == status_filter)
    if search:
        query = query.filter(
            or_(
                Order.client_name.ilike(f"%{search}%"),
                Order.plate.ilike(f"%{search}%"),
                Order.vehicle.ilike(f"%{search}%")
            )
        )
    return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


def create_order(db: Session, order: OrderInput) -> Order:
    """Create a new order"""
    # Verify client exists
    client = get_client(db, order.client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Generate UUID for order
    order_id = str(uuid.uuid4())
    
    # Get client name if not provided
    client_name = order.client_name or client.name
    
    # Convert damages list to JSON string
    damages_str = json.dumps(order.damages) if order.damages else None
    
    db_order = Order(
        id=order_id,
        client_id=order.client_id,
        client_name=client_name,
        vehicle=order.vehicle,
        plate=order.plate,
        status=order.status or OrderStatus.draft,
        total=0.0,
        is_urgent=order.is_urgent or False,
        notes=order.notes,
        mileage=order.mileage,
        damages=damages_str
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Add items if provided
    if order.items:
        for item in order.items:
            add_order_item(db, order_id, item)
    
    # Refresh to get updated total
    db.refresh(db_order)
    
    return db_order


def get_order(db: Session, order_id: str) -> Optional[Order]:
    """Get order by ID with all relationships"""
    return db.query(Order).options(
        joinedload(Order.items),
        joinedload(Order.vehicle_obj),
        joinedload(Order.mechanic),
        joinedload(Order.client)
    ).filter(Order.id == order_id).first()


def update_order(db: Session, order_id: str, order: OrderSchema) -> Optional[Order]:
    """Update order"""
    db_order = get_order(db, order_id)
    if not db_order:
        return None
    
    db_order.client_id = order.client_id
    db_order.client_name = order.client_name
    db_order.vehicle = order.vehicle
    db_order.plate = order.plate
    db_order.status = order.status
    db_order.is_urgent = order.is_urgent
    db_order.notes = order.notes
    db_order.mileage = order.mileage
    
    # Convert damages list to JSON string
    if order.damages:
        db_order.damages = json.dumps(order.damages)
    
    db.commit()
    db.refresh(db_order)
    return db_order


def recalculate_order_total(db: Session, order_id: str) -> float:
    """Recalculate order total price based on items"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return 0.0
    
    total = sum(item.price * item.qty for item in order.items)
    order.total = total
    db.commit()
    return total


# ============== OrderItem CRUD ==============
def add_order_item(db: Session, order_id: str, item: OrderItemCreate) -> OrderItem:
    """Add item to order"""
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    db_item = OrderItem(
        order_id=order_id,
        inventory_id=item.inventory_id,
        service_id=item.service_id,
        name=item.name,
        price=item.price,
        qty=item.qty,
        type=item.type
    )
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # Recalculate order total
    recalculate_order_total(db, order_id)
    
    return db_item


# ============== Dashboard & Finance ==============
def get_dashboard_stats(db: Session) -> dict:
    """Get dashboard statistics"""
    # Calculate revenue from all completed orders
    completed_orders = db.query(Order).filter(Order.status == OrderStatus.done).all()
    revenue = sum(order.total for order in completed_orders)
    
    # Count active orders (not draft or done)
    active_orders = db.query(Order).filter(
        Order.status.in_([OrderStatus.pending, OrderStatus.diagnosis, OrderStatus.work, OrderStatus.parts])
    ).count()
    
    # Count orders pending release (done status)
    pending_release = db.query(Order).filter(Order.status == OrderStatus.done).count()
    
    # Total orders
    total_orders = db.query(Order).count()
    
    return {
        "revenue": revenue,
        "activeOrders": active_orders,
        "pendingRelease": pending_release,
        "totalOrders": total_orders
    }


def get_finance_report(db: Session, date_from: Optional[str] = None, date_to: Optional[str] = None) -> dict:
    """Get finance report"""
    query = db.query(Order).filter(Order.status == OrderStatus.done)
    
    # Apply date filters if provided
    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from)
            query = query.filter(Order.created_at >= from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to)
            query = query.filter(Order.created_at <= to_date)
        except ValueError:
            pass
    
    completed_orders = query.all()
    
    # Calculate revenue
    revenue = sum(order.total for order in completed_orders)
    
    # Calculate expenses (sum of part costs)
    expenses = 0.0
    for order in completed_orders:
        for item in order.items:
            if item.type == OrderItemType.part:
                expenses += item.price * item.qty
    
    # Calculate profit
    profit = revenue - expenses
    
    return {
        "revenue": revenue,
        "expenses": expenses,
        "profit": profit,
        "completedOrdersCount": len(completed_orders)
    }
