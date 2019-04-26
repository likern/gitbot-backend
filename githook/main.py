from typing import List
from functools import wraps
import json

import aiohttp
import pydantic

from models.telegram import SendMessage, ChatId
from models import telegram
from .exceptions import NoHandlerError, MultipleHandlerError, MultipleMiddlewareError
from .context import Context

BASE_URL = "https://api.github.com"


class GitHub:
    def __init__(self, token: str, context: Context = None, http_client: aiohttp.ClientSession = None, base_url: str = BASE_URL):
        self._token = token
        self._base_url = f"{base_url}{token}/"
        self.http_client = http_client
        self.context = context
        self._handlers = {}
        self._none_handlers = {}
        self._middlewares = {}
        self._none_middlewares = {}

    def handler(self, msg_type: pydantic.BaseModel, state=None):
        def internal_function(func):
            async def wrapped(message):
                return await func(message, self.context.set)

            if state is None:
                if msg_type in self._none_handlers:
                    raise MultipleHandlerError(
                        f"Register multiple handlers for the same msg_type [{msg_type}] is prohibited"
                    )

                else:
                    self._none_handlers[msg_type] = wrapped
            else:
                if (state in self._handlers) and (msg_type in self._handlers[state]):
                    raise MultipleHandlerError(
                        f"Register multiple handlers for the same state [{state}]\
                             and msg_type [{msg_type}] is prohibited"
                    )
                else:
                    self._handlers[state] = [(msg_type, wrapped)]

            return wrapped
        return internal_function

    def middleware(self, msg_types: List[pydantic.BaseModel], state=None):
        def internal_function(func):
            async def wrapped(message):
                return await func(message)

            if state is None:
                for msg_type in msg_types:
                    if msg_type in self._none_middlewares:
                        raise MultipleMiddlewareError(
                            f"Register multiple middlewares for the same msg_type [{msg_type}] is prohibited"
                        )
                    else:
                        self._none_middlewares[msg_type] = wrapped
            else:
                state_middleware = self._middlewares.get(state)
                if state_middleware is None:
                    state_middleware = []
                    for msg_type in msg_types:
                        state_middleware.append((msg_type, wrapped))
                    self._middlewares[state] = state_middleware
                else:
                    for msg_type in msg_types:
                        for (exist_msg_type, func) in state_middleware:
                            if msg_type == exist_msg_type:
                                raise MultipleMiddlewareError(
                                    f"Register multiple middlewares for the same msg_type [{msg_type}] is prohibited"
                                )
                        state_middleware.append((msg_type, wrapped))

            return wrapped
        return internal_function

    async def webhook(self, request):
        print("GITHUB INCOMING WEBHOOK JSON:")
        print(json.dumps(request.json, indent=2, sort_keys=True))
        payload = request.json

        model = None
        func = None
        state = await self.context.get()
        if state is None:
            for (msg_type, middleware) in self._none_middlewares.items():
                try:
                    model = msg_type.parse_obj(payload)
                    await middleware(model)
                    break
                except pydantic.ValidationError as err:
                    continue


            # iterate over all types
            for (msg_type, closure) in self._none_handlers.items():
                try:
                    model = msg_type.parse_obj(payload)
                    func = closure
                    break
                except pydantic.ValidationError as err:
                    continue
            else:
                raise NoHandlerError("No handlers found for payload", payload)
        else:
            middlewares = self._middlewares.get(state)
            if middlewares:
                for (msg_type, middleware) in middlewares:
                    try:
                        model = msg_type.parse_obj(payload)
                        await middleware(model)
                        break
                    except pydantic.ValidationError:
                        continue            

            handlers = self._handlers.get(state)
            if handlers:
                for (msg_type, closure) in handlers:
                    try:
                        model = msg_type.parse_obj(payload)
                        func = closure
                        break
                    except pydantic.ValidationError:
                        continue
                else:
                    raise NoHandlerError(
                        "No handlers found for payload", payload)
            else:
                raise NoHandlerError("No handlers found for payload", payload)

        return await func(model)

    async def send_message(self, obj_type=telegram.SendMessage, **kwargs):

        if not issubclass(obj_type, telegram.SendMessage):
            raise TypeError(
                f"{obj_type} should be subclass of telegram.SendMessage")

        if 'parse_mode' not in kwargs:
            kwargs['parse_mode'] = telegram.ParseMode.markdown

        model = obj_type(**kwargs)
        json_payload = model.dict(skip_defaults=True)
        url = f"{self._base_url}sendMessage"
        async with self.http_client.post(url, json=json_payload) as resp:
            print(f"Response status [{resp.status}]")
            json = await resp.json()
            return json
            print(f"Response body: [{json}]")

    async def delete_message(self, obj_type=telegram.DeleteMessage, **kwargs):

        if not issubclass(obj_type, telegram.DeleteMessage):
            raise TypeError(
                f"{obj_type} should be subclass of telegram.DeleteMessage")

        model = obj_type(**kwargs)
        json_payload = model.dict(skip_defaults=True)
        url = f"{self._base_url}deleteMessage"
        async with self.http_client.post(url, json=json_payload) as resp:
            print(f"Response status [{resp.status}]")
            json = await resp.json()
            return json
            print(f"Response body: [{json}]")
