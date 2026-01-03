from sqlalchemy.orm import Session
import models, schemas, auth

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        email=user.email, 
        full_name=user.full_name,
        org_name=user.org_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_polar_subscription(db: Session, user_id: int, is_subscribed: bool, polar_customer_id: str = None, polar_subscription_id: str = None):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.is_subscribed = is_subscribed
        if polar_customer_id:
            db_user.polar_customer_id = polar_customer_id
        if polar_subscription_id:
            db_user.polar_subscription_id = polar_subscription_id
        db.commit()
        db.refresh(db_user)
    return db_user

def create_verification_code(db: Session, email: str, code: str, expires_at):
    db_code = models.VerificationCode(email=email, code=code, expires_at=expires_at)
    db.add(db_code)
    db.commit()
    db.refresh(db_code)
    return db_code

def get_verification_code(db: Session, email: str, code: str):
    return db.query(models.VerificationCode).filter(
        models.VerificationCode.email == email,
        models.VerificationCode.code == code
    ).first()

def delete_verification_codes(db: Session, email: str):
    db.query(models.VerificationCode).filter(models.VerificationCode.email == email).delete()
    db.commit()

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        update_data = user_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def get_variables(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Variable).offset(skip).limit(limit).all()

def create_variable(db: Session, variable: schemas.VariableCreate, user_id: int):
    db_variable = models.Variable(**variable.dict(), owner_id=user_id)
    db.add(db_variable)
    db.commit()
    db.refresh(db_variable)
    return db_variable
