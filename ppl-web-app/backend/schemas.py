from typing import List, Optional
from pydantic import BaseModel

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- User Schemas ---
class UserBase(BaseModel):
    email: str
    full_name: str
    org_name: str
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    org_name: Optional[str] = None
    avatar_url: Optional[str] = None

class LoginRequest(BaseModel):
    email: str

class VerifyCodeRequest(BaseModel):
    email: str
    code: str

class User(UserBase):
    id: int
    is_active: bool
    is_subscribed: bool
    
    class Config:
        from_attributes = True

# --- Variable Schemas ---
class VariableBase(BaseModel):
    tag: str
    location: str
    excel_data: Optional[dict] = None
    hihi: Optional[float] = None
    high: Optional[float] = None
    objective: Optional[float] = None
    low: Optional[float] = None
    lolo: Optional[float] = None
    unit_subsection: List[str] = []
    forecast_type: Optional[str] = None
    key_words: List[str] = []
    forecast_variables: List[str] = []

class VariableCreate(VariableBase):
    pass

class Variable(VariableBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

# --- Model Schemas ---
class ModelConfig(BaseModel):
    name: str
    input_variables: List[str]
    output_variables: List[str]
    description: Optional[str] = None

class ModelResponse(BaseModel):
    message: str
    model_id: str

class ModelSummary(BaseModel):
    id: str
    name: str
    status: str
    accuracy: float

class ModelDetails(BaseModel):
    id: str
    name: str
    description: Optional[str]
    input_variables: List[str]
    output_variables: List[str]
    metrics: dict

class SubscriptionRequest(BaseModel):
    interval: str # "month" or "year"
