import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
import database, auth, models, crud, schemas

router = APIRouter(
    prefix="/payment",
    tags=["payment"]
)

# Env Vars
POLAR_ACCESS_TOKEN = os.getenv("POLAR_ACCESS_TOKEN", "")
POLAR_PRODUCT_ID_MONTHLY = os.getenv("POLAR_PRODUCT_ID_MONTHLY", "") 
POLAR_PRODUCT_ID_YEARLY = os.getenv("POLAR_PRODUCT_ID_YEARLY", "")
POLAR_WEBHOOK_SECRET = os.getenv("POLAR_WEBHOOK_SECRET", "")
FRONTEND_URL = "http://localhost:5173"

@router.post("/create-checkout-session")
async def create_checkout_session(request: schemas.SubscriptionRequest, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    product_id = POLAR_PRODUCT_ID_MONTHLY if request.interval == "month" else POLAR_PRODUCT_ID_YEARLY
    
    if not POLAR_ACCESS_TOKEN or not product_id:
        raise HTTPException(status_code=500, detail="Polar configuration missing (Token or Product ID)")

    async with httpx.AsyncClient() as client:
        try:
            # Create Checkout Link
            # Docs: POST https://api.polar.sh/v1/checkouts/
            response = await client.post(
                "https://api.polar.sh/v1/checkouts/custom", 
                headers={
                    "Authorization": f"Bearer {POLAR_ACCESS_TOKEN}",
                    "Content-Type": "application/json"
                },
                json={
                    "product_id": product_id,
                    "success_url": f"{FRONTEND_URL}/subscription?success=true",
                    "customer_email": current_user.email,
                }
            )
            
            # If standard endpoint fails, we might need to look at specific Polar endpoint structures.
            # But normally APIs follow this pattern.
            
            if response.status_code not in [200, 201]:
                print(f"Polar Error: {response.text}")
                raise HTTPException(status_code=400, detail="Failed to create checkout session with Polar")
                
            data = response.json()
            # Expecting 'url' in response for the user to redirect to.
            checkout_url = data.get("url")
            if not checkout_url:
                 raise HTTPException(status_code=500, detail="No checkout URL returned from Polar")
                 
            return {"url": checkout_url}

        except Exception as e:
            print(f"Payment Error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def webhook(request: Request, polar_webhook_signature: str = Header(None), db: Session = Depends(database.get_db)):
    payload = await request.body()
    # TODO: Verify Signature using POLAR_WEBHOOK_SECRET
    # Polar documentation would specify how. Typically HMAC-SHA256.
    
    try:
        event = await request.json()
        event_type = event.get("type")
        data = event.get("data", {})
        
        # Handle "subscription.created" or "checkout.session.completed"
        if event_type == "subscription.created" or event_type == "order.created":
            # Identify user. 
            # We need to link 'customer_id' or 'email'.
            customer_email = data.get("customer", {}).get("email")
            # Or metadata if we passed it.
            
            if customer_email:
                user = crud.get_user_by_email(db, customer_email)
                if user:
                    # Update Subscription
                    polar_sub_id = data.get("id")
                    polar_cust_id = data.get("customer_id")
                    crud.update_user_polar_subscription(db, user.id, True, polar_cust_id, polar_sub_id)
                    print(f"User {user.email} subscription activated via Polar.")
                    
        elif event_type == "subscription.canceled":
             # Handle cancellation
             pass

    except Exception as e:
        print(f"Webhook Error: {e}")
        # Don't fail the webhook? Or do?
        raise HTTPException(status_code=400, detail="Webhook processing failed")

    return {"status": "success"}
