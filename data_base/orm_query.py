from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload
from data_base.engine import session_maker
from data_base.models import Product, User, Category, Cart, Branch
from data_base.anotations import CartAddBase


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


async def add_cart(cart_in: CartAddBase):
    async with session_maker() as session:
        cart = Cart(**cart_in.model_dump())
        query = select(Cart).where(Cart.user_id == cart.user_id, 
                                   Cart.product_id == cart.product_id)
        result = await session.execute(query)
        user_cart = result.scalar()
        if user_cart:
            for name, value in cart_in.model_dump(exclude_unset=True).items():
                setattr(user_cart, name, value)
        else:
            user_cart = cart
            session.add(user_cart)
        
        await session.commit()
        return user_cart


async def get_user_carts(user_id: str):
    async with session_maker() as session:
        query = select(Cart).where(Cart.user_id == user_id)
        result = await session.execute(query)
        return result.scalars().all()


async def select_cart(user_id: int, good_id):
    async with session_maker() as session:
        query = select(Cart).where(Cart.user_id == user_id, Cart.product_id == good_id)
        result = await session.execute(query)
        return result.scalar()


async def delete_user_cart(user_id: str, good_id: int):
    async with session_maker() as session:
        query = delete(Cart).where(Cart.user_id == user_id, Cart.product_id == good_id)
        await session.execute(query)
        await session.commit()


async def delete_user_carts(user_id: str):
    async with session_maker() as session:
        query = delete(Cart).where(Cart.user_id == user_id)
        await session.execute(query)
        await session.commit()


# async def get_goods_by_category(category_id: int):
#     async with session_maker() as session:
#         query = select(Product).where(Product.category_id == category_id).order_by(Product.id)
#         result = await session.execute(query)
#         return result.scalars().all()


# async def select_goods_by_category_city(category_id: int, city_id: int):
#     async with session_maker() as session:
#         query = select(Product).options(joinedload(Product.branch)).where(Product.category_id == category_id,
#                                    Product.branch_id == city_id).order_by(Product.id)
#         result = await session.execute(query)
#         return result.scalars().all()


# async def get_user_arenda_carts(user_id: str):
#     async with session_maker() as session:
#         query = select(ArendaCart).where(ArendaCart.user_id == user_id)
#         result = await session.execute(query)
#         return result.scalars().all()


# async def select_arenda_cart(user_id: int, good_id: int):
#     async with session_maker() as session:
#         query = select(ArendaCart).where(ArendaCart.user_id == user_id, 
#                                          ArendaCart.good_id == good_id)
#         result = await session.execute(query)
#         return result.scalar()

# async def delete_user_arenda_cart(user_id: str, good_id: int):
#     async with session_maker() as session:
#         query = delete(ArendaCart).where(ArendaCart.user_id == user_id, 
#                                          ArendaCart.good_id == good_id)
#         await session.execute(query)
#         await session.commit()
# async def add_arenda_cart(cart_in: ArendaCartAddBase):
#     async with session_maker() as session:
#         cart = ArendaCart(**cart_in.model_dump())
#         query = select(ArendaCart).where(ArendaCart.user_id == cart.user_id, 
#                                    ArendaCart.good_id == cart.good_id)
#         result = await session.execute(query)
#         user_cart = result.scalar()
#         if user_cart:
#             for name, value in cart_in.model_dump(exclude_unset=True).items():
#                 setattr(user_cart, name, value)
#         else:
#             user_cart = cart
#             session.add(user_cart)
        
#         await session.commit()
#         return user_cart

# async def select_arenda_good(good_id: int):
#     async with session_maker() as session:
#         query = select(ArendaGood).options(joinedload(ArendaGood.city)).where(ArendaGood.id == good_id)
#         result = await session.execute(query)
#         return result.scalar()


# async def select_arenda_goods():
#     async with session_maker() as session:
#         query = select(ArendaGood).order_by(ArendaGood.id)
#         result = await session.execute(query)
#         return result.scalars().all()


# async def delete_user_arenda_carts(user_id: str):
#     async with session_maker() as session:
#         query = delete(ArendaCart).where(ArendaCart.user_id == user_id)
#         await session.execute(query)
#         await session.commit()

# async def update_cart(cart_in: CartAddSerializer):
#     async with session_maker() as session:
#         cart = Cart(**cart_in.model_dump())
#         query = update(Cart).where(Cart.user_id == cart.user_id, 
#                                    Cart.good_id == cart.good_id).values(
#                                        {Cart.quantity: cart.quantity,
#                                         Cart.arenda_time: cart.arenda_time,
#                                         Cart.is_delivery: cart.is_delivery,
#                                         Cart.is_contract: cart.is_contract,
#                                         Cart.total_price: cart.total_price}
#                                    ).returning(Cart)
#         result = await session.execute(query)
#         user_cart = result.scalar()
#         await session.commit() 
#         return user_cart

# async def select_carts_purch_arenda(user_id: int):
#     async with session_maker() as session:
#         query1 = select(Cart).options(joinedload(Cart.good)).where(Cart.user_id==user_id,
#                                                                   Cart.is_arenda == False)
#         query2 = select(Cart).options(joinedload(Cart.good)).where(Cart.user_id==user_id,
#                                                                   Cart.is_arenda == True)
#         result1 = await session.execute(query1)
#         result2 = await session.execute(query2)
#         goods = result1.scalars().all()
#         arenda_goods = result2.scalars().all()
#         return {'goods': goods, 'arenda_goods': arenda_goods}

# async def delete_message(session_id: str):
#     async with session_maker() as session:
#         query_ids = select(MessageStore.id).where(MessageStore.session_id == session_id).order_by(MessageStore.id)
#         all_message_ids = (await session.scalars(query_ids)).all()
#         count_messages = len(all_message_ids)
#         if count_messages > 10:
#             num_to_delete = count_messages - 10
#             ids_to_delete = all_message_ids[:num_to_delete]
#             stmt = delete(MessageStore).where(MessageStore.id.in_(ids_to_delete))
#             await session.execute(stmt)
#             await session.commit()



# async def get_good_by_id(good_id: int):
#     async with session_maker() as session:
#         query = select(Good).where(Good.id == good_id)
#         result = await session.execute(query)
#         return result.scalar()


# async def get_all_goods():
#     async with session_maker() as session:
#         query = select(Good)
#         result = await session.execute(query)
#         return result.scalars().all()
