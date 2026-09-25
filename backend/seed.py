from app.database import SessionLocal
from app.models import User, Contact, Deal


def seed():
    db = SessionLocal()

    try:
        user = User(
            name="Rahma",
            email="rahma@example.com",
            password_hash="temporary-hash"
        )

        db.add(user)
        db.flush()

        contact1 = Contact(
            name="Alice Smith",
            email="alice@example.com",
            phone="+213555111222",
            company="Tech Solutions",
            notes="Interested in our premium plan",
            owner_id=user.id
        )

        contact2 = Contact(
            name="John Doe",
            email="john@example.com",
            phone="+213555333444",
            company="Digital Agency",
            notes="Follow up next week",
            owner_id=user.id
        )

        db.add_all([contact1, contact2])
        db.flush()

        deal1 = Deal(
            title="Tech Solutions Premium",
            value=5000,
            status="open",
            contact_id=contact1.id,
            owner_id=user.id
        )

        deal2 = Deal(
            title="Digital Agency Contract",
            value=8500,
            status="won",
            contact_id=contact2.id,
            owner_id=user.id
        )

        db.add_all([deal1, deal2])

        db.commit()

        print("Seed data created successfully!")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed()