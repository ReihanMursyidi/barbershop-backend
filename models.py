from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Time, Text
from sqlalchemy.orm import relationship
from database import Base

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    
    booking = relationship("Booking", back_populates="customer")

class Barber(Base):
    __tablename__ = 'barbers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    specialty = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)

    booking = relationship("Booking", back_populates="barber")

class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    desc = Column(Text, nullable=True)
    price = Column(Float, nullable=False)

    # Blok waktu yang dihabiskan
    duration_blocks = Column(Float, nullable=False)

    booking = relationship("Booking", back_populates="service")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    barber_id = Column(Integer, ForeignKey("barbers.id"))
    service_id = Column(Integer, ForeignKey("services.id"))

    # Tanggal dan Waktu Booking
    booking_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    status = Column(String, default="Confirmed")

    # Relasi
    customer = relationship("Customer", back_populates="booking")
    barber = relationship("Barber", back_populates="booking")
    service = relationship("Service", back_populates="booking")