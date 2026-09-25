from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.deal import Deal
from app.models.contact import Contact
from app.models.user import User
from app.schemas.deal import DealCreate, DealResponse
from app.security import get_current_user


router = APIRouter(
    prefix="/deals",
    tags=["Deals"]
)


@router.post("/", response_model=DealResponse)
def create_deal(
    deal: DealCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contact = db.query(Contact).filter(
        Contact.id == deal.contact_id,
        Contact.owner_id == current_user.id
    ).first()

    if contact is None:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )

    new_deal = Deal(
        title=deal.title,
        value=deal.value,
        status=deal.status,
        contact_id=deal.contact_id,
        owner_id=current_user.id
    )

    db.add(new_deal)
    db.commit()
    db.refresh(new_deal)

    return new_deal



@router.get("/{deal_id}", response_model=DealResponse)
def get_deal(
    deal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deal = db.query(Deal).filter(
        Deal.id == deal_id,
        Deal.owner_id == current_user.id
    ).first()

    if deal is None:
        raise HTTPException(
            status_code=404,
            detail="Deal not found"
        )

    return deal


@router.put("/{deal_id}", response_model=DealResponse)
def update_deal(
    deal_id: int,
    deal: DealCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_deal = db.query(Deal).filter(
        Deal.id == deal_id,
        Deal.owner_id == current_user.id
    ).first()

    if existing_deal is None:
        raise HTTPException(
            status_code=404,
            detail="Deal not found"
        )

    contact = db.query(Contact).filter(
        Contact.id == deal.contact_id,
        Contact.owner_id == current_user.id
    ).first()

    if contact is None:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )

    existing_deal.title = deal.title
    existing_deal.value = deal.value
    existing_deal.status = deal.status
    existing_deal.contact_id = deal.contact_id

    db.commit()
    db.refresh(existing_deal)

    return existing_deal


@router.delete("/{deal_id}")
def delete_deal(
    deal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deal = db.query(Deal).filter(
        Deal.id == deal_id,
        Deal.owner_id == current_user.id
    ).first()

    if deal is None:
        raise HTTPException(
            status_code=404,
            detail="Deal not found"
        )

    db.delete(deal)
    db.commit()

    return {
        "message": "Deal deleted successfully"
    }


@router.get("/", response_model=list[DealResponse])
def get_deals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Deal).filter(
        Deal.owner_id == current_user.id
    ).all()