"""
Database initialization script
Creates initial admin user and sample data
"""
from app.database import SessionLocal, init_db
from app.models import User, UserRole, Client, Vehicle, Inventory
from app.auth import get_password_hash


def create_admin_user(db):
    """Create default admin user if not exists"""
    admin = db.query(User).filter(User.login == "admin").first()
    if not admin:
        admin = User(
            full_name="System Administrator",
            role=UserRole.admin,
            login="admin",
            password_hash=get_password_hash("admin123")
        )
        db.add(admin)
        db.commit()
        print("✓ Created admin user (login: admin, password: admin123)")
    else:
        print("✓ Admin user already exists")


def create_sample_data(db):
    """Create sample data for testing"""
    # Check if data already exists
    if db.query(Client).first():
        print("✓ Sample data already exists")
        return
    
    # Create sample mechanic
    mechanic = User(
        full_name="John Mechanic",
        role=UserRole.mechanic,
        login="mechanic1",
        password_hash=get_password_hash("mechanic123")
    )
    db.add(mechanic)
    
    # Create sample clients
    client1 = Client(name="Айдар Смагулов", phone="+77011234567")
    client2 = Client(name="Айгерім Нұрланова", phone="+77029876543")
    db.add_all([client1, client2])
    db.commit()
    
    # Create sample vehicles
    vehicle1 = Vehicle(
        client_id=client1.id,
        license_plate="A123BC01",
        vin="1HGBH41JXMN109186",
        brand="Toyota",
        model="Camry"
    )
    vehicle2 = Vehicle(
        client_id=client2.id,
        license_plate="B456DE02",
        vin="2HGFG12878H553617",
        brand="Honda",
        model="Accord"
    )
    db.add_all([vehicle1, vehicle2])
    
    # Create sample inventory items
    items = [
        Inventory(name="Моторное масло 5W-30", article="OIL-5W30-001", quantity=50, price=5000),
        Inventory(name="Масляный фильтр", article="FILTER-OIL-001", quantity=30, price=1500),
        Inventory(name="Воздушный фильтр", article="FILTER-AIR-001", quantity=25, price=2000),
        Inventory(name="Тормозные колодки", article="BRAKE-PAD-001", quantity=20, price=8000),
        Inventory(name="Свечи зажигания", article="SPARK-PLUG-001", quantity=40, price=1200),
    ]
    db.add_all(items)
    
    db.commit()
    print("✓ Created sample data (1 mechanic, 2 clients, 2 vehicles, 5 inventory items)")


def main():
    """Main initialization function"""
    print("Initializing database...")
    
    # Create tables
    init_db()
    print("✓ Database tables created")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Create admin user
        create_admin_user(db)
        
        # Create sample data
        create_sample_data(db)
        
        print("\n✓ Database initialization completed successfully!")
        print("\nDefault credentials:")
        print("  Admin - login: admin, password: admin123")
        print("  Mechanic - login: mechanic1, password: mechanic123")
        
    except Exception as e:
        print(f"\n✗ Error during initialization: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
