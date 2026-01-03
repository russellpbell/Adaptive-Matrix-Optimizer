from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import database, auth, models, schemas

router = APIRouter(
    prefix="/models",
    tags=["models"],
    responses={404: {"description": "Not found"}},
)

@router.post("/train", response_model=schemas.ModelResponse) # Assuming ModelResponse schema needs to be created or we use a generic dict for now
def train_model(
    model_config: schemas.ModelConfig, # To be defined
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Trigger model training.
    """
    # Placeholder for training logic trigger
    return {"message": "Training started", "model_id": "mock_model_123"}

@router.get("/", response_model=List[schemas.ModelSummary]) # To be defined
def list_models(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    List all available models.
    """
    # Placeholder return
    return [
        {"id": "model_1", "name": "Model Alpha", "status": "Ready", "accuracy": 0.95},
        {"id": "model_2", "name": "Model Beta", "status": "Training", "accuracy": 0.0}
    ]

@router.get("/{model_id}", response_model=schemas.ModelDetails) # To be defined
def get_model_details(
    model_id: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Get details for a specific model.
    """
    return {
        "id": model_id,
        "name": "Model Alpha",
        "description": "Prediction model for Reactor 1",
        "input_variables": ["XMEAS(1)", "XMEAS(2)"],
        "output_variables": ["XMEAS(10)"],
        "metrics": {"mse": 0.023, "loss": 0.015}
    }

@router.get("/{model_id}/visualizations")
def get_model_visualizations(
    model_id: str,
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Get data or paths for visualizations.
    """
    return {
        "error_dist": "/static/visualizations/error_dist.png",
        "lime_plot": "/static/visualizations/lime_violin.png"
    }
