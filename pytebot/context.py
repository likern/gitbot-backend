from abc import ABC, abstractmethod
from enum import Enum


class FinalMeta(type(ABC), type(Enum)):
    pass


class Context(ABC):
    @abstractmethod
    def get(self, chat_id):
        pass

    @abstractmethod
    def set(self, chat_id, state):
        pass
