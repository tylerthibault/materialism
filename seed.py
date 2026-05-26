import os
os.makedirs('instance', exist_ok=True)

from app import create_app
from app.extensions import db
from app.models.user import User, UserRole
from app.models.project import Project, ProjectStatus
from app.models.material_list import MaterialList
from app.models.material_item import MaterialItem, UnitType
from app.models.store import StoreSource, StoreType
from app.models.price_result import PriceResult, AvailabilityStatus
from datetime import datetime

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()

    admin = User(email='admin@buildbid.com', name='Tyler Admin', company_name='BuildBid', role=UserRole.ADMIN)
    admin.set_password('password123')
    demo = User(email='demo@buildbid.com', name='Demo Contractor', company_name='Demo Construction LLC', role=UserRole.USER)
    demo.set_password('password123')
    db.session.add_all([admin, demo])
    db.session.flush()

    stores = [
        StoreSource(name='Home Depot', store_type=StoreType.HOME_DEPOT, website_url='https://www.homedepot.com', is_active=True, supports_scraping=True),
        StoreSource(name="Lowe's", store_type=StoreType.LOWES, website_url='https://www.lowes.com', is_active=True, supports_scraping=True),
        StoreSource(name='Local Lumber Co.', store_type=StoreType.LOCAL, website_url='', is_active=True, supports_scraping=False),
        StoreSource(name='Facebook Marketplace', store_type=StoreType.FACEBOOK, website_url='https://www.facebook.com/marketplace', is_active=True, supports_scraping=True),
    ]
    db.session.add_all(stores)
    db.session.flush()
    hd, lowes, local, fb = stores

    p1 = Project(user_id=demo.id, name='Smith Residence Remodel', client_name='John Smith', location='Seattle, WA', description='Full interior remodel', status=ProjectStatus.ACTIVE)
    db.session.add(p1)
    db.session.flush()

    framing = MaterialList(project_id=p1.id, name='Framing')
    drywall_list = MaterialList(project_id=p1.id, name='Drywall')
    db.session.add_all([framing, drywall_list])
    db.session.flush()

    framing_items = [
        MaterialItem(list_id=framing.id, name='2x4x8 Stud', quantity=100, unit=UnitType.EACH, sort_order=1),
        MaterialItem(list_id=framing.id, name='OSB Sheathing 4x8', quantity=50, unit=UnitType.SHEET, sort_order=2),
        MaterialItem(list_id=framing.id, name='LVL Beam 3.5x9.5x20', quantity=4, unit=UnitType.EACH, sort_order=3),
    ]
    drywall_items = [
        MaterialItem(list_id=drywall_list.id, name='1/2 inch Drywall 4x8', quantity=80, unit=UnitType.SHEET, sort_order=1),
        MaterialItem(list_id=drywall_list.id, name='Joint Compound 4.5 Gal', quantity=10, unit=UnitType.EACH, sort_order=2),
        MaterialItem(list_id=drywall_list.id, name='Metal Corner Bead 8ft', quantity=30, unit=UnitType.EACH, sort_order=3),
    ]
    db.session.add_all(framing_items + drywall_items)
    db.session.flush()

    price_data = {
        framing_items[0].id: {hd.id: 4.98, lowes.id: 5.12, local.id: 4.75, fb.id: 3.50},
        framing_items[1].id: {hd.id: 28.45, lowes.id: 27.99, local.id: 30.00},
        framing_items[2].id: {hd.id: 189.00, lowes.id: 195.00, local.id: 175.00},
        drywall_items[0].id: {hd.id: 13.48, lowes.id: 12.99, local.id: 14.00, fb.id: 9.50},
        drywall_items[1].id: {hd.id: 8.97, lowes.id: 9.48, local.id: 10.00},
        drywall_items[2].id: {hd.id: 1.28, lowes.id: 1.35, local.id: 1.50},
    }
    for item_id, store_prices in price_data.items():
        item = MaterialItem.query.get(item_id)
        for store_id, price in store_prices.items():
            pr = PriceResult(item_id=item_id, store_id=store_id,
                price_per_unit=price, total_price=price * item.quantity,
                product_name=item.name, availability=AvailabilityStatus.IN_STOCK,
                fetched_at=datetime.utcnow(), is_manual=False)
            db.session.add(pr)

    p2 = Project(user_id=demo.id, name='Johnson Commercial Addition', client_name='Mike Johnson', location='Tacoma, WA', description='500 sqft commercial addition', status=ProjectStatus.ACTIVE)
    db.session.add(p2)
    db.session.flush()

    concrete_list = MaterialList(project_id=p2.id, name='Concrete Work')
    roofing_list = MaterialList(project_id=p2.id, name='Roofing')
    db.session.add_all([concrete_list, roofing_list])
    db.session.flush()

    concrete_items = [
        MaterialItem(list_id=concrete_list.id, name='80lb Concrete Mix Bag', quantity=40, unit=UnitType.BAG, sort_order=1),
        MaterialItem(list_id=concrete_list.id, name='Rebar #4 20ft', quantity=20, unit=UnitType.EACH, sort_order=2),
        MaterialItem(list_id=concrete_list.id, name='Wire Mesh 5x150', quantity=2, unit=UnitType.EACH, sort_order=3),
    ]
    roofing_items = [
        MaterialItem(list_id=roofing_list.id, name='Architectural Shingles sq', quantity=12, unit=UnitType.EACH, sort_order=1),
        MaterialItem(list_id=roofing_list.id, name='Synthetic Underlayment 10sq', quantity=2, unit=UnitType.EACH, sort_order=2),
        MaterialItem(list_id=roofing_list.id, name='Drip Edge 10ft', quantity=30, unit=UnitType.EACH, sort_order=3),
    ]
    db.session.add_all(concrete_items + roofing_items)
    db.session.flush()

    price_data2 = {
        concrete_items[0].id: {hd.id: 7.98, lowes.id: 7.64, local.id: 8.50},
        concrete_items[1].id: {hd.id: 11.48, lowes.id: 10.98, local.id: 12.00, fb.id: 7.00},
        concrete_items[2].id: {hd.id: 34.98, lowes.id: 33.48, local.id: 36.00},
        roofing_items[0].id: {hd.id: 98.00, lowes.id: 95.00, local.id: 102.00},
        roofing_items[1].id: {hd.id: 72.00, lowes.id: 68.50, local.id: 75.00},
        roofing_items[2].id: {hd.id: 4.28, lowes.id: 3.98, local.id: 4.75},
    }
    for item_id, store_prices in price_data2.items():
        item = MaterialItem.query.get(item_id)
        for store_id, price in store_prices.items():
            pr = PriceResult(item_id=item_id, store_id=store_id,
                price_per_unit=price, total_price=price * item.quantity,
                product_name=item.name, availability=AvailabilityStatus.IN_STOCK,
                fetched_at=datetime.utcnow(), is_manual=False)
            db.session.add(pr)

    db.session.commit()
    print("Seed complete!")
    print("Login credentials:")
    print("  demo@buildbid.com  / password123")
    print("  admin@buildbid.com / password123")
