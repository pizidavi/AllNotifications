import os
import re
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import Updater, CallbackContext
from telegram.ext import Defaults, Filters
from telegram.ext import MessageHandler, CallbackQueryHandler

from utils.logger import get_logger
from storages.BaseStorage import DBStorage

logger = get_logger(__name__)


class View:

    def __init__(self, token: str = None):
        token = token if token is not None else os.getenv('TELEGRAM_TOKEN')
        self.__message_max_length = int(os.getenv('MESSAGE_MAX_LENGTH'))

        self.__dao = DBStorage(type_='admin')
        self.__commands = {
            'start': 'Start the bot',
        }

        self.__updater = Updater(token, defaults=Defaults(parse_mode=ParseMode.MARKDOWN_V2))
        self.__updater.dispatcher.add_handler(MessageHandler(Filters.chat_type, self.__handler))
        self.__updater.dispatcher.add_handler(CallbackQueryHandler(self.__handler))
        self.__updater.dispatcher.add_error_handler(self.__handler_error)

        self.__updater.start_polling()
        logger.debug('Telegram listener started')

    def __handler(self, update: Update, _: CallbackContext) -> None:
        telegram_user = update.effective_user
        user = self.__dao.get_user(telegram_id=telegram_user.id)
        if user is None:
            if update.message:
                update.message.reply_text('You are not authorized to use this bot.')
            return

        if update.message:
            message = update.message
            logger.info('Request from %s', telegram_user.id)

            message_text = message.text

            if message_text.startswith('/start'):
                text = f'Ciao {telegram_user.first_name} 👋'
                message.reply_text(text)
            elif message_text.startswith('/'):
                command, *arguments = re.split(r'[ |\n]', message_text.removeprefix('/'), 1)
                arguments = (''.join(arguments)).split('\n')

                if command not in self.__commands:
                    message.reply_text('Command not found')
                    return

                text = self.__commands[command](user['user_id'], arguments)
                if isinstance(text, bool):
                    text = 'The command was successfully executed' if text else 'An error occurred'

                ids_ = []
                while len(text) >= self.__message_max_length:
                    _text = text[:self.__message_max_length-1].rsplit('\n', 1)[0]
                    text = text[len(_text):]
                    message_posted = message.reply_text(_text, parse_mode=ParseMode.HTML)
                    ids_.append(str(message_posted.message_id))

                inline_keyboard = [[InlineKeyboardButton(text='❌', callback_data='delete|'+('-'.join(ids_)))]]
                message.reply_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard),
                                   parse_mode=ParseMode.HTML)
                message.delete()
            else:
                message.reply_text('Command not found')

        elif update.callback_query:
            query = update.callback_query
            logger.info('%s %s %s', 'callback_query', telegram_user.id, query.data)

            chat_id = query.message.chat_id
            action, *data = query.data.split('|', 1)
            data = (''.join(data)).split('-')

            if 'delete' == action:
                for _message_id in data:
                    _.bot.delete_message(chat_id=chat_id, message_id=_message_id)
                query.delete_message()
            else:
                query.answer('Command not found', show_alert=True)
            query.answer()

    @staticmethod
    def __handler_error(update, context: CallbackContext):
        logger.error('TelegramError: %s', context.error)

    def register_command(self, type_: str, command: str, func: callable):
        """
        Register command in View
        :param type_: Provider's TYPE
        :param command: Command name
        :param func: Function to be called
        """
        command = f'{command}_{type_}'
        if command not in self.__commands:
            self.__commands[command] = func
            self.__save_commands()

    def register_commands(self, type_: str, commands: list[tuple[str, callable]]) -> None:
        """
        Register more commands in View
        :param type_: Provider's TYPE
        :param commands: List of tuple(command name, function to be called)
        """
        found = False
        for command, func in commands:
            command = f'{command}_{type_}'
            if command not in self.__commands:
                self.__commands[command] = func
                found = True
        if found:
            self.__save_commands()

    def __save_commands(self):
        telegram_commands = [(k, v if not callable(v) else (v.__doc__ or '??').strip())
                             for k, v in self.__commands.items()]
        if len(telegram_commands) > 0:
            self.__updater.bot.set_my_commands(telegram_commands)

    def stop(self):
        self.__updater.stop()
