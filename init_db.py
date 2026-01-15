"""
Database initialization script
Creates initial admin user and sample data
"""
from app.database import SessionLocal, init_db
from app.models import User, Client, Vehicle, Inventory, Service, ClientType, EmployeeStatus
from app.auth import get_password_hash


def create_admin_user(db):
    """Create default admin user if not exists"""
    admin = db.query(User).filter(User.login == "admin").first()
    if not admin:
        # WARNING: Default password is for development only!
        # In production, change this immediately or require password change on first login
        admin = User(
            name="System Administrator",
            role="admin",
            phone="+77012345678",
            status=EmployeeStatus.active,
            login="admin",
            password_hash=get_password_hash("admin123")
        )
        db.add(admin)
        db.commit()
        print("✓ Created admin user (login: admin, password: admin123)")
        print("  ⚠️  WARNING: Change the default password in production!")
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
        name="John Mechanic",
        role="mechanic",
        phone="+77019876543",
        status=EmployeeStatus.active,
        login="mechanic1",
        password_hash=get_password_hash("mechanic123")
    )
    db.add(mechanic)
    
    # Create sample clients
    client1 = Client(
        name="Айдар Смагулов", 
        phone="+77011234567",
        email="aidar@example.com",
        type=ClientType.private
    )
    client2 = Client(
        name="Айгерім Нұрланова", 
        phone="+77029876543",
        email="aigerim@example.com",
        type=ClientType.private
    )
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
        Inventory(name="Моторное масло 5W-30", sku="OIL-5W30-001", quantity=50, price=5000, location="A1-01"),
        Inventory(name="Масляный фильтр", sku="FILTER-OIL-001", quantity=30, price=1500, location="A1-02"),
        Inventory(name="Воздушный фильтр", sku="FILTER-AIR-001", quantity=25, price=2000, location="A1-03"),
        Inventory(name="Тормозные колодки", sku="BRAKE-PAD-001", quantity=20, price=8000, location="B2-01"),
        Inventory(name="Свечи зажигания", sku="SPARK-PLUG-001", quantity=40, price=1200, location="A2-01"),
    ]
    db.add_all(items)
    
    # Create sample services
    services = [
        Service(name="Замена масла", price=3000, duration=0.5),
        Service(name="Диагностика двигателя", price=5000, duration=1.0),
        Service(name="Замена тормозных колодок", price=8000, duration=2.0),
        Service(name="Развал-схождение", price=4000, duration=1.5),
        Service(name="Замена свечей зажигания", price=2000, duration=0.75),
    ]
    db.add_all(services)
    
    db.commit()
    print("✓ Created sample data (1 mechanic, 2 clients, 2 vehicles, 5 inventory items, 5 services)")


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
