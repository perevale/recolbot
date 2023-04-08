from abc import ABCMeta, abstractmethod
from telegram import Update
from telegram.ext import ContextTypes



class Messages(metaclass=ABCMeta):
    
    @abstractmethod
    def get_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        raise NotImplementedError
  
    # @abstractmethod
    # def get_to_init_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     raise NotImplementedError

    # @abstractmethod
    # def get_to_init_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     raise NotImplementedError

    # @abstractmethod
    # def get_to_init_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     raise NotImplementedError

    # @abstractmethod
    # def get_to_init_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     raise NotImplementedError


class MessagesEN(Messages):
    def get_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        return f"Hello, {update.effective_user.first_name}, welcome to the recollection bot."

class MessagesRU(Messages):
    def get_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        return f"Привет, {update.effective_user.first_name}, добро пожаловать в бота, который поможет тебе запоминать."
