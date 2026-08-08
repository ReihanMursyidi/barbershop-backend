import os
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta, date, time
from collections import defaultdict
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

import models
import schemas
from database import engine, get_db
from pydantic import BaseModel

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Blackwood Barbershop API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Config Cloudinary
cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"), 
    api_key = os.getenv("CLOUDINARY_API_KEY"), 
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
    secure = True
)

@app.get("/")
def read_root():
    return {"message": "Sistem Backend Barbershop Berhasil Berjalan!"}

# Endpoint untuk mendapatkan semua Services
@app.get("/services", response_model=list[schemas.ServiceResponse])
def get_services(db: Session = Depends(get_db)):
    return db.query(models.Service).all()

# Endpoint untuk update Service
@app.put("/services/{service_id}", response_model=schemas.ServiceResponse)
def update_service(service_id: int, service_data: schemas.ServiceUpdate, db: Session = Depends(get_db)):
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Layanan tidak ditemukan")

    update_data = service_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(service, key, value)

    db.commit()
    db.refresh(service)

    return service

# Endpoint untuk mendapatkan semua Barbers
@app.get("/barbers", response_model=list[schemas.BarberResponse])
def get_barbers(db: Session = Depends(get_db)):
    return db.query(models.Barber).all()

# Endpoint untuk update Barber
@app.put("/barbers/{barber_id}", response_model=schemas.BarberResponse)
def update_barber(barber_id: int, barber_data: schemas.BarberUpdate, db: Session = Depends(get_db)):
    barber = db.query(models.Barber).filter(models.Barber.id == barber_id).first()
    if not barber:
        raise HTTPException(status_code=404, detail="Barber tidak ditemukan")

    update_data = barber_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(barber, key, value)

    db.commit()
    db.refresh(barber)

    return barber

# Endpoint untuk membuat booking
@app.post("/bookings", response_model=schemas.BookingResponse)
def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    service = db.query(models.Service).filter(models.Service.id == booking.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Layanan tidak ditemukan")

    start_dt = datetime.combine(datetime.today(), booking.start_time)
    duration_minutes = int(service.duration_blocks * 30)
    end_dt = start_dt + timedelta(minutes= duration_minutes)
    calculated_end_time = end_dt.time()

    selected_barber_id = booking.barber_id

    if selected_barber_id == 0:
        all_barbers = db.query(models.Barber).all()
        available_barber = None

        for barber in all_barbers:
            overlapping = db.query(models.Booking).filter(
                models.Booking.barber_id == barber.id,
                models.Booking.booking_date == booking.booking_date,
                models.Booking.start_time < calculated_end_time,
                models.Booking.end_time > booking.start_time
            ).first()

            if not overlapping:
                available_barber = barber
                break

        if not available_barber:
            raise HTTPException(status_code=400, detail="Maaf, tidak ada barber yang tersedia pada waktu yang dipilih.")

        selected_barber_id = available_barber.id
    
    else:
        overlapping_booking = db.query(models.Booking).filter(
            models.Booking.barber_id == selected_barber_id,
            models.Booking.booking_date == booking.booking_date,
            models.Booking.start_time < calculated_end_time,
            models.Booking.end_time > booking.start_time
        ).first()

        if overlapping_booking:
            raise HTTPException(
                status_code=400, 
                detail=f"Maaf, jadwal barber bentrok. Jadwal yang terisi: {overlapping_booking.start_time} - {overlapping_booking.end_time}"
            )

    customer = db.query(models.Customer).filter(models.Customer.phone == booking.customer_phone).first()
    if not customer:
        customer = models.Customer(name=booking.customer_name, phone=booking.customer_phone)
        db.add(customer)
        db.commit()
        db.refresh(customer)

    new_booking = models.Booking(
        customer_id=customer.id,
        barber_id=selected_barber_id,
        service_id=booking.service_id,
        booking_date=booking.booking_date,
        start_time=booking.start_time,
        end_time=calculated_end_time
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return {
        "id": new_booking.id, 
        "message": "Reservasi berhasil dibuat!",
        "barber_id": selected_barber_id
    }

# Endpoint slot waktu yang sudah terisi
@app.get("/bookings/booked-slots")
def get_booked_slots(barber_id: int, date_str: str, db: Session = Depends(get_db)):
    
    if barber_id == 0:
        total_barbers = db.query(models.Barber).count()
        bookings = db.query(models.Booking).filter(
            models.Booking.booking_date == date_str
        ).all()

        slot_counts = defaultdict(int)

        for b in bookings:
            current = datetime.combine(datetime.today(), b.start_time)
            end = datetime.combine(datetime.today(), b.end_time)

            while current < end:
                slot_counts[current.strftime("%H:%M")] += 1
                current += timedelta(minutes=30)

        occupied_slots = [slot for slot, count in slot_counts.items() if count >= total_barbers]
        return occupied_slots
    else:
        bookings = db.query(models.Booking).filter(
            models.Booking.barber_id == barber_id,
            models.Booking.booking_date == date_str
        ).all()

        occupied_slots = []

        for b in bookings:
            current = datetime.combine(datetime.today(), b.start_time)
            end = datetime.combine(datetime.today(), b.end_time)

            while current < end:
                occupied_slots.append(current.strftime("%H:%M"))
                current += timedelta(minutes=30)

        return occupied_slots

# ENDPOINT ADMIN
@app.get("/admin/bookings")
def get_admin_bookings(date: str, db: Session = Depends(get_db)):
    results = db.query(
        models.Booking,
        models.Customer,
        models.Barber,
        models.Service
    ).join(models.Customer, models.Booking.customer_id == models.Customer.id)\
    .join(models.Barber, models.Booking.barber_id == models.Barber.id)\
    .join(models.Service, models.Booking.service_id == models.Service.id)\
    .filter(models.Booking.booking_date == date)\
    .order_by(models.Booking.start_time).all()
    
    formatted_bookings = []

    for booking, customer, barber, service in results:
        star_str = booking.start_time.strftime("%H:%M")
        end_str = booking.end_time.strftime("%H:%M")

        formatted_bookings.append({
            "customer_name": customer.name,
            "customer_phone": customer.phone,
            "service_name": service.name,
            "barber_name": barber.name,
            "start_time": star_str,
            "end_time": end_str
        })
    
    return formatted_bookings

@app.get("/admin/bookings/history", response_model=list[schemas.BookingAdminResponse])
def get_all_booking_history(db: Session = Depends(get_db)):
    return db.query(models.Booking).order_by(
        desc(models.Booking.booking_date),
        desc(models.Booking.start_time)
    ).all()

@app.get("/admin/barbers")
def get_admin_barbers(db: Session = Depends(get_db)):
    barbers = db.query(models.Barber).all()
    return barbers

@app.post("/admin/barbers", response_model=schemas.BarberResponse)
def create_admin_barber(barber: schemas.BarberCreate, db: Session = Depends(get_db)):
    new_barber = models.Barber(
        name=barber.name,
        specialty=barber.specialty,
        photo_url=barber.photo_url
    )
    db.add(new_barber)
    db.commit()
    db.refresh(new_barber)
    return new_barber

@app.put("/admin/barbers/{barber_id}", response_model=schemas.BarberResponse)
def update_admin_barber(barber_id: int, barber_data: schemas.BarberUpdate, db: Session = Depends(get_db)):
    barber = db.query(models.Barber).filter(models.Barber.id == barber_id).first()
    if not barber:
        raise HTTPException(status_code=404, detail="Barber tidak ditemukan")

    if barber_data.name is not None:
        barber.name = barber_data.name
    if barber_data.specialty is not None:
        barber.specialty = barber_data.specialty
    if barber_data.photo_url is not None:
        barber.photo_url = barber_data.photo_url

    db.commit()
    db.refresh(barber)

    return barber

@app.delete("/admin/barbers/{barber_id}")
def delete_admin_barber(barber_id: int, db: Session = Depends(get_db)):
    barber_to_delete = db.query(models.Barber).filter(models.Barber.id == barber_id).first()
    if not barber_to_delete:
        raise HTTPException(status_code=404, detail="Barber tidak ditemukan")
    
    db.delete(barber_to_delete)
    db.commit()
    return {"message": "Barber berhasil dihapus"}

@app.get("/admin/services", response_model=list[schemas.ServiceResponse])
def get_admin_services(db: Session = Depends(get_db)):
    return db.query(models.Service).all()

@app.post("/admin/services", response_model=schemas.ServiceResponse)
def create_admin_service(service: schemas.ServiceBase, db: Session = Depends(get_db)):
    new_service = models.Service(
        name=service.name,
        desc=service.desc,
        price=service.price,
        duration_blocks=service.duration_blocks
    )
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service

@app.put("/admin/services/{service_id}", response_model=schemas.ServiceResponse)
def update_admin_service(service_id: int, service_data: schemas.ServiceUpdate, db: Session = Depends(get_db)):
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Layanan tidak ditemukan")
    
    # Update hanya data yang dikirimkan (karena bersifat Optional)
    if service_data.name is not None: service.name = service_data.name
    if service_data.desc is not None: service.desc = service_data.desc
    if service_data.price is not None: service.price = service_data.price
    if service_data.duration_blocks is not None: service.duration_blocks = service_data.duration_blocks
    
    db.commit()
    db.refresh(service)
    return service

@app.delete("/admin/services/{service_id}")
def delete_admin_service(service_id: int, db: Session = Depends(get_db)):
    service_to_delete = db.query(models.Service).filter(models.Service.id == service_id).first()
    if service_to_delete:
        db.delete(service_to_delete)
        db.commit()
        return {"message": "Layanan dihapus"}
    raise HTTPException(status_code=404, detail="Layanan tidak ditemukan")

# --- ENDPOINT PUBLIC: AMBIL LAYANAN UNTUK HALAMAN DEPAN ---
@app.get("/services", response_model=list[schemas.ServiceResponse])
def get_public_services(db: Session = Depends(get_db)):
    return db.query(models.Service).all()

@app.post("/admin/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        result = cloudinary.uploader.upload(
            file.file,
            folder="barbershop_gallery"
        )
        return {"url": result.get("secure_url")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengunggah foto: {str(e)}")