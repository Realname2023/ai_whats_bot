from langchain.tools import tool
from envs import (about_company, WEBHOOK_URL, b24rest_request, method_deal_add, method_contact_list, 
                        method_contact_update, method_contact_add, method_products_set)
from data_base.anotations import (GoodBase, OrderBase)
from data_base.orm_query import (select_all_categories, seleact_all_gases, select_gas_cylinders, 
                                select_all_cities, select_product, select_services, select_liquefied_gases, 
                                get_user)


@tool
async def get_company_info() -> str:
    """Получает информацию о компании которую ты будешь представлять"""
    return about_company


@tool
async def get_branches_company():
    """Получает информацию о филиалах, городах компании (адреса, графики работы).
    Цены на газы отличаются в зависимости от города, филиала.
    """
    cities = await select_all_cities()
    return '\n----------\n'.join(f"""ID города: {city.id}, название: {city.name}, 
                                описание: {city.description}""" for city in cities)


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
    цена вместе с доставкой: {item.delivery_price} тенге, условия доставки: {item.delivery_terms}, 
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


@tool(args_schema=OrderBase)
async def send_order(user_id: str, product_id: int, quantity: int, is_delivery: bool):
    """Отправляет заказ менеджеру.
        Args:
            user_id: str ID пользователя
            product_id: int ID товара для заказа
            quantity: int количество заказываемого товара
            is_delivery: bool нужно ли сделать доставку товара
    """
    user = await get_user(user_id=user_id)
    product = await select_product(good_id=product_id)
    if is_delivery is True and product.is_delivery is False:
        return F"Извините доставку {product.name} не осуществляем"
    elif is_delivery is True and product.is_delivery is True:
        price = product.delivery_price
    else:
        price = product.price
    tittle = user.full_name
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
    poses = [{"PRODUCT_NAME": product.name,
                "PRICE": float(price),
                "QUANTITY": quantity,
                "MEASURE_NAME": product.unit
                }]
    
    parametr_products_set = {
        "id": deal_id,
        "rows": poses}

    await b24rest_request(WEBHOOK_URL, method_products_set, parametr_products_set)

    return 'Заказ успешно отправлен менеджеру'


agent_tools = [get_company_info, get_branches_company, get_categories_of_goods,get_all_gases, 
                get_all_gas_cylinders, get_all_services, get_all_liquefied_gases,
                get_product_description, send_order]
