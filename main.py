from enum import Enum
import logging
import os
from typing import Iterable, Union

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
from telegram.helpers import escape_markdown


from data_handling import DataHandler, FileHandler
from messages import MessagesEN, MessagesRU

load_dotenv() 
    
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class BotCaller:

    # TODO: new class Menu that constructs iterables of button names
    init_menu = ['Alarm', 'Dictionary', 'Get Definition']
    
    alarm_menu = ['View Alarms', 'Change Alarm', 'Back']
    choose_alarm_menu = ['Alarm 1', 'Alarm 2', 'Alarm 3', 'Alarm 4', 'Back']
    change_alarm_menu = ['Set Alarm', 'Delete Alarm', 'Back']

    choose_dict_menu = ['Dict 1', 'Dict 2', 'Dict 3', 'Dict 4', 'Back']
    dict_menu = ['Add Words', 'Delete', 'Back']
    delete_dict_menu = ['Delete One Word', 'Delete All Word']
    add_words_menu = ['Back']
    lang_menu = ['English', 'Русский']

    menus = [
        'INIT', 
        'ALARM', 'CHOOSE_ALARM', 'CHANGE_ALARM', 'CHOOSE_ALARM_DICT', 'PROCESS_SETTING_ALARM',
        'DICTIONARY', 'CHOOSE_DICTIONARY', 'DELETE_DICTIONARY', 'ADD_WORDS_DICTIONARY',
        'PROCESSING_DEFINITION', 'DELETING_WORD'
        ]
    States = Enum('States', menus) 

    def __init__(self, data_handler: DataHandler, token: str):
        self.data_handler = data_handler
        self.token = token
        self.Messages = MessagesEN()
          

    @staticmethod
    def buttons_to_calls_list(l: Iterable) -> Iterable:
        return [BotCaller.button_to_call(i) for i in l]        

    @staticmethod
    def button_to_call(button_name: str) -> str:
        return button_name.replace(" ", "_").upper()

    @staticmethod
    async def send_message( 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE,
        message: str = "",
        markup: Union[ReplyKeyboardMarkup, ReplyKeyboardRemove] = None
        ):
            await update.message.reply_text(
            text=escape_markdown(message, version=2),
            reply_markup=markup, 
            parse_mode='MarkdownV2'
            )
    
    @staticmethod
    def get_keyboard_markup(keys: Iterable, max_in_row: int = 3, field_text: str = None) -> ReplyKeyboardMarkup:
        n = max(1, max_in_row)        
        reply_keyboard = [keys[i:i+n] for i in range(0, len(keys), n)]
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, 
            one_time_keyboard=True,  # the keyboard hides as soon as used, but is still available from the button 
            input_field_placeholder=field_text
            )
        return reply_markup


    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info('Started.')
        # await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hello, {update.effective_user.first_name}, welcome to the recollection bot.")
        message = self.Messages.get_start(update, context)
        await self.send_message(update, context, message)
        
        await self.to_init_menu(update, context)
        return self.States.INIT

    async def to_init_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info('In init!')
        markup = self.get_keyboard_markup(self.init_menu, 2)
        message = self.Messages.get_start(update, context)
        await self.send_message(update, context, message)
        
        await update.message.reply_text("What do you want to set?", reply_markup=markup)
        return self.States.INIT



    # - parse big load of definitions
    # async parse_definitions(self, )

# - set timer for notifications, multiple notifications can be set
# - view 4 timers 
# - set timer
# - send notification
# - delete all the data

# Beyond MVP:
# - the user can provide feedback: REMEMBER, DONT REMEMBER
# - playing with the probabilities: set some
# - if the data was not provided, but the timer is set, ask user if the timer can be deleted
# - attach a database for this 
# - dockerize
# - convert choosing timer number in buttons
# - dynamic buttons for alarms, dictionaries
# - get random word button

    async def to_alarm_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info('In alarm!')
        markup = self.get_keyboard_markup(self.alarm_menu, 2)
        await update.message.reply_text(
            "Ok, you can \n1\) **view** the alarms you have already set; \n2\) **change** \(set, modify, delete\) alarms", 
            reply_markup=markup, 
            parse_mode='MarkdownV2'
            )
        return self.States.ALARM
    
    async def dictionary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        markup = self.get_keyboard_markup(self.choose_dict_menu, 2)
        await update.message.reply_text(
            "Ok, you have to choose which dictionary you want to modify\. \n\nYou get 4 slots, it is up to you how you decide to use them\. For example, if you learn multiple languages you can dedicate each dictionary slot to each language\. Another way to utilize these slots can be assigning them vocabulary from different levels \(A1 level, \.\.\., B2 level\)\. Be creative\!", 
            reply_markup=markup, 
            parse_mode='MarkdownV2'
            )
        return self.States.CHOOSE_DICTIONARY
    
    async def view_alarm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        
        alarms = []

        # TODO: get all set alarms

        alarms_str = " \n".join([f'{i+1}. {alarm}' for i, alarm in enumerate(alarms)])
        if len(alarms_str) == 0:
            alarms_str = 'None'
        markup = self.get_keyboard_markup(self.alarm_menu, 2)
        await update.message.reply_text(
            f"This are the alarms you have set: \n {alarms_str}",
            reply_markup=markup, 
            parse_mode='MarkdownV2'
            )
        return self.States.ALARM
    

    async def chosen_alarm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        alarm_num = update.message.text
        context.user_data["alarm_num"] = alarm_num
        logger.info(f"The user has chosen alarm {context.user_data['alarm_num']}")
        
        await self.choose_alarm_dict(update, context)

        return self.States.CHOOSE_ALARM_DICT

    async def choose_alarm_dict(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        markup = self.get_keyboard_markup(self.choose_dict_menu, 2)
        await update.message.reply_text(
            "Ok, you have to choose which dictionary you want to associate with this alarm\. \nFor example, you can set each alarm to a different dictionary \(if you use different dictionaries\) or set the same dictionary to all 4 alarms to get notifications from the same dictionary 4 times a day\!", 
            reply_markup=markup, 
            parse_mode='MarkdownV2'
            )
        return self.States.CHOOSE_ALARM_DICT

    async def chosen_alarm_dict(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        alarm_dict_num = update.message.text
        context.user_data["alarm_dict_num"] = alarm_dict_num
        logger.info(f"The user has chosen dict {context.user_data['alarm_dict_num']} for alarm {context.user_data['alarm_num']}")
        
        await self.change_alarm(update, context)

        return self.States.CHANGE_ALARM

    async def change_alarm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        markup = self.get_keyboard_markup(self.change_alarm_menu, 2)
        await update.message.reply_text(
            "Ok, you can set a time for the notification or delete the notification all together\.", 
            reply_markup=markup, 
            parse_mode='MarkdownV2'
            )
        return self.States.CHANGE_ALARM


    async def choose_alarm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        markup = self.get_keyboard_markup(self.choose_alarm_menu, 2)
        await update.message.reply_text(
            "Ok, you have to choose which alarm you want to modify\. \n\nYou get 4 alarms, it is up to you if you want to set all the alarms to the same dictionary or divide them\.", 
            reply_markup=markup, 
            parse_mode='MarkdownV2'
            )
        return self.States.CHOOSE_ALARM
    
    async def set_alarm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Ok, setting time for notification is really easy\! Just type any time in format HH\:MM, for example `12:30`\.", 
            reply_markup=ReplyKeyboardRemove(), 
            parse_mode='MarkdownV2'
            )
        return self.States.PROCESS_SETTING_ALARM

    async def process_setting_alarm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        alarm = update.message.text
        try:
            # TODO: parse
            # TODO: save parsed time
            # TODO: schedule a job
            await update.message.reply_text(
                f"Ok, someday I'll process {alarm}", 
                reply_markup=ReplyKeyboardRemove(), 
                parse_mode='MarkdownV2'
                )
            response_state = await self.to_alarm_menu(update, context)
            return response_state
        except:
            await update.message.reply_text(
                "Ok, I could not understand it\. Let's try again\! Next time, remember to type any time in format HH\:MM, for example `12:30`\.", 
                reply_markup=ReplyKeyboardRemove(), 
                parse_mode='MarkdownV2'
                )
            await self.change_alarm(update, context)
            return self.States.CHOOSE_ALARM
        
    async def delete_alarm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info('In delete alarm!')
        await update.message.reply_text(
                f"Ok, someday I'll delete alarm {context.user_data['alarm_num']} associated with dictionary {context.user_data['alarm_dict_num']}", 
                reply_markup=ReplyKeyboardRemove(), 
                parse_mode='MarkdownV2'
                )
        
        # TODO: delete the alarm

        response_state = await self.to_alarm_menu(update, context)
        return response_state

    async def choose_dict(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        dict_num = update.message.text
        context.user_data["dict_num"] = dict_num
        logger.info(f"The user has chosen dict {context.user_data['dict_num']}")
        
        await self.to_dict_menu(update, context)

        return self.States.DICTIONARY


    async def add_words(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        markup = self.get_keyboard_markup(self.add_words_menu, 2)
        await update.message.reply_text(
            "Ok, send me words with definitions\. You can add them in batches or one by one\. When you are done, press the `Back` button\.",
            reply_markup=markup, 
            parse_mode='MarkdownV2'
            )
        return self.States.ADD_WORDS_DICTIONARY
    
    async def add_more(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        markup = self.get_keyboard_markup(self.add_words_menu, 2)

        # TODO: process update.message.text

        await update.message.reply_text(
            f"Ok, someday I am going to process {update.message.text}\. In the mean time, you can send more\. When you are done, press the `Back` button\.",
            reply_markup=markup, 
            parse_mode='MarkdownV2'
            )
        return self.States.ADD_WORDS_DICTIONARY


    async def get_definition(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        markup = self.get_keyboard_markup(['Back'], 2)
        await update.message.reply_text(
            "Ok, please send me a word you want to find definition for in any dictionary you have\.", 
            reply_markup=markup, 
            parse_mode='MarkdownV2'
            )
        return self.States.PROCESSING_DEFINITION


    async def processing_definition(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        word = update.message.text
        try:
            # TODO: parse
            # TODO: search through all dicts
            # TODO: return answer
            await update.message.reply_text(
                f"Ok, someday I'll find you a definition for {word}", 
                reply_markup=ReplyKeyboardRemove(), 
                parse_mode='MarkdownV2'
                )
            
            response_state = await self.to_init_menu(update, context)
            return response_state
        except:
            await update.message.reply_text(
                "Ok, something went terribly wrong there.", 
                # reply_markup=ReplyKeyboardRemove(), 
                parse_mode='MarkdownV2'
                )
            response_state = await self.to_init_menu(update, context)
            return response_state
        


    async def delete_dict(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        markup = self.get_keyboard_markup(self.delete_dict_menu, 2)

        await update.message.reply_text(
            f"Ok, you do you want to delete just one specific word or all words from the dictionary\?",
            reply_markup=markup, 
            parse_mode='MarkdownV2'
            )
        return self.States.DELETE_DICTIONARY

    async def delete_one_word(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        markup = self.get_keyboard_markup(['Back'], 2)
        await update.message.reply_text(
            "Ok, please send me a word you want to delete\.", 
            reply_markup=markup, 
            parse_mode='MarkdownV2'
            )
        return self.States.DELETING_WORD

    async def deleting_word(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        word = update.message.text
        try:
            # TODO: parse
            # TODO: delete from dict
            # TODO: check if the word exists
            await update.message.reply_text(
                f"Ok, someday I'll delete {word}", 
                reply_markup=ReplyKeyboardRemove(), 
                parse_mode='MarkdownV2'
                )
            
            response_state = await self.to_dict_menu(update, context)
            return response_state
        except:
            await update.message.reply_text(
                "Ok, something went terribly wrong there.", 
                reply_markup=ReplyKeyboardRemove(), 
                parse_mode='MarkdownV2'
                )
            response_state = await self.to_dict_menu(update, context)
            return response_state
        

    async def delete_all_words(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # TODO: delete all words

        await update.message.reply_text(
            f"Ok, someday I'll delete all words from {context.user_data['dict_num']} ", 
            reply_markup=ReplyKeyboardRemove(), 
            parse_mode='MarkdownV2'
            )
        
        response_state = await self.to_dict_menu(update, context)
        return response_state

    async def to_dict_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        markup = self.get_keyboard_markup(self.dict_menu, 2)
        await update.message.reply_text(
            f"Ok, what would you like to do with the {context.user_data['dict_num']}\?",
            reply_markup=markup, 
            parse_mode='MarkdownV2'
            )

        return self.States.DICTIONARY

    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        pass
    
    async def done(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info('In done!')

    async def language(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info('In lang!')

    # set the separator
    async def set_separator(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        separator = context.args[0]
        chat_id = update.effective_chat.id
        self.data_handler.set_separator(chat_id=chat_id, separator=separator)
        await context.bot.send_message(chat_id=chat_id, text=f"The separator is now:{self.data_handler.load_separator(chat_id)}")

    def run(self):
        init_menu_actions = [self.to_alarm_menu, self.dictionary, self.get_definition]
        alarm_menu_actions = [self.view_alarm, self.choose_alarm, self.to_init_menu]
        choose_alarm_menu_actions = [self.chosen_alarm for _ in self.choose_alarm_menu[:-1]] + [self.to_alarm_menu]
        choose_alarm_dict_menu_actions = [self.chosen_alarm_dict for _ in self.choose_dict_menu]
        change_alarm_menu_actions = [self.set_alarm, self.delete_alarm, self.to_alarm_menu]
        
        choose_dict_menu_actions = [self.choose_dict for _ in self.choose_dict_menu[:-1]] + [self.to_init_menu]
        dict_menu_actions = [self.add_words, self.delete_dict] + [self.to_init_menu]
        delete_dict_menu_actions = [self.delete_one_word, self.delete_all_words]
        add_words_menu_actions = [self.to_dict_menu]
        
        button_names = [self.init_menu, self.alarm_menu, self.choose_alarm_menu, self.change_alarm_menu, self.choose_dict_menu, self.dict_menu, self.delete_dict_menu, self.add_words_menu]
        button_actions = [init_menu_actions, alarm_menu_actions, 
            choose_alarm_menu_actions, change_alarm_menu_actions, 
            choose_dict_menu_actions, dict_menu_actions, delete_dict_menu_actions, add_words_menu_actions]

        for names, actions in zip(button_names, button_actions):
            assert len(names) == len(actions)

        application = ApplicationBuilder().token(self.token).build()
    
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                self.States.INIT: [
                    MessageHandler(
                        filters.Regex(f"^({self.init_menu[i]})$"), init_menu_actions[i]
                    ) for i in range(len(self.init_menu))
                    ],
                
                self.States.ALARM: [
                    MessageHandler(
                        filters.Regex(f"^({self.alarm_menu[i]})$"), alarm_menu_actions[i]
                    ) for i in range(len(self.alarm_menu))
                    ],
                self.States.CHOOSE_ALARM: [
                    MessageHandler(
                        filters.Regex(f"^({self.choose_alarm_menu[i]})$"), choose_alarm_menu_actions[i]
                    ) for i in range(len(self.choose_alarm_menu))
                    ],
                self.States.CHOOSE_ALARM_DICT: [
                    MessageHandler(
                        filters.Regex(f"^({self.choose_dict_menu[i]})$"), choose_alarm_dict_menu_actions[i]
                    ) for i in range(len(self.choose_dict_menu))
                    ],
                self.States.CHANGE_ALARM: [
                    MessageHandler(
                        filters.Regex(f"^({self.change_alarm_menu[i]})$"), change_alarm_menu_actions[i]
                    ) for i in range(len(self.change_alarm_menu))
                    ],
                self.States.PROCESS_SETTING_ALARM: [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND | filters.Regex(f"^Done|Back$")), self.process_setting_alarm
                    ),
                    MessageHandler(
                        filters.Regex(f"^Back$"), self.change_alarm
                    )
                    ],
                self.States.PROCESSING_DEFINITION: [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND | filters.Regex(f"^Done|Back$")), self.processing_definition
                    ),
                    MessageHandler(
                        filters.Regex(f"^Back$"), self.to_init_menu
                    )
                    ],
                self.States.DELETING_WORD: [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND | filters.Regex(f"^Done|Back$")), self.deleting_word
                    ),
                    MessageHandler(
                        filters.Regex(f"^Back$"), self.to_dict_menu
                    )
                    ],
                
                self.States.CHOOSE_DICTIONARY: [
                    MessageHandler(
                        filters.Regex(f"^({self.choose_dict_menu[i]})$"),
                         choose_dict_menu_actions[i]
                    ) for i in range(len(self.choose_dict_menu))
                    ],
                self.States.DICTIONARY: [
                    MessageHandler(
                        filters.Regex(f"^({self.dict_menu[i]})$"), dict_menu_actions[i]
                    ) for i in range(len(self.dict_menu))
                    ],
                self.States.DELETE_DICTIONARY: [
                    MessageHandler(
                        filters.Regex(f"^({self.delete_dict_menu[i]})$"), delete_dict_menu_actions[i]
                    ) for i in range(len(self.delete_dict_menu))
                    ],
                self.States.ADD_WORDS_DICTIONARY: [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND | filters.Regex(f"^Done|{'|'.join(self.add_words_menu)}$")), self.add_more
                    )
                ]+[
                    MessageHandler(
                        filters.Regex(f"^({self.add_words_menu[i]})$"), add_words_menu_actions[i]
                    ) for i in range(len(self.add_words_menu))
                    ],
                
            },
            fallbacks=[MessageHandler(filters.Regex("^Done$"), self.done)],
        )

        application.add_handler(conv_handler)


        separator_handler = CommandHandler('set_separator', self.set_separator)
        application.add_handler(separator_handler)

        help_handler = CommandHandler('help', self.help)
        application.add_handler(help_handler)

        lang_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("language", self.language)],
        states={
            0: [MessageHandler(filters.Regex("^()$"), self.language)],
        },
        fallbacks=[CommandHandler("cancel", self.language)],
        )

        application.add_handler(lang_conv_handler)


        application.run_polling()



if __name__ == '__main__':
    data_handler = FileHandler()
    token = os.getenv('TOKEN')

    bot_caller = BotCaller(data_handler=data_handler, token=token)
    bot_caller.run()