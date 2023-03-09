
import asyncio
import http
import json

import httpx


async def delete_message_task(delete_message, message_id, chat_id):
    await asyncio.sleep(28800)
    await delete_message(message_id=message_id, chat_id=chat_id)


def create_hate_message():
    hate_message = ''
    response = httpx.get(url='https://evilinsult.com/generate_insult.php?lang=ru&type=json')
    if response.status_code == http.HTTPStatus.OK:
        try:
            hate_message = response.json()['insult']
        except json.decoder.JSONDecodeError:
            hate_message = 'JSONDecodeError\nНе удалось получить ругательное сообщение.'

    return hate_message
