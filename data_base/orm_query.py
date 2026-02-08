from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload
from data_base.engine import session_maker
from data_base.models import Product, User, Category, Cart, Branch


async def add_user(user_id: str, full_name: str | None = None,
    phone_number: str | None = None):
    async with session_maker() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        if result.first() is None:
            session.add(
                User(user_id=user_id, phone_number=phone_number, full_name=full_name)
            )
            await session.commit()


async def get_user(user_id: str):
    async with session_maker() as session:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        return result.scalar()


async def select_all_categories():
    async with session_maker() as session:
        query = select(Category)
        result = await session.execute(query)
        return result.scalars().all()


async def select_all_cities():
    async with session_maker() as session:
        query = select(Branch).order_by(Branch.id)
        result = await session.execute(query)
        return result.scalars().all()


async def seleact_all_gases():
    async with session_maker() as session:
        query = select(Product).options(joinedload(Product.branch)).where(Product.category_id == 1).order_by(Product.id)
        result = await session.execute(query)
        return result.scalars().all()


async def select_gas_cylinders():
    async with session_maker() as session:
        query = select(Product).where(Product.category_id == 2).order_by(Product.id)
        result = await session.execute(query)
        return result.scalars().all()


async def select_services():
    async with session_maker() as session:
        query = select(Product).where(Product.category_id == 3).order_by(Product.id)
        result = await session.execute(query)
        return result.scalars().all()


async def select_liquefied_gases():
    async with session_maker() as session:
        query = select(Product).where(Product.category_id == 4).order_by(Product.id)
        result = await session.execute(query)
        return result.scalars().all()


async def select_product(good_id: int):
    async with session_maker() as session:
        query = select(Product).options(joinedload(Product.branch)).where(Product.id == good_id)
        result = await session.execute(query)
        return result.scalar_one()
