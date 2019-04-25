from abc import ABC, abstractmethod
from enum import Enum


class Context(ABC):
    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def set(self):
        pass


class NoneContext(Context):
    async def get(self):
        return None

    async def set(self):
        pass
