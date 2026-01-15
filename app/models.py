"""
SQLAlchemy database models
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    """User roles enumeration"""
    admin = "admin"
    mechanic = "mechanic"


class EmployeeStatus(str, enum.Enum):
    """Employee status enumeration"""
    active = "active"
    vacation = "vacation"
    sick = "sick"


class OrderStatus(str, enum.Enum):
    """Order status enumeration"""
    draft = "draft"
    pending = "pending"
    diagnosis = "diagnosis"
    work = "work"
    parts = "parts"
    done = "done"


class ClientType(str, enum.Enum):
    """Client type enumeration"""
    private = "private"
    corporate = "corporate"


class OrderItemType(str, enum.Enum):
    """Order item type enumeration"""
    service = "service"
    part = "part"


class User(Base):
    """User model - system users (admin, mechanics) - also known as Employee"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Changed from full_name
    role = Column(String, nullable=False, default="mechanic")  # Changed to String for flexibility
    phone = Column(String, nullable=False)
    status = Column(Enum(EmployeeStatus), nullable=False, default=EmployeeStatus.active)
    login = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    
    # Relationships
    orders = relationship("Order", back_populates="mechanic")


class Client(Base):
    """Client model - customers"""
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=False, index=True)
    email = Column(String, nullable=True)
    type = Column(Enum(ClientType), nullable=False, default=ClientType.private)
    
    # Relationships
    vehicles = relationship("Vehicle", back_populates="client", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="client")


class Vehicle(Base):
    """Vehicle model - client vehicles"""
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    license_plate = Column(String, nullable=False, index=True)
    vin = Column(String, nullable=True, index=True)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    
    # Relationships
    client = relationship("Client", back_populates="vehicles")
    orders = relationship("Order", back_populates="vehicle_obj", cascade="all, delete-orphan")


class Order(Base):
    """Order model - service orders"""
    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True)  # Changed to String for UUID support
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)  # Made optional
    mechanic_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # New fields to match OpenAPI spec
    client_name = Column(String, nullable=True)  # Denormalized for quick access
    vehicle = Column(String, nullable=True)  # e.g., "Toyota Camry"
    plate = Column(String, nullable=True)  # License plate
    
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.draft, index=True)
    total = Column(Float, nullable=False, default=0.0)  # Renamed from total_price
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    # Additional fields
    is_urgent = Column(Boolean, nullable=False, default=False)
    notes = Column(Text, nullable=True)
    mileage = Column(Integer, nullable=True)
    damages = Column(Text, nullable=True)  # Store as JSON string or comma-separated
    
    # Relationships
    vehicle_obj = relationship("Vehicle", back_populates="orders")
    mechanic = relationship("User", back_populates="orders")
    client = relationship("Client", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class Inventory(Base):
    """Inventory model - parts and supplies storage"""
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    sku = Column(String, nullable=False, unique=True, index=True)  # Changed from article
    quantity = Column(Integer, nullable=False, default=0)
    price = Column(Float, nullable=False)
    location = Column(String, nullable=False)  # New field
    
    # Relationships
    order_items = relationship("OrderItem", back_populates="inventory_item")


class OrderItem(Base):
    """OrderItem model - items/services in an order"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)  # Changed to String
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)  # New field
    
    name = Column(String, nullable=False)  # Changed from description
    price = Column(Float, nullable=False)  # Changed from price_at_time
    qty = Column(Integer, nullable=False, default=1)  # Changed from quantity
    type = Column(Enum(OrderItemType), nullable=False)  # New field
    
    # Relationships
    order = relationship("Order", back_populates="items")
    inventory_item = relationship("Inventory", back_populates="order_items")
    service = relationship("Service", back_populates="order_items")


class Service(Base):
    """Service model - service catalog"""
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    duration = Column(Float, nullable=False)  # Duration in hours
    
    # Relationships
    order_items = relationship("OrderItem", back_populates="service")
