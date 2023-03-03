
import asyncio
import http

import httpx


async def delete_message_task(delete_message, message_id, chat_id):
    await asyncio.sleep(300)
    await delete_message(message_id=message_id, chat_id=chat_id)


def create_hate_message():
    hate_message = ''
    response = httpx.get(url='https://evilinsult.com/generate_insult.php?lang=ru&type=json')
    if response.status_code == http.HTTPStatus.OK:
        hate_message = response.json()['insult']

    return hate_message
