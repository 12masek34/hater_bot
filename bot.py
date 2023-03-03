
import asyncio
import logging
import os
import re
from random import choice
from time import sleep

from dotenv import load_dotenv
from telegram import (
    ForceReply,
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
)

load_dotenv(os.getcwd() + '/.ENV')
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)
TOKEN = os.getenv('TOKEN')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""

    user = update.effective_user
    await update.message.reply_html(
        rf'Привет {user.mention_html()}!',
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""

    await update.message.reply_text(
        'hater_bot v0.2\n\n'
        'Возможности.\n'
        '1. Если в вашем сообщении содержится хотя бы одна ссылка, вы получите от меня оскорбление.\n\n'
        '2. Я реализую примитивную копию утилиты sed (потоковый редактор). Пример: отправьте s/regexp/new_value '
        'на сообщение которое хотите отредактировать.',
    )


async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    await update.message.reply_text(
        '1. Сообщения бота удаляются автоматически через 5 минут.\n'
        '2. Оскорбления генеррируются в стороннем сервисе.'
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


def main() -> None:
    """Start the bot."""

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('new', new_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hate_link))
    application.add_handler(MessageHandler(~filters.COMMAND, hate_forward))
    application.run_polling()


if __name__ == '__main__':
    main()