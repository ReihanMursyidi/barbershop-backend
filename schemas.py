from pydantic import BaseModel
from datetime import date, time
from typing import Optional

# --- SCHEMAS UNTUK SERVICES ---
class ServiceBase(BaseModel):
    name: str
    desc: Optional[str] = None
    price: float
    duration_blocks: float

class ServiceResponse(ServiceBase):
    id: int
    class Config:
        from_attributes = True

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    desc: Optional[str] = None
    price: Optional[float] = None
    duration_blocks: Optional[float] = None

# --- SCHEMAS UNTUK BARBERS ---
class BarberBase(BaseModel):
    name: str
    specialty: Optional[str] = None
    photo_url: Optional[str] = None

class BarberCreate(BarberBase):
    specialty: Optional[str] = ""
    photo_url: Optional[str] = ""

class BarberResponse(BarberBase):
    id: int
    class Config:
        from_attributes = True

class BarberUpdate(BaseModel):
    name: Optional[str] = None
    specialty: Optional[str] = None
    photo_url: Optional[str] = None

#  --- SCHEMAS UNTUK BOOKING ---
class BookingCreate(BaseModel):
    customer_name: str
    customer_phone: str
    barber_id: int
    service_id: int
    booking_date: date
    start_time: time

class BookingResponse(BaseModel):
    id: int
    message: str
    barber_id: int
    class Config:
        from_attributes = True

class CustomerBase(BaseModel):
    name: str
    phone: str

class BookingAdminResponse(BaseModel):
    id: int
    booking_date: date
    start_time: time
    end_time: time
    status: str
    customer: CustomerBase
    barber: BarberBase
    service: ServiceBase

    class Config:
        from_attributes = True

