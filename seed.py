from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()

    # Check if data already exists
    if db.query(models.Service).first():
         print("⚠️ Data sudah ada di database. Proses seeding dilewati.")
         db.close()
         return
    
    print("🚀 Memulai proses seeding data...")

    # Seed Services
    services_data = [
        models.Service(
            name="Premium Haircut",
            desc="Layanan utama. Termasuk konsultasi, double hair wash, potongan presisi, dan premium styling.", 
            price=75000, 
            duration_blocks=2.0
        ),
        models.Service(
            name="Gentlemen's Shave & Beard Trim",
            desc="Perawatan brewok & kumis dengan teknik hot towel dan straight razor.", 
            price=50000, 
            duration_blocks=2.0
        ),
        models.Service(
            name="Hair Coloring & Highlight", 
            desc="Layanan pewarnaan rambut profesional. Harga dasar untuk warna natural.", 
            price=150000, 
            duration_blocks=4.0
        ),
        models.Service(
            name="The Executive Package", 
            desc="Paket relaksasi komplit. Premium Haircut + Gentlemen's Shave + Black Mask + Ekstra Pijat.", 
            price=130000, 
            duration_blocks=3.0
        ),
        models.Service(
            name="Kids & Student Haircut", 
            desc="Khusus anak (<12 th) & pelajar. Ditangani oleh kapster yang sabar dan telaten.", 
            price=50000, 
            duration_blocks=2.0
        )
    ]

    # Seed Barbers
    barbers_data = [
        models.Barber(
            name="Bima", 
            specialty="Classic Cuts, Executive Contours, Hot Towel Shaves", 
            photo_url="https://images.unsplash.com/photo-1622286342621-4bd786c2447c?q=80&w=200&auto=format&fit=crop"
        ),
        models.Barber(
            name="Rio", 
            specialty="Hair Coloring, Modern Textures, Korean Styles", 
            photo_url="https://images.unsplash.com/photo-1599351431202-1e0f0137899a?q=80&w=200&auto=format&fit=crop"
        ),
        models.Barber(
            name="Dimas", 
            specialty="Skin Fades, Buzz Cuts, Kids Haircut", 
            photo_url="https://images.unsplash.com/photo-1585747860715-2ba37e788b70?q=80&w=200&auto=format&fit=crop"
        )
    ]

    # Add data to the session
    db.add_all(services_data)
    db.add_all(barbers_data)

    # Commit the session to save data to the database
    db.commit()

    print("✅ Proses seeding data selesai.")
    db.close()

if __name__ == "__main__":
    seed_data()