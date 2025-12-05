
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def create_user():
    db = SessionLocal()
    try:
        email = "bmithran15@gmail.com"
        # Check if user exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"User {email} already exists")
            return

        user = User(
            email=email,
            password_hash=get_password_hash("password123"),
            role="merchant"
        )
        db.add(user)
        db.commit()
        print(f"Created user: {email} / password123")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_user()
