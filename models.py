from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Customer:
    id: Optional[int]
    name: str
    phone: str
    address: str

@dataclass
class OrderItem:
    id: Optional[int]
    order_id: Optional[int]
    product_name: str
    quantity: int
    price: float

@dataclass
class Order:
    id: Optional[int]
    customer_id: int
    order_date: str
    status: str
    total: float
    items: List[OrderItem] = field(default_factory=list) 
