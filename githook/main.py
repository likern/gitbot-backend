from typing import List, Iterable, Union
from functools import wraps, partial
from collections import defaultdict
import inspect
from inspect import signature
import json

import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient
import pydantic
from pydantic import BaseModel

from models.telegram import SendMessage, ChatId
from models import telegram
from .exceptions import NoHandlerError, MultipleHandlerError, MultipleMiddlewareError, MiddlewareSignatureError
from .context import Context, NoneContext

BASE_URL = "https://api.github.com"


class GitHub:
    def __init__(
        self,
        token: str,
        context: Context = NoneContext,
        http_client: aiohttp.ClientSession = None,
        mongodb_client: AsyncIOMotorClient = None,
        base_url: str = BASE_URL):

        self._allowed_handler_args = ["middleware", "set_context"]
        self._token = token
        self._base_url = f"{base_url}{token}/"
        self.http_client = http_client
        self.mongodb_client = mongodb_client
        self.context = context
        self._handlers = defaultdict(dict)
        self._middlewares = defaultdict(dict)
        self._middleware_for_handler = defaultdict(dict)


    async def _raise_exception(func):
                raise ValueError(f"Function [{func.__qualname__}] shouldn't be called directly")

    def prepare(self):
        if not self._middleware_for_handler:
            self._build_subclass_hierarchy()

    def _build_subclass_hierarchy(self):
        for (state, state_handlers_info) in self._handlers.items():
                state_middlewares_info = self._middlewares[state]
                for (message_handler, handler_info) in state_handlers_info.items():
                    for (message_middleware, middleware_info) in state_middlewares_info.items():
                        if issubclass(message_handler, message_middleware):
                            coro = handler_info["coro"]
                            if self._middleware_for_handler[state].get(coro):
                                raise MultipleMiddlewareError(
                                    f"Found multiple middlewares for handler [{coro.__qualname__}]"
                                )
                            self._middleware_for_handler[state][coro] = middleware_info["coro"]
            

    def _check_types(self, message_type) -> Iterable[BaseModel]:
        if issubclass(message_type, pydantic.BaseModel):
            return [message_type]
        elif issubclass(message_type, Iterable):
            for item in message_type:
                if not issubclass(item, pydantic.BaseModel):
                    raise TypeError(f"Type [{item}] should be subclass of [BaseModel] type")
            return message_type
        
        raise TypeError(f"Type [{item}] should be subclass of [BaseModel] or [Iterable[BaseModel]] type")

    def _check_async_func(self, func) -> None:
        if not inspect.iscoroutinefunction(func):
            raise TypeError(
                f"function [{func.__qualname__}] is not asynchronous"
            )

    def _get_state_middleware_for_handler(self, state):
        return self._middleware_for_handler[state]
        
    def _get_state_handlers(self, state):
        return self._handlers[state]

    def _get_state_middlewares(self, state):
        return self._middlewares[state]

    def _get_handler_coro_info(self, coro):
        coro_info = {
            "coro": coro,
            "arguments": {
                "middleware": False,
                "set_context": False
            }
        }

        params = signature(coro).parameters
        for (index, (key, value)) in enumerate(params.items()) :
                if index != 0:
                    if key in self._allowed_handler_args:
                        coro_info["arguments"][key] = True
                    else:
                        raise MiddlewareSignatureError(
                            f"function [{coro.__qualname__}] can't contain parameter [{key}]"
                        )
        return coro_info

    def _get_middleware_coro_info(self, coro):
        coro_info = {
            "coro": coro
        }

        params = signature(coro).parameters
        params_length = len(params)

        if params_length > 1:
            raise MiddlewareSignatureError(
                f"function [{coro.__qualname__}] can't contain multiple parameters"
            )
        elif params_length < 1:
            raise MiddlewareSignatureError(
                f"function [{coro.__qualname__}] should contain one required parameter"
            )

        return coro_info

    # def _run_middleware(state, payload):
    #     state_middlewares = self._get_state_middlewares(state)
    #     for (message, middleware) in state_middlewares.items():
    #         try:
    #             model = message.parse_obj(payload)
    #             return await middleware(model)
    #         except pydantic.ValidationError as err:
    #             continue

    def handler(self, msg_type: pydantic.BaseModel, state=None):
        def internal_function(func):
            self._check_async_func(func)
            

            coro_info = self._get_handler_coro_info(func)
            state_handlers = self._get_state_handlers(state)
            if msg_type in state_handlers:
                raise MultipleHandlerError(
                        f"Register multiple handlers for the same msg_type [{msg_type}] is prohibited"
                    )

            state_handlers[msg_type] = coro_info

            # partial_func = None
            # if arguments["middleware"] and arguments["set_context"]:
            #     partial_func = partial(
            #         func, 
            #         middleware=argument["middle"],
            #         set_context=argument["set_context"]
            #     )
            # elif arguments["middleware"] and not arguments["set_context"]:
            #     partial_func = partial(
            #         func, 
            #         middleware=argument["middle"]
            #     )
            # elif not arguments["middleware"] and arguments["set_context"]
            #     partial_func = partial(
            #         func, 
            #         set_context=argument["set_context"]
            #     )
            # else:
            #     partial_func = func 


                # if value.kind == value.KEYWORD_ONLY:
                #     raise MiddlewareSignatureError(
                #         f"function [{func.__qualname__}] can't contain keyword-only parameters"
                #     )

                # if value.kind == value.VAR_KEYWORD:
                #     raise MiddlewareSignatureError(
                #         f"function [{func.__qualname__}] can't contain **{key} parameter"
                #     )

                # if value.kind == value.VAR_POSITIONAL:
                #     raise MiddlewareSignatureError(
                #         f"function [{func.__qualname__}] can't contain *{key} parameter"
                #     )
                 
                # if not index and :
                #     raise MiddlewareSignatureError(
                #         f"function [{func.__qualname__}] can't contain *{key} parameter"
                #     )

            return self._raise_exception
        return internal_function

    def middleware(self, type: Union[BaseModel, Iterable[BaseModel]], *, state=None):
        types = self._check_types(type)

        def internal_function(func):
            self._check_async_func(func)

            coro_info = self._get_middleware_coro_info(func)
            state_middlewares = self._get_state_middlewares(state)
            for msg_type in types:
                if msg_type in state_middlewares:
                    raise MultipleHandlerError(
                            f"Register multiple middlewares for the same msg_type [{msg_type}] is prohibited"
                        )

                state_middlewares[msg_type] = coro_info
            return self._raise_exception
        return internal_function

    async def webhook(self, request):
        # Build hierarchy only once
        if not self._middleware_for_handler:
            self._build_subclass_hierarchy()

        print("GITHUB INCOMING WEBHOOK JSON:")
        print(json.dumps(request.json, indent=2, sort_keys=True))

        payload = request.json
        state = await self.context.get()
        state_middlewares = self._get_state_middlewares(state)
        state_handlers = self._get_state_handlers(state)
        state_middleware_for_handler = self._get_state_middleware_for_handler(state)

        for (message, handler_info) in state_handlers.items():
            model = None
            try:
                model = message.parse_obj(payload)
            except pydantic.ValidationError as err:
                continue

            if model:
                handler_coro = handler_info["coro"]
                middleware = state_middleware_for_handler.get(handler_coro)

                pass_middleware = handler_info["arguments"]["middleware"]
                pass_set_context = handler_info["arguments"]["set_context"]
                if middleware:
                    if pass_middleware:
                        if pass_set_context:
                            return await handler_coro(
                                model,
                                middleware=middleware(model),
                                set_context=self.context.set
                            )
                        else:
                            return await handler_coro(
                                model,
                                middleware=middleware(model)
                            )
                    else:
                        await middleware(model)
                        if pass_set_context:
                            return await handler_coro(
                                model,
                                set_context=self.context.set
                            )
                        else:
                            return await handler_coro(
                                model
                            )
                else:
                    if pass_set_context: 
                        return await handler_coro(
                            model,
                            set_context=self.context.set
                        )
                    else:
                        return await handler_coro(model)
            else:
                raise NoHandlerError("No handlers found for payload", payload)

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
