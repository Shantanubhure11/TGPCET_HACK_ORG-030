"""
Sample Data Loader.
Populates warehouses, suppliers, items, initial inventory levels, and
generates 1 year of realistic synthetic sales orders for ML model training.
"""
import sys
import os
import random
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

# Insert workspace root to system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from erp_backend.database import SessionLocal, get_db_context
from erp_backend.models.warehouse import Warehouse
from erp_backend.models.supplier import Supplier
from erp_backend.models.item import Item
from erp_backend.models.inventory import Inventory
from erp_backend.models.sales_order import SalesOrder
from erp_backend.models.inventory_ledger import InventoryLedger

# Seed randomness for reproducibility
random.seed(42)

def generate_suppliers(db: Session):
    """Inserts 5 representative suppliers."""
    suppliers = [
        Supplier(
            supplier_id="SUP-001",
            name="Alpha Logistics & Mfg",
            contact_email="orders@alphalog.com",
            avg_lead_time=2.0,
            lead_time_std=0.3,
            reliability_pct=98.0,
            moq=50,
            capacity=5000
        ),
        Supplier(
            supplier_id="SUP-002",
            name="Bharat Components",
            contact_email="sales@bharatcomp.in",
            avg_lead_time=4.0,
            lead_time_std=0.8,
            reliability_pct=92.0,
            moq=100,
            capacity=10000
        ),
        Supplier(
            supplier_id="SUP-003",
            name="Apex Global Traders",
            contact_email="import@apextraders.com",
            avg_lead_time=7.0,
            lead_time_std=1.5,
            reliability_pct=85.0,
            moq=500,
            capacity=15000
        ),
        Supplier(
            supplier_id="SUP-004",
            name="Rapid Supply Co.",
            contact_email="rapid@supplyco.com",
            avg_lead_time=1.5,
            lead_time_std=0.2,
            reliability_pct=99.0,
            moq=25,
            capacity=2500
        ),
        Supplier(
            supplier_id="SUP-005",
            name="Continental Parts Corp",
            contact_email="orders@contiparts.com",
            avg_lead_time=5.0,
            lead_time_std=1.0,
            reliability_pct=90.0,
            moq=200,
            capacity=8000
        )
    ]
    for s in suppliers:
        # Check if already exists
        existing = db.query(Supplier).filter(Supplier.supplier_id == s.supplier_id).first()
        if not existing:
            db.add(s)
    db.commit()
    print(f"Loaded {len(suppliers)} Suppliers.")

def generate_warehouses(db: Session):
    """Inserts 2 warehouses."""
    warehouses = [
        Warehouse(
            warehouse_id="WH-01",
            name="Main Nagpur Central DC",
            location="Nagpur, Maharashtra",
            capacity=100000
        ),
        Warehouse(
            warehouse_id="WH-02",
            name="Secondary Mumbai Regional Hub",
            location="Mumbai, Maharashtra",
            capacity=40000
        )
    ]
    for w in warehouses:
        existing = db.query(Warehouse).filter(Warehouse.warehouse_id == w.warehouse_id).first()
        if not existing:
            db.add(w)
    db.commit()
    print(f"Loaded {len(warehouses)} Warehouses.")

def generate_items(db: Session):
    """Inserts 10 representative SKU items (categories: Electronics, Packaging, Spares)."""
    items = [
        Item(sku_id="SKU-9902", name="Precision micro-controller IC", category="Electronics", unit="pcs", unit_cost=15.00, selling_price=30.00, supplier_id="SUP-001", moq=100),
        Item(sku_id="SKU-1234", name="OLED Display Panel 5.5 inch", category="Electronics", unit="pcs", unit_cost=45.00, selling_price=90.00, supplier_id="SUP-003", moq=50),
        Item(sku_id="SKU-4567", name="Reinforced Cardboard Box 12x12x12", category="Packaging", unit="pcs", unit_cost=1.20, selling_price=3.50, supplier_id="SUP-002", moq=500),
        Item(sku_id="SKU-8890", name="Heavy Duty Hydraulic Pump", category="Spares", unit="pcs", unit_cost=120.00, selling_price=250.00, supplier_id="SUP-005", moq=10),
        Item(sku_id="SKU-2345", name="Polymer Protective Foam Wrap", category="Packaging", unit="rolls", unit_cost=8.50, selling_price=18.00, supplier_id="SUP-002", moq=50),
        Item(sku_id="SKU-3456", name="Rechargeable Li-Ion Battery 3.7V", category="Electronics", unit="pcs", unit_cost=5.50, selling_price=12.00, supplier_id="SUP-001", moq=200),
        Item(sku_id="SKU-5678", name="Stainless Steel M6 Screws Group", category="Spares", unit="boxes", unit_cost=3.00, selling_price=7.00, supplier_id="SUP-004", moq=100),
        Item(sku_id="SKU-6789", name="Thermal Interface Paste 10g", category="Electronics", unit="tubes", unit_cost=2.00, selling_price=5.50, supplier_id="SUP-004", moq=50),
        Item(sku_id="SKU-7890", name="High-Temp Heat Shrink Tube", category="Packaging", unit="meters", unit_cost=0.50, selling_price=1.80, supplier_id="SUP-002", moq=1000),
        Item(sku_id="SKU-9012", name="Rubber Sealing O-Ring Pack", category="Spares", unit="packs", unit_cost=4.00, selling_price=9.50, supplier_id="SUP-005", moq=50)
    ]
    for i in items:
        existing = db.query(Item).filter(Item.sku_id == i.sku_id).first()
        if not existing:
            db.add(i)
    db.commit()
    print(f"Loaded {len(items)} Items.")

def initialize_inventory(db: Session):
    """Initializes inventory quantities and logs initial ledger balance."""
    items = db.query(Item).all()
    warehouses = db.query(Warehouse).all()
    
    loaded_count = 0
    for w in warehouses:
        for i in items:
            existing = db.query(Inventory).filter(
                Inventory.sku_id == i.sku_id,
                Inventory.warehouse_id == w.warehouse_id
            ).first()
            
            if not existing:
                # Random starting stock
                initial_stock = float(random.randint(200, 800)) if w.warehouse_id == "WH-01" else float(random.randint(50, 200))
                allocated = float(random.randint(10, 40))
                
                inv = Inventory(
                    sku_id=i.sku_id,
                    warehouse_id=w.warehouse_id,
                    physical_stock=initial_stock,
                    allocated_stock=allocated,
                    incoming_stock=0.0,
                    safety_stock=float(i.moq * 0.3),
                    rop=float(i.moq * 0.7),
                    last_counted_at=datetime.utcnow()
                )
                db.add(inv)
                db.flush()
                
                # Ledger entry
                ledger = InventoryLedger(
                    sku_id=i.sku_id,
                    warehouse_id=w.warehouse_id,
                    transaction_type="INITIAL",
                    qty_change=initial_stock,
                    previous_balance=0.0,
                    new_balance=initial_stock,
                    timestamp=datetime.utcnow() - timedelta(days=365),
                    notes="System Initialization Stock"
                )
                db.add(ledger)
                loaded_count += 1
                
    db.commit()
    print(f"Initialized {loaded_count} Inventory stock points.")

def generate_sales_history(db: Session):
    """
    Generates 1 year of daily SalesOrders for training.
    """
    # Check if we already have sales history
    cnt = db.query(SalesOrder).count()
    if cnt > 100:
        print("Sales history already populated. Skipping sales generation.")
        return

    items = db.query(Item).all()
    warehouses = db.query(Warehouse).all()
    
    start_date = datetime.now() - timedelta(days=365)
    end_date = datetime.now()
    
    total_sales = 0
    
    # Process SKU by SKU
    for item in items:
        # Define baseline average demand per day for this item
        base_demand = random.choice([8, 12, 20, 25])
        
        current_date = start_date
        while current_date <= end_date:
            day_of_week = current_date.weekday()
            
            # Weekend seasonality (Saturday/Sunday higher demand)
            weekend_multiplier = 1.35 if day_of_week >= 5 else 0.90
            
            # Monthly seasonality (Slight holiday lift in Oct/Nov/Dec)
            month = current_date.month
            monthly_multiplier = 1.25 if month in [10, 11, 12] else 1.0
            
            # Promotions
            promo = random.random() < 0.05  # 5% chance of promo
            promo_multiplier = 2.0 if promo else 1.0
            discount = float(random.choice([10.0, 15.0, 20.0])) if promo else 0.0
            
            # Generate target sales quantity using Poisson/Gamma shape distribution
            raw_qty = base_demand * weekend_multiplier * monthly_multiplier * promo_multiplier
            sales_qty = random.randint(int(raw_qty * 0.7), int(raw_qty * 1.3))
            
            # Distribute among warehouses
            wh_shares = {"WH-01": int(sales_qty * 0.8), "WH-02": int(sales_qty * 0.2)}
            
            for wh_id, qty in wh_shares.items():
                if qty > 0:
                    so = SalesOrder(
                        sku_id=item.sku_id,
                        warehouse_id=wh_id,
                        order_qty=float(qty),
                        unit_price=item.selling_price,
                        discount_pct=discount,
                        promotion_flag=promo,
                        stock_available_at_sale=float(qty + random.randint(10, 100)),
                        order_date=current_date
                    )
                    db.add(so)
                    total_sales += 1
            
            # Commit batches
            if total_sales % 1000 == 0:
                db.commit()
                
            current_date += timedelta(days=1)
            
    db.commit()
    print(f"Generated {total_sales} daily Sales order logs across 1 year.")

def main():
    print("Populating database with realistic synthetic data...")
    with get_db_context() as db:
        generate_suppliers(db)
        generate_warehouses(db)
        generate_items(db)
        initialize_inventory(db)
        generate_sales_history(db)
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    main()
