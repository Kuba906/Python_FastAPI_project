from sqlalchemy.orm import Session
from . import models
import schemas
from sqlalchemy import update, func


def get_suppliers(db: Session):
    return db.query(models.Supplier)\
        .order_by(models.Supplier.SupplierID)\
            .all()

def get_supplier(db: Session, supplier_id: int):
    return(db.query(models.Supplier)
        .filter(models.Supplier.SupplierID == supplier_id)
        .first())

def get_supplier_products(db: Session, supplier_id:int):
    return db.query(models.Product)\
        .join(models.Category).filter(models.Product.SupplierID == supplier_id)\
            .order_by(models.Product.ProductID.desc()).all()


def create_supplier(db: Session, new_supplier: schemas.NewSupplier):
    id = db.query(func.max(models.Supplier.SupplierID)).scalar()
    new_supplier.SupplierID = id + 1
    db.add(models.Supplier(**new_supplier.dict()))
    db.commit()
    return get_supplier(db, id + 1)

def update_supplier(db: Session, id: int, supplier_update: schemas.UpdateSupplier):
    supplier_dict = {key: el for key, el in supplier_update.dict().items() if el is not None}
    update = update(models.Supplier).where(models.Supplier.SupplierID == id).values(**supplier_dict)
    db.execute(update)
    db.commit()
    return get_supplier(db, id)

def delete_supplier(db: Session, id: int):
    data = db.query(models.Supplier)\
        .filter(models.Supplier.SupplierID == id).one()
    db.delete(data)
    db.commit()
