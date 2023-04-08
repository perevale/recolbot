from abc import ABCMeta, abstractmethod

class Button(metaclass=ABCMeta):
    
    @property
    @abstractmethod
    def alarm(self):
        pass

class ButtonEN(Button):
    alarm = None

class ButtonRU(Button):
    alarm = None
