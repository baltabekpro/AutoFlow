"""
CRUD operations for database entities
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import Optional, List
from fastapi import HTTPException, status

from app.models import User, Client, Vehicle, Order, Inventory, OrderItem, OrderStatus
from app.schemas import (
    UserCreate, ClientCreate, ClientUpdate, VehicleCreate,
    OrderCreate, InventoryCreate, InventoryUpdate, OrderItemCreate
)
from app.auth import get_password_hash


# ============== User CRUD ==============
def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user"""
    # Check if login already exists
    existing_user = db.query(User).filter(User.login == user.login).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login already registered"
        )
    
    db_user = User(
        full_name=user.full_name,
        role=user.role,
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


# ============== Client CRUD ==============
def get_clients(db: Session, search: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Client]:
    """Get list of clients with optional search"""
    query = db.query(Client)
    if search:
        query = query.filter(
            or_(
                Client.name.ilike(f"%{search}%"),
                Client.phone.ilike(f"%{search}%")
            )
        )
    return query.offset(skip).limit(limit).all()


def create_client(db: Session, client: ClientCreate) -> Client:
    """Create a new client"""
    db_client = Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def get_client(db: Session, client_id: int) -> Optional[Client]:
    """Get client by ID"""
    return db.query(Client).filter(Client.id == client_id).first()


def update_client(db: Session, client_id: int, client_update: ClientUpdate) -> Optional[Client]:
    """Update client information"""
    db_client = get_client(db, client_id)
    if not db_client:
        return None
    
    update_data = client_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_client, field, value)
    
    db.commit()
    db.refresh(db_client)
    return db_client


# ============== Vehicle CRUD ==============
def get_client_vehicles(db: Session, client_id: int) -> List[Vehicle]:
    """Get all vehicles for a client"""
    return db.query(Vehicle).filter(Vehicle.client_id == client_id).all()


def create_vehicle(db: Session, vehicle: VehicleCreate) -> Vehicle:
    """Create a new vehicle"""
    # Verify client exists
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


# ============== Inventory CRUD ==============
def get_inventory(db: Session, search: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Inventory]:
    """Get inventory list with optional search"""
    query = db.query(Inventory)
    if search:
        query = query.filter(
            or_(
                Inventory.name.ilike(f"%{search}%"),
                Inventory.article.ilike(f"%{search}%")
            )
        )
    return query.offset(skip).limit(limit).all()


def create_inventory_item(db: Session, item: InventoryCreate) -> Inventory:
    """Create a new inventory item"""
    # Check if article already exists
    existing_item = db.query(Inventory).filter(Inventory.article == item.article).first()
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Article already exists"
        )
    
    db_item = Inventory(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_inventory_item(db: Session, item_id: int) -> Optional[Inventory]:
    """Get inventory item by ID"""
    return db.query(Inventory).filter(Inventory.id == item_id).first()


def update_inventory_item(db: Session, item_id: int, item_update: InventoryUpdate) -> Optional[Inventory]:
    """Update inventory item"""
    db_item = get_inventory_item(db, item_id)
    if not db_item:
        return None
    
    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item


# ============== Order CRUD ==============
def get_orders(db: Session, status_filter: Optional[OrderStatus] = None, skip: int = 0, limit: int = 100) -> List[Order]:
    """Get list of orders with optional status filter"""
    query = db.query(Order)
    if status_filter:
        query = query.filter(Order.status == status_filter)
    return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


def create_order(db: Session, order: OrderCreate) -> Order:
    """Create a new order"""
    # Verify vehicle exists
    vehicle = get_vehicle(db, order.vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # Verify mechanic exists if provided
    if order.mechanic_id:
        mechanic = db.query(User).filter(User.id == order.mechanic_id).first()
        if not mechanic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mechanic not found"
            )
    
    db_order = Order(**order.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def get_order(db: Session, order_id: int) -> Optional[Order]:
    """Get order by ID with all relationships"""
    return db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.inventory_item),
        joinedload(Order.vehicle).joinedload(Vehicle.client),
        joinedload(Order.mechanic)
    ).filter(Order.id == order_id).first()


def update_order_status(db: Session, order_id: int, new_status: OrderStatus) -> Optional[Order]:
    """Update order status and handle inventory deduction"""
    db_order = get_order(db, order_id)
    if not db_order:
        return None
    
    old_status = db_order.status
    db_order.status = new_status
    
    # If order is being closed, deduct items from inventory
    if new_status == OrderStatus.closed and old_status != OrderStatus.closed:
        for order_item in db_order.items:
            if order_item.inventory_id:
                inventory_item = get_inventory_item(db, order_item.inventory_id)
                if inventory_item:
                    new_quantity = inventory_item.quantity - order_item.quantity
                    if new_quantity < 0:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Insufficient inventory for item: {inventory_item.name}"
                        )
                    inventory_item.quantity = new_quantity
    
    db.commit()
    db.refresh(db_order)
    return db_order


def recalculate_order_total(db: Session, order_id: int) -> float:
    """Recalculate order total price based on items"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return 0.0
    
    total = sum(item.price_at_time * item.quantity for item in order.items)
    order.total_price = total
    db.commit()
    return total


# ============== OrderItem CRUD ==============
def add_order_item(db: Session, order_id: int, item: OrderItemCreate) -> OrderItem:
    """Add item to order"""
    # Verify order exists
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # If inventory_id is provided, get price from inventory and check stock
    price_at_time = 0.0
    description = item.description
    
    if item.inventory_id:
        inventory_item = get_inventory_item(db, item.inventory_id)
        if not inventory_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory item not found"
            )
        
        # Check if enough stock is available
        if inventory_item.quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient inventory. Available: {inventory_item.quantity}"
            )
        
        price_at_time = inventory_item.price
        if not description:
            description = inventory_item.name
    
    db_item = OrderItem(
        order_id=order_id,
        inventory_id=item.inventory_id,
        description=description,
        quantity=item.quantity,
        price_at_time=price_at_time
    )
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # Recalculate order total
    recalculate_order_total(db, order_id)
    
    return db_item
