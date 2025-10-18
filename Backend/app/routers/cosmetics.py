from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select
from app.database import engine
from app.models import Avatar, Badge, CosmeticItem, UserInventory
from app.schemas import (
    AvatarCreate, AvatarRead,
    BadgeCreate, BadgeRead,
    CosmeticItemCreate, CosmeticItemRead,
    PurchaseRequest, EquipRequest
)

router = APIRouter(prefix="/cosmetics", tags=["Cosmetics & Rewards"])

# ------------------------------------------------------------------
# 🎨 AVATAR ROUTES
# ------------------------------------------------------------------

@router.post("/avatar", response_model=AvatarRead, status_code=status.HTTP_201_CREATED)
def create_or_update_avatar(data: AvatarCreate):
    """Create or update a user's avatar."""
    with Session(engine) as session:
        existing = session.exec(select(Avatar).where(Avatar.user == data.user)).first()
        if existing:
            for field, value in data.dict().items():
                setattr(existing, field, value)
            session.add(existing)
            session.commit()
            session.refresh(existing)
            return existing

        new_avatar = Avatar(**data.dict())
        session.add(new_avatar)
        session.commit()
        session.refresh(new_avatar)
        return new_avatar


@router.get("/avatar/{username}", response_model=AvatarRead)
def get_avatar(username: str):
    """Retrieve avatar details for a specific user."""
    with Session(engine) as session:
        avatar = session.exec(select(Avatar).where(Avatar.user == username)).first()
        if not avatar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Avatar for user '{username}' not found."
            )
        return avatar


# ------------------------------------------------------------------
# 🏅 BADGE ROUTES
# ------------------------------------------------------------------

@router.post("/badge", response_model=BadgeRead, status_code=status.HTTP_201_CREATED)
def create_badge(data: BadgeCreate):
    """Create a new badge (admin use)."""
    with Session(engine) as session:
        badge = Badge(**data.dict())
        session.add(badge)
        session.commit()
        session.refresh(badge)
        return badge


@router.get("/badges", response_model=list[BadgeRead])
def list_badges():
    """List all available badges."""
    with Session(engine) as session:
        return session.exec(select(Badge)).all()


@router.get("/badges/unlockable/{xp}", response_model=list[BadgeRead])
def get_unlockable_badges(xp: int):
    """List all badges unlockable given the user's total XP."""
    with Session(engine) as session:
        return session.exec(select(Badge).where(Badge.xp_required <= xp)).all()


# ------------------------------------------------------------------
# 🛍️ COSMETIC SHOP ROUTES
# ------------------------------------------------------------------

@router.post("/shop/item", response_model=CosmeticItemRead, status_code=status.HTTP_201_CREATED)
def add_cosmetic_item(item: CosmeticItemCreate):
    """Add a new cosmetic item to the shop (admin use)."""
    with Session(engine) as session:
        new_item = CosmeticItem(**item.dict())
        session.add(new_item)
        session.commit()
        session.refresh(new_item)
        return new_item


@router.get("/shop", response_model=list[CosmeticItemRead])
def list_shop_items():
    """View all available cosmetics in the shop."""
    with Session(engine) as session:
        return session.exec(select(CosmeticItem)).all()


# ------------------------------------------------------------------
# 💰 PURCHASE & INVENTORY ROUTES
# ------------------------------------------------------------------

@router.post("/purchase", status_code=status.HTTP_200_OK)
def purchase_cosmetic(purchase: PurchaseRequest):
    """Purchase a cosmetic using coins."""
    with Session(engine) as session:
        item = session.exec(select(CosmeticItem).where(CosmeticItem.id == purchase.item_id)).first()
        if not item:
            raise HTTPException(status_code=404, detail="Cosmetic item not found.")

        avatar = session.exec(select(Avatar).where(Avatar.user == purchase.user)).first()
        if not avatar:
            raise HTTPException(status_code=404, detail="User avatar not found.")

        if avatar.coins < item.price:
            raise HTTPException(status_code=400, detail="Not enough coins to purchase item.")

        # Deduct coins and add item to inventory
        avatar.coins -= item.price
        session.add(avatar)

        owned = UserInventory(user=purchase.user, item_id=item.id)
        session.add(owned)
        session.commit()
        return {"message": f"Successfully purchased {item.name}!", "remaining_coins": avatar.coins}


@router.get("/inventory/{username}", response_model=list[CosmeticItemRead])
def get_user_inventory(username: str):
    """Retrieve all cosmetics owned by a user."""
    with Session(engine) as session:
        owned_items = (
            session.query(CosmeticItem)
            .join(UserInventory, UserInventory.item_id == CosmeticItem.id)
            .filter(UserInventory.user == username)
            .all()
        )
        return owned_items


# ------------------------------------------------------------------
# 🧥 EQUIP / UNEQUIP ROUTES
# ------------------------------------------------------------------

@router.post("/equip", status_code=status.HTTP_200_OK)
def equip_cosmetic(request: EquipRequest):
    """Equip a cosmetic to the user's avatar."""
    with Session(engine) as session:
        avatar = session.exec(select(Avatar).where(Avatar.user == request.user)).first()
        if not avatar:
            raise HTTPException(status_code=404, detail="Avatar not found.")

        owned = session.exec(
            select(UserInventory)
            .where(UserInventory.user == request.user, UserInventory.item_id == request.item_id)
        ).first()
        if not owned:
            raise HTTPException(status_code=400, detail="Item not owned by user.")

        item = session.exec(select(CosmeticItem).where(CosmeticItem.id == request.item_id)).first()
        avatar.equipped_item = item.name
        session.add(avatar)
        session.commit()
        return {"message": f"{item.name} equipped successfully!"}


@router.post("/unequip", status_code=status.HTTP_200_OK)
def unequip_cosmetic(username: str):
    """Unequip currently equipped cosmetic."""
    with Session(engine) as session:
        avatar = session.exec(select(Avatar).where(Avatar.user == username)).first()
        if not avatar:
            raise HTTPException(status_code=404, detail="Avatar not found.")

        avatar.equipped_item = None
        session.add(avatar)
        session.commit()
        return {"message": "Cosmetic unequipped successfully."}
