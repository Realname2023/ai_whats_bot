from typing import List
from sqlalchemy import DateTime, ForeignKey, String, Text, BigInteger, Boolean, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    __abstract__ = True
    
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(150), nullable=True)
    full_name: Mapped[str] = mapped_column(String(500), nullable=True)

    def __str__(self):
        return self.full_name


class Branch(Base):
    __tablename__ = 'branches'

    name: Mapped[str] = mapped_column(String(500), nullable=False)
    verbose_name: Mapped[str] = mapped_column(String(500), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    products: Mapped[List['Product']] = relationship(back_populates="branch", lazy="selectin")

    def __str__(self):
        return self.name


class Category(Base):
    __tablename__ = 'categories'

    photo: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    verbose_name: Mapped[str] = mapped_column(String(500), nullable=True)

    products: Mapped[List['Product']] = relationship(back_populates="category", lazy="selectin")

    def __str__(self):
        return self.name
    
class Product(Base):
    __tablename__ = 'products'

    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id', ondelete='CASCADE'))
    branch_id: Mapped[int] = mapped_column(ForeignKey('branches.id', ondelete='CASCADE'))
    photo: Mapped[str] = mapped_column(Text, nullable=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    verbose_name: Mapped[str] = mapped_column(String(500), nullable=True)
    unit: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_delivery: Mapped[bool] = mapped_column(Boolean, default=False)
    price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    delivery_price: Mapped[int] = mapped_column(BigInteger, nullable=True)
    delivery_terms: Mapped[str] = mapped_column(Text, nullable=True)
    b_id: Mapped[str] = mapped_column(String(50))

    branch: Mapped['Branch'] = relationship(back_populates="products", lazy="selectin")
    category: Mapped['Category'] = relationship(back_populates="products", lazy="selectin")

    def __str__(self):
        return self.name


class Cart(Base):
    __tablename__ = 'carts'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    quantity: Mapped[int] = mapped_column(BigInteger)
    total_price: Mapped[int] = mapped_column(BigInteger)
    
    user: Mapped['User'] = relationship(backref='carts', lazy="selectin")
    product: Mapped['Product'] = relationship(backref='carts', lazy="selectin")

    def __str__(self) -> str:
        return self.user.full_name
