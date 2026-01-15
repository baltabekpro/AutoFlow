"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from app.models import OrderStatus, ClientType, EmployeeStatus, OrderItemType

if TYPE_CHECKING:
    pass


# ============== Employee Schemas ==============
class EmployeeBase(BaseModel):
    name: str
    role: str
    phone: str
    status: EmployeeStatus


class EmployeeInput(EmployeeBase):
    pass


class EmployeeCreate(EmployeeBase):
    login: str
    password: str


class EmployeeResponse(EmployeeBase):
    id: int
    login: str
    model_config = ConfigDict(from_attributes=True)


# ============== Auth Schemas ==============
class Token(BaseModel):
    token: str
    user: EmployeeResponse


class TokenData(BaseModel):
    login: Optional[str] = None


class UserLogin(BaseModel):
    login: str
    password: str


# ============== Client Schemas ==============
class ClientBase(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    type: ClientType


class ClientInput(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    type: ClientType


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    type: Optional[ClientType] = None


class Client(ClientBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ClientResponse(Client):
    pass


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


# ============== Service Schemas ==============
class ServiceBase(BaseModel):
    name: str
    price: float
    duration: float


class ServiceInput(ServiceBase):
    pass


class Service(ServiceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ============== Inventory Schemas ==============
class InventoryItemBase(BaseModel):
    name: str
    sku: str
    quantity: int = Field(ge=0)
    price: float = Field(ge=0)
    location: str


class InventoryItemInput(InventoryItemBase):
    pass


class InventoryItem(InventoryItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class InventoryCreate(InventoryItemBase):
    pass


class InventoryUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    quantity: Optional[int] = Field(default=None, ge=0)
    price: Optional[float] = Field(default=None, ge=0)
    location: Optional[str] = None


class InventoryResponse(InventoryItem):
    pass


# ============== OrderItem Schemas ==============
class OrderItemBase(BaseModel):
    name: str
    price: float
    qty: float
    type: OrderItemType


class OrderItem(OrderItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class OrderItemCreate(BaseModel):
    inventory_id: Optional[int] = Field(default=None, alias="inventoryId")
    service_id: Optional[int] = Field(default=None, alias="serviceId")
    name: str
    price: float
    qty: float = 1
    type: OrderItemType
    
    model_config = ConfigDict(populate_by_name=True)


class OrderItemResponse(OrderItem):
    pass


# ============== Order Schemas ==============
class OrderBase(BaseModel):
    client_id: int = Field(alias="clientId")
    client_name: Optional[str] = Field(default=None, alias="clientName")
    vehicle: Optional[str] = None
    plate: Optional[str] = None
    status: OrderStatus = OrderStatus.draft
    is_urgent: Optional[bool] = Field(default=False, alias="isUrgent")
    notes: Optional[str] = None
    mileage: Optional[int] = None
    damages: Optional[List[str]] = None
    
    model_config = ConfigDict(populate_by_name=True)


class OrderInput(BaseModel):
    client_id: int = Field(alias="clientId")
    client_name: Optional[str] = Field(default=None, alias="clientName")
    vehicle: str
    plate: str
    status: Optional[OrderStatus] = OrderStatus.draft
    items: List[OrderItemCreate]
    is_urgent: Optional[bool] = Field(default=False, alias="isUrgent")
    notes: Optional[str] = None
    mileage: Optional[int] = None
    damages: Optional[List[str]] = None
    
    model_config = ConfigDict(populate_by_name=True)


class OrderCreate(BaseModel):
    client_id: int = Field(alias="clientId")
    client_name: Optional[str] = Field(default=None, alias="clientName")
    vehicle: str
    plate: str
    status: Optional[OrderStatus] = OrderStatus.draft
    items: Optional[List[OrderItemCreate]] = None
    is_urgent: Optional[bool] = Field(default=False, alias="isUrgent")
    notes: Optional[str] = None
    mileage: Optional[int] = None
    damages: Optional[List[str]] = None
    
    model_config = ConfigDict(populate_by_name=True)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class Order(OrderBase):
    id: str
    total: float
    items: List[OrderItem] = []
    created_at: datetime = Field(alias="createdAt")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class OrderResponse(Order):
    pass


class OrderDetailResponse(Order):
    """Extended order response with related data"""
    vehicle_obj: Optional[VehicleResponse] = None
    mechanic: Optional[EmployeeResponse] = None
    model_config = ConfigDict(from_attributes=True)


# ============== Dashboard Schemas ==============
class DashboardStats(BaseModel):
    revenue: float
    active_orders: int = Field(alias="activeOrders")
    pending_release: int = Field(alias="pendingRelease")
    total_orders: int = Field(alias="totalOrders")
    
    model_config = ConfigDict(populate_by_name=True)


class FinanceReport(BaseModel):
    revenue: float
    expenses: float
    profit: float
    completed_orders_count: int = Field(alias="completedOrdersCount")
    
    model_config = ConfigDict(populate_by_name=True)
