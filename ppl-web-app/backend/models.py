from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, JSON, DateTime
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)
    full_name = Column(String)
    org_name = Column(String)
    avatar_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    polar_customer_id = Column(String, nullable=True)
    polar_subscription_id = Column(String, nullable=True)
    is_subscribed = Column(Boolean, default=False)

    variables = relationship("Variable", back_populates="owner")

class VerificationCode(Base):
    __tablename__ = "verification_codes"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    code = Column(String)
    expires_at = Column(DateTime)


class Variable(Base):
    __tablename__ = "variables"

    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String, index=True)
    location = Column(String)
    excel_data = Column(JSON, nullable=True) # Stores filePath, cellLocation
    
    # Bounds
    hihi = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    objective = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    lolo = Column(Float, nullable=True)
    
    unit_subsection = Column(JSON, nullable=True) # List of strings
    forecast_type = Column(String, nullable=True)
    key_words = Column(JSON, nullable=True) # List of strings
    forecast_variables = Column(JSON, nullable=True) # List of strings

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="variables")
