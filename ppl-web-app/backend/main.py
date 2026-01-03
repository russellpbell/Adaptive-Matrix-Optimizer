from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
import shutil
import os

import crud, models, schemas, database, auth
from routers import models as models_router
from routers import payment

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="PPL Web App API")

app.include_router(models_router.router)
app.include_router(payment.router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS (Allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173"), "http://localhost:5173", "http://localhost:4173"], # Allow configured frontend, plus local defaults
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Auth Endpoints ---
from datetime import datetime, timedelta

# --- Auth Endpoints ---
@app.post("/auth/request-code")
async def request_code(request: schemas.LoginRequest, db: Session = Depends(database.get_db)):
    user = crud.get_user_by_email(db, email=request.email)
    if not user:
        # Auto-register user
        new_user = schemas.UserCreate(email=request.email, full_name="New User", org_name="Default Org")
        user = crud.create_user(db, new_user)
    
    # Generate Code
    code = auth.generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    # Save to DB
    crud.delete_verification_codes(db, request.email) # Clean old codes
    crud.create_verification_code(db, request.email, code, expires_at)
    
    # "Send" Email (Print to console)
    print(f"\n[MAGIC LINK] Login Code for {request.email}: {code}\n")
    
    return {"message": "Verification code sent"}

@app.post("/auth/verify-code", response_model=schemas.Token)
async def verify_code(request: schemas.VerifyCodeRequest, db: Session = Depends(database.get_db)):
    # Check code
    db_code = crud.get_verification_code(db, request.email, request.code)
    if not db_code:
        raise HTTPException(status_code=400, detail="Invalid code")
        
    if db_code.expires_at < datetime.utcnow():
        crud.delete_verification_codes(db, request.email)
        raise HTTPException(status_code=400, detail="Code expired")
        
    # Code valid, consume it
    crud.delete_verification_codes(db, request.email)
    
    # Get user
    user = crud.get_user_by_email(db, email=request.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # issue token
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.put("/users/me", response_model=schemas.User)
async def update_user_me(
    user_update: schemas.UserUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.update_user(db=db, user_id=current_user.id, user_update=user_update)

@app.post("/users/me/avatar", response_model=schemas.User)
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Create directory if it doesn't exist (safety check)
    os.makedirs("static/avatars", exist_ok=True)
    
    # Save file
    file_location = f"static/avatars/{current_user.id}_{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    
    # Update user avatar_url
    base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    avatar_url = f"{base_url}/{file_location}"
    
    user_update = schemas.UserUpdate(avatar_url=avatar_url)
    return crud.update_user(db=db, user_id=current_user.id, user_update=user_update)

# --- Variable Endpoints ---
@app.post("/variables/", response_model=schemas.Variable)
def create_variable(
    variable: schemas.VariableCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.create_variable(db=db, variable=variable, user_id=current_user.id)

@app.get("/variables/", response_model=List[schemas.Variable])
def read_variables(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.get_variables(db, skip=skip, limit=limit)

# --- Prediction Endpoints ---
# --- Prediction Endpoints ---
import prediction

@app.get("/model/variables")
def get_model_variables():
    """List variables available in the trained model."""
    return prediction.get_available_variables()

@app.get("/variables/{variable_name}/prediction")
def get_variable_prediction(variable_name: str):
    """Get prediction for a specific variable (random sample)."""
    # Note: variable_name should match the column name in CSV, e.g. "XMEAS(1)"
    # URL encoding might be needed for names with parenthesis
    data = prediction.predict_sample(variable_name)
    if not data:
        raise HTTPException(status_code=404, detail=f"Variable {variable_name} not found in model outputs")
    return data
