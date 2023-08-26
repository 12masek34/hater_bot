
import asyncio
import http
import json
import os
import subprocess
from pathlib import (
    Path,
)
from typing import Callable

import httpx
import speech_recognition as sr


recognizer = sr.Recognizer()


async def delete_message_task(delete_message: Callable, message_id: int, chat_id: int) -> None:
    await asyncio.sleep(28800)
    await delete_message(message_id=message_id, chat_id=chat_id)


def create_hate_message() -> str:
    hate_message = ''
    response = httpx.get(url='https://evilinsult.com/generate_insult.php?lang=ru&type=json')
    if response.status_code == http.HTTPStatus.OK:
        try:
            hate_message = response.json()['insult']
        except json.decoder.JSONDecodeError:
            hate_message = 'JSONDecodeError\nНе удалось получить ругательное сообщение.'

    return hate_message


def voice_recognizer(file_name: str, language: str = 'ru_RU') -> str:
    name = Path(file_name).stem
    subprocess.run(['ffmpeg', '-i', file_name, f'{name}.wav', '-y'])
    file = sr.AudioFile(f'{name}.wav')

    with file as source:
        try:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio, language=language)
        except Exception as err:
            text = 'Это невозможно преобразовать в текст.'

    os.remove(file_name)
    os.remove(f'{name}.wav')

    return text
