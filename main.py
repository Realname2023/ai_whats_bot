import aiohttp
import asyncio
import re
from envs import GREEN_API_URL, TOKEN
from ai_agent.graph import chat_chain_graph
from data_base.engine import create_db
from data_base.orm_query import add_user

pattern = r'https?://\S+\.(?:jpg|jpeg|png|gif|webp|bmp|svg)'

async def get_message():
    get_url = f'{GREEN_API_URL}/receiveNotification/{TOKEN}'
    del_url = f'{GREEN_API_URL}/deleteNotification/{TOKEN}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url=get_url) as response:
            api_answer = await response.json(encoding='utf-8')
            if api_answer is not None:
                message = None
                chat_id = None
                chat_name = None
                phone_number = None
                receipt_id = api_answer.get("receiptId")
                if receipt_id:
                    if api_answer["body"].get('typeWebhook') == 'incomingMessageReceived':
                        message = api_answer["body"]["messageData"]["textMessageData"]["textMessage"]
                        chat_id = api_answer["body"]["senderData"]["chatId"]
                        chat_name = api_answer["body"]["senderData"]["chatName"]
                        phone_number = chat_id.replace('@c.us', '')

                    id_del_url = f'{del_url}/{receipt_id}'
                    await session.delete(url=id_del_url)
                

                if message is None or chat_id is None:
                    return False
                else:
                    await add_user(user_id=chat_id, full_name=chat_name, phone_number=phone_number)
                    return chat_id, chat_name, message
            else:
                return False


async def send_message(chat_id: str, chat_name: str, message: str):
    answer = await chat_chain_graph(message, chat_id, chat_name)
    match = re.search(pattern, answer)
    if match:
        image_url = match.group(0)
        send_url = f'{GREEN_API_URL}/sendFileByUrl/{TOKEN}'
        payload = {
            "chatId": chat_id,
            "urlFile": image_url,
            "fileName": "photo.png",
            "caption": answer}
    else:
        send_url = f'{GREEN_API_URL}/sendMessage/{TOKEN}'
        payload = {
            "chatId": chat_id, 
            "message": answer
            }
        
    headers = {
    'Content-Type': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url=send_url, headers=headers, json=payload) as response:
            print(response.status)
    


async def main():
    await create_db()
    while True:
        data = await get_message()
        print(data)
        if data:
            chat_id, chat_name, message = data
            await send_message(chat_id, chat_name, message)


if __name__ == "__main__":
    asyncio.run(main())
