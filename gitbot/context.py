from abc import ABC, abstractmethod
from enum import Enum


class Context(ABC):
    @abstractmethod
    def get(self, chat_id):
        pass

    @abstractmethod
    def set(self, chat_id, state):
        pass
