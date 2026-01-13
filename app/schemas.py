"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models import UserRole, OrderStatus


# ============== Auth Schemas ==============
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    login: Optional[str] = None


class UserLogin(BaseModel):
    login: str
    password: str


# ============== User Schemas ==============
class UserBase(BaseModel):
    full_name: str
    role: UserRole
    login: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ============== Client Schemas ==============
class ClientBase(BaseModel):
    name: str
    phone: str


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None


class ClientResponse(ClientBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ============== Vehicle Schemas ==============
class VehicleBase(BaseModel):
    client_id: int
    license_plate: str
    vin: Optional[str] = None
    brand: str
    model: str


class VehicleCreate(VehicleBase):
    pass


class VehicleResponse(VehicleBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ============== Inventory Schemas ==============
class InventoryBase(BaseModel):
    name: str
    article: str
    quantity: int = Field(ge=0)
    price: float = Field(ge=0)


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    name: Optional[str] = None
    article: Optional[str] = None
    quantity: Optional[int] = Field(default=None, ge=0)
    price: Optional[float] = Field(default=None, ge=0)


class InventoryResponse(InventoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ============== OrderItem Schemas ==============
class OrderItemBase(BaseModel):
    inventory_id: Optional[int] = None
    description: str
    quantity: int = Field(ge=1)
    price_at_time: float = Field(ge=0)


class OrderItemCreate(BaseModel):
    inventory_id: Optional[int] = None
    description: str
    quantity: int = Field(ge=1, default=1)


class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    model_config = ConfigDict(from_attributes=True)


# ============== Order Schemas ==============
class OrderBase(BaseModel):
    vehicle_id: int
    mechanic_id: Optional[int] = None
    mileage: Optional[int] = None


class OrderCreate(OrderBase):
    pass


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderResponse(OrderBase):
    id: int
    status: OrderStatus
    total_price: float
    created_at: datetime
    items: List[OrderItemResponse] = []
    model_config = ConfigDict(from_attributes=True)


class OrderDetailResponse(OrderResponse):
    """Extended order response with related data"""
    vehicle: VehicleResponse
    mechanic: Optional[UserResponse] = None
    model_config = ConfigDict(from_attributes=True)
