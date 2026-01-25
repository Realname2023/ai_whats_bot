from langchain.tools import tool
from envs import (about_company, WEBHOOK_URL, b24rest_request, method_deal_add, method_contact_list, 
                        method_contact_update, method_contact_add, method_products_set)
from data_base.anotations import (GoodBase, CartBase, CartAddBase, OrderBase)
from data_base.orm_query import (select_all_categories, seleact_all_gases, select_gas_cylinders, 
                                select_all_cities, select_product, select_services, select_liquefied_gases, 
                                add_cart, get_user, get_user_carts, delete_user_carts)


@tool
async def get_company_info() -> str:
    """Получает информацию о компании которую ты будешь представлять"""
    return about_company


@tool
async def get_branches_company():
    """Получает филиалы, города компании. Цены на газы отличаются в зависимости от города, филиала.
    """
    cities = await select_all_cities()
    return '\n----------\n'.join(f'ID города: {city.id}, название: {city.name}' for city in cities)


@tool
async def get_categories_of_goods() -> str:
    """Получает информацию о категориях товаров,
    то есть вообще какой продукцией занимается компания которую ты представляешь.
    Запоминай ID категории товара, если есть интерес к определенной категории товаров."""
    categories = await select_all_categories()
    info = [f'ID категории: {cat.id}, название: {cat.name}' for cat in categories]
    return '\n-------------------------------------\n'.join(info)


@tool
async def get_all_gases() -> str:
    """Получает информацию о газах. Цена за сам газ без баллона.
       Запоминай ID товара, если есть интерес к определенному товару.
    """
    items = await seleact_all_gases()
    return '\n-------------------------\n'.join(f"""Фото: {item.photo} ID товара: {item.id}, 
    название: {item.name}, единица измерения: {item.unit}, цена: {item.price} тенге, 
    цена доставки: {item.delivery_price} тенге, условия доставки: {item.delivery_terms}, 
    филиал: {item.branch.name}""" for item in items)


@tool
async def get_all_gas_cylinders() -> str:
    """Получает информацию о баллонах для газов. Баллоны пустые без газа.
        Цена за сами баллоны.
       Запоминай ID товара, если есть интерес к определенному товару.
    """
    items = await select_gas_cylinders()
    return '\n-------------------------\n'.join(f"""Фото: {item.photo} ID товара: {item.id}, 
    название: {item.name}, единица измерения: {item.unit}, цена: {item.price} тенге""" for item in items)


@tool
async def get_all_services() -> str:
    """Получает информацию об услугах компании.
       Запоминай ID товара, если есть интерес к определенной услуге.
    """
    items = await select_services()
    return '\n-------------------------\n'.join(f"""Фото: {item.photo} ID товара: {item.id}, 
    название: {item.name}, единица измерения: {item.unit}, цена: {item.price} тенге""" for item in items)


@tool
async def get_all_liquefied_gases() -> str:
    """Получает информацию о жидких газах.
       Запоминай ID товара, если есть интерес к определенному жидкому газу.
    """
    items = await select_liquefied_gases()
    return '\n-------------------------\n'.join(f"""Фото: {item.photo} ID товара: {item.id}, 
    название: {item.name}, единица измерения: {item.unit}, цена: {item.price} тенге""" for item in items)


@tool(args_schema=GoodBase)
async def get_product_description(product_id):
    """Получает описание и характеристики товара, которым заинтересовался клиент.
        Args:
            product_id: int ID товара, которым заинтересовался клиент.
    """
    product = await select_product(product_id)
    return f'{product.photo}\n{product.name}\n{product.description}'


@tool(args_schema=CartBase)
async def add_user_cart(user_id: str, product_id: int, quantity: int, is_delivery: bool):
    """Добавляет корзину пользователя, а также обновляет корзину если такой товар уже есть 
    в корзине пользователя
         Args:
            user_id: str ID пользователя
            product_id: int ID товара для заказа
            quantity: int количество заказываемого товара
            is_delivery: bool нужно ли сделать доставку товара
    """
    good = await select_product(good_id=product_id)
    if is_delivery is True and good.is_delivery is False:
        return F"Извините доставку {good.name} не осуществляем"
    elif is_delivery is True and good.is_delivery is True:
        total_price = quantity*(good.price + good.delivery_price)
    else:
        total_price = quantity*good.price
    cart_in = CartAddBase(
        user_id=user_id,
        product_id=product_id,
        quantity=quantity,
        total_price=total_price
    )

    await add_cart(cart_in=cart_in)
    return 'Товар успешно добавлен в корзину'


@tool(args_schema=OrderBase)
async def send_order(user_id: str):
    """Отправляет заказ менеджеру.
        Всю информацию о пользователе и его корзинах получает из базы данных,
        которые сформированы в процессе переписки с пользователе через его user_id
        Args:
            user_id: str ID пользователя
    """
    user = await get_user(user_id=user_id)
    tittle = user.full_name
    user_carts = await get_user_carts(user_id=user_id)
    client_phone = user.phone_number

    parametr_contact_list = {
		'filter': {"PHONE": client_phone},
		'select': ["ID", "NAME"]
	}

    contacts_b24 = await b24rest_request(WEBHOOK_URL, method_contact_list, parametr_contact_list)

    if contacts_b24.get('result') != [] and contacts_b24.get('result') is not None:

        contact_id = contacts_b24.get('result')[-1].get('ID')
        contact_name = contacts_b24.get('result')[-1].get('NAME')
        if contact_name == 'Без имени':
            parametr_contact_update = {
                "id": contact_id,
                "fields": {'NAME': tittle}
            }

            await b24rest_request(WEBHOOK_URL, method_contact_update, parametr_contact_update)
    else:
        parametr_contact_add = {"fields": {
                    "NAME": tittle,
                    "PHONE": [{'VALUE': client_phone, "VALUE_TYPE": "WORK"}]}}
        
        contact_b24 = await b24rest_request(WEBHOOK_URL, method_contact_add, parametr_contact_add)

        contact_id = str(contact_b24.get('result'))
        

    parametr_deal_add = {"fields": {
                    "TITLE": tittle,
                    "STAGE_ID": "NEW",
                    "CONTACT_ID": contact_id,
                    "ASSIGNED_BY_ID": '3429',
                    }}
    
    response = await b24rest_request(WEBHOOK_URL, method_deal_add, parametr_deal_add)

    deal_id = str(response.get('result'))
    poses = []

    if user_carts != []:
        for ret in user_carts:
            quantity = ret.quantity
            price = ret.product.price

            pos = {"PRODUCT_NAME": ret.product.name,
                "PRICE": float(price),
                "QUANTITY": quantity,
                "MEASURE_NAME": ret.product.unit
                }
            poses.append(pos)
    
    parametr_products_set = {
        "id": deal_id,
        "rows": poses}

    await b24rest_request(WEBHOOK_URL, method_products_set, parametr_products_set)
    await delete_user_carts(user_id=user_id)
    # return 'Заказ успешно отправлен менеджеру'


agent_tools = [get_company_info, get_branches_company, get_categories_of_goods,get_all_gases, 
                get_all_gas_cylinders, get_all_services, get_all_liquefied_gases,
                get_product_description, add_user_cart, send_order]

# @tool(args_schema=CategoryBase)
# async def get_goods_info_by_category(category_id: int) -> str:
#     """Получает информацию о товарах по ID категории.
#        Запоминай ID категории товара, если есть интерес к определенной категории товаров.
#        Args:
#             category_id: int ID категории
#             """
#     goods = await get_goods_by_category(category_id=category_id)

#     return '\n-------------------------------------\n'.join(f"""URL фото: {g.photo}, 
#             ID товара: {g.id}, название: {g.name}, описание: {g.description}, ед. изм: {g.unit}, 
#             цена: {g.price} тенге, цена доставки {g.delivery_price} тенге, есть ли доставка товара: 
#             {g.is_delivery}, условия доставки: {g.delivery_terms}, ID филиала (города): {g.city_id}"""
#             for g in goods)


# @tool(args_schema=CategoryCityBase)
# async def get_goods_by_category_city(category_id: int, city_id: int):
#     """Получает информацию о товарах по ID категории и по ID филиала (города).
#        Касается газов, так как цены на газы в разных городах (филиалах) отличаются.
#        Запоминай ID категории товара, если есть интерес к определенной категории товаров.
#        Также запоминай ID города где клиент хочет приобрести газ
#        Args:
#             category_id: int ID категории
#              city_id: int ID города (филиала)
#             """
#     goods = await select_goods_by_category_city(category_id, city_id)
#     return '\n-------------------------------------\n'.join(f"""URL фото: {g.photo}, 
#             ID товара: {g.id}, название: {g.name}, описание: {g.description}, ед. изм: {g.unit}, 
#             цена: {g.price} тенге, цена доставки {g.delivery_price} тенге, есть ли доставка товара: 
#             {g.is_delivery}, условия доставки: {g.delivery_terms}, ID филиала (города): {g.city_id}"""
#             for g in goods)


# @tool(args_schema=GoodBase)
# async def get_good_info_by_id(good_id: int) -> str:
#     """Получает информацию о товаре по ID товара
#        Args:
#             good_id: int ID товара 
#     """
#     good = await select_product(good_id=good_id)

#     return f"""URL фото: {good.photo}, ID товара: {good.id}, название: {good.name}, 
#             описание: {good.description}, ед. изм: {good.unit}, цена: {good.price} тенге, 
#             цена доставки {good.delivery_price} тенге, есть ли доставка товара: {good.is_delivery}, 
#             условия доставки: {good.delivery_terms}, ID филиала (города): {good.city_id}"""



    

# agent_tools = [get_company_info, get_branches_company, get_categories_of_goods, 
#                get_goods_info_by_category, get_goods_by_category_city, get_good_info_by_id, 
#                add_user_cart, send_order]

# @tool
# async def get_arenda_goods():
#     """Получает арендные товары. 
#     Запоминай ID аренды товара, если есть интерес к аренде определенного товара.
#     """
#     arenda_goods = await select_arenda_goods()
#     return '\n-------------\n'.join(f"""URL фото: {g.photo}, 
#             ID аренды товара: {g.id}, название: {g.name}, описание: {g.description}, ед. изм: {g.unit}, 
#             цена: {g.price} тенге, цена аренды при заключении договора {g.arenda_contract} тенге,
#             условия аренды: {g.arenda_terms}"""
#             for g in arenda_goods)


# @tool(args_schema=ArendaGoodBase)
# async def get_arenda_good_info_by_id(good_id: int) -> str:
#     """Получает информацию об аренде товаре по ID арендного товара
#        Args:
#             good_id: int ID товара аренды
#     """
#     good = await select_arenda_good(good_id=good_id)

#     return f"""URL фото: {good.photo}, ID аренды товара: {good.id}, название: {good.name}, 
#             описание: {good.description}, ед. изм: {good.unit}, цена: {good.price} тенге, 
#             цена аренды при заключении договора {good.arenda_contract} тенге,
#             условия аренды: {good.arenda_terms}"""
    


# @tool(args_schema=ArendaCartBase)
# async def arenda_cart_add(user_id: str, good_id: int, quantity: int, 
#                           arenda_time: int, is_contract: bool):
#     """Добавляет корзину аренды  пользователя, а также обновляет арендную 
#     корзину если такой товар уже есть в корзине аренды пользователя
#          Args:
#             user_id: str ID пользователя
#             good_id: int ID аренды товара для заказа
#             quantity: int количество заказываемого товара
#             arenda_time: int время аренды товара в месяцах 
#             is_contract: bool хочет ли клиент заключить договор аренды со скидкой
#     """
#     arenda_good = await select_arenda_good(good_id=good_id)
#     if is_contract:
#         total_price = quantity*arenda_time(arenda_good.price - arenda_good.arenda_contract)
#     else:
#         total_price = quantity*arenda_time*arenda_good.price

#     cart_in = ArendaCartAddBase(
#         user_id=user_id,
#         good_id=good_id,
#         quantity=quantity,
#         arenda_time=arenda_time,
#         total_price=total_price
#     )

#     await add_arenda_cart(cart_in=cart_in)
