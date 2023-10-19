
import asyncio
import io
import logging
import os
import re
from random import (
    choice,
)
from time import (
    sleep,
)

from dotenv import (
    load_dotenv,
)
from telegram import (
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from helpers import (
    create_hate_message,
    delete_message_task,
    voice_recognizer,
)

load_dotenv(os.getcwd() + '/.ENV')
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)
TOKEN = os.getenv('TOKEN')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""

    await update.message.reply_text(
        'hater_bot v0.3\n\n'
        'Возможности.\n'
        '1. Если в вашем сообщении содержится хотя бы одна ссылка, вы получите от меня оскорбление.\n\n'
        '2. Я реализую примитивную копию утилиты sed (потоковый редактор). Пример: отправьте s/regexp/new_value '
        'на сообщение которое хотите отредактировать.\n\n'
        '3. Преобразую голосовые сообщения в текс.',
    )


async def hate_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    message_id = update.message.message_id if update.message is not None else None
    chat_id = update.message.chat_id if update.message is not None else None
    forward_message = update.message.forward_from_chat if update.message is not None else None
    URL_PATTERN = r'[A-Za-z0-9]+://[A-Za-z0-9%-_]+(/[A-Za-z0-9%-_])*(#|\\?)[A-Za-z0-9%-_&=]*'
    link = re.match(URL_PATTERN, update.message.text)
    hate_message = create_hate_message()

    if link is not None:
        await asyncio.sleep(choice(range(1,6)))
        msg = await context.bot.send_message(
            chat_id=chat_id,
            reply_to_message_id=message_id,
            text=hate_message,
        )
        loop = asyncio.get_event_loop()
        loop.create_task(delete_message_task(context.bot.deleteMessage, msg.message_id, msg.chat_id))


    elif forward_message is not None:
        sleep(choice(range(1,6)))
        msg = await context.bot.send_message(
            chat_id=chat_id,
            reply_to_message_id=message_id,
            text=hate_message,
        )
        loop = asyncio.get_event_loop()
        loop.create_task(delete_message_task(context.bot.deleteMessage, msg.message_id, msg.chat_id))

    elif update.message.text.startswith('s/'):
        pattern = update.message.text.split('/')
        message = update.message.reply_to_message
        if message is not None:
            new_text = re.sub(rf'{pattern[1]}', rf'{pattern[2]}', message.text)
            await context.bot.send_message(
                chat_id=chat_id,
                reply_to_message_id=update.message.reply_to_message.id,
                text=new_text,
            )


async def hate_forward(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    forward_message = update.message.forward_from_chat if update.message is not None else None
    message_id = update.message.message_id if update.message is not None else None
    chat_id = update.message.chat_id if update.message is not None else None

    if forward_message is not None:
        hate_message = create_hate_message()
        sleep(choice(range(1,6)))
        msg = await context.bot.send_message(
            chat_id=chat_id,
            reply_to_message_id=message_id,
            text=hate_message,
        )
        loop = asyncio.get_event_loop()
        loop.create_task(delete_message_task(context.bot.deleteMessage, msg.message_id, msg.chat_id))


async def speach_to_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    file_name = 'audio.ogg'

    with io.BytesIO() as f:
        file = await context.bot.get_file(update.message.voice.file_id)

        if int(file.file_size) >= 715000:
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                reply_to_message_id=update.message.message_id,
                text='Файл большеват для перевода в текст.',
            )
            return

        await file.download_to_memory(out=f)
        file_data = f.getvalue()

    with open(file_name, 'wb') as file:
        file.write(file_data)

    text = voice_recognizer(file_name)
    msg = await context.bot.send_message(
        chat_id=update.message.chat_id,
        reply_to_message_id=update.message.message_id,
        text=text,
    )
    loop = asyncio.get_event_loop()
    loop.create_task(delete_message_task(context.bot.deleteMessage, msg.message_id, msg.chat_id))


def main() -> None:
    """Start the bot."""

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(MessageHandler(filters.VOICE, speach_to_text))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hate_link))
    application.add_handler(MessageHandler(~filters.COMMAND, hate_forward))
    application.run_polling()


if __name__ == '__main__':
    main()
# AAA