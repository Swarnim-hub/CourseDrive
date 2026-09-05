"""
Seed script: Creates an admin user + default categories.
Run once: python seed_data.py
"""
import asyncio
from app.database import AsyncSessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.category import Category
from app.core.security import get_password_hash
from sqlalchemy import select


CATEGORIES = [
    {"name": "Web Development", "icon": "Code"},
    {"name": "Data Science & AI", "icon": "BrainCircuit"},
    {"name": "Business", "icon": "Briefcase"},
    {"name": "Design & UX", "icon": "Palette"},
    {"name": "Marketing", "icon": "TrendingUp"},
    {"name": "Cybersecurity", "icon": "Shield"},
    {"name": "Mobile Development", "icon": "Smartphone"},
    {"name": "Cloud & DevOps", "icon": "Cloud"},
]


def slugify(text: str) -> str:
    import re
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Seed admin user
        admin_email = "admin@coursedrive.com"
        existing = await db.scalar(select(User).where(User.email == admin_email))
        if not existing:
            admin = User(
                email=admin_email,
                hashed_password=get_password_hash("admin123"),
                full_name="CourseDrive Admin",
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True,
            )
            db.add(admin)
            print(f"[CREATED] Admin: {admin_email} / admin123")
        else:
            print(f"[EXISTS] Admin: {admin_email}")

        # Seed categories
        for cat_data in CATEGORIES:
            slug = slugify(cat_data["name"])
            existing_cat = await db.scalar(select(Category).where(Category.slug == slug))
            if not existing_cat:
                cat = Category(
                    name=cat_data["name"],
                    slug=slug,
                    icon=cat_data["icon"],
                    description=f"Courses related to {cat_data['name']}",
                )
                db.add(cat)
                print(f"[CREATED] Category: {cat_data['name']}")
            else:
                print(f"[EXISTS] Category: {cat_data['name']}")

        await db.commit()
        print("\n[DONE] Seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed())
