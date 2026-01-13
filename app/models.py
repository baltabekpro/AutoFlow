"""
SQLAlchemy database models
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    """User roles enumeration"""
    admin = "admin"
    mechanic = "mechanic"


class OrderStatus(str, enum.Enum):
    """Order status enumeration"""
    new = "new"
    in_progress = "in_progress"
    ready = "ready"
    closed = "closed"


class User(Base):
    """User model - system users (admin, mechanics)"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.mechanic)
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
    
    # Relationships
    vehicles = relationship("Vehicle", back_populates="client", cascade="all, delete-orphan")


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
    orders = relationship("Order", back_populates="vehicle", cascade="all, delete-orphan")


class Order(Base):
    """Order model - service orders"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    mechanic_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.new, index=True)
    total_price = Column(Float, nullable=False, default=0.0)
    mileage = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="orders")
    mechanic = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class Inventory(Base):
    """Inventory model - parts and supplies storage"""
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    article = Column(String, nullable=False, unique=True, index=True)
    quantity = Column(Integer, nullable=False, default=0)
    price = Column(Float, nullable=False)
    
    # Relationships
    order_items = relationship("OrderItem", back_populates="inventory_item")


class OrderItem(Base):
    """OrderItem model - items/services in an order"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=True)
    description = Column(String, nullable=False)  # Service or part description
    quantity = Column(Integer, nullable=False, default=1)
    price_at_time = Column(Float, nullable=False)  # Price at the time of adding
    
    # Relationships
    order = relationship("Order", back_populates="items")
    inventory_item = relationship("Inventory", back_populates="order_items")
