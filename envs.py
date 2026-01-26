import aiohttp
from os import getenv
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# DATABASE_URL = str(getenv('DB_URL'))
DATABASE_URL = f"postgresql+asyncpg://{getenv('POSTGRES_USER')}:{getenv('POSTGRES_PASSWORD')}@db:5432/{getenv('POSTGRES_DB')}"
GREEN_API_URL = str(getenv('GREEN_URL'))
TOKEN = str(getenv('TOKEN'))
WEBHOOK_URL = str(getenv('URL_WEBHOOK'))

about_company = None


with open('company.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()
    about_company = ''.join(lines)


method_deal_add = 'crm.deal.add'
method_contact_update = 'crm.contact.update'
method_products_set = 'crm.deal.productrows.set'
method_contact_list = 'crm.contact.list'
method_contact_add = 'crm.contact.add'
method_list_deals = 'crm.deal.list'


async def b24rest_request(url_webhook: str, method: str, parametr: dict) -> dict:
    url = url_webhook + method + '.json?'
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=parametr) as response:
            response_data = await response.json()
            if response.status == 200:
                # Запрос выполнен успешно
                print(f"Ответ сервера: {response_data}")
            else:
                print(f"Ошибка при выполнении запроса. Статус код: {response_data}") 
    return response_data
