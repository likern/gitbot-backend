from contextvars import ContextVar
import asyncio

telegram_chat_id = ContextVar('telegram_chat_id')


class Intl:
    def __init__(self, collection, user_col):
        self._collection = collection
        self._users = user_col

    def __getattribute__(self, attr):
        if attr.startswith('_'):
            return object.__getattribute__(self, attr)

        async def internal_function():
            chat_id = telegram_chat_id.get()
            document = await self._users.find_one(
                filter={"settings.privacy.chat_id": chat_id},
                projection=["settings.lang.current"]
            )

            if document:
                lang = document['settings']['lang']['current']
                document = await self._collection.find_one(
                    filter={"key": attr, "lang": lang},
                    projection=["text"]
                )

                if document is None:
                    document = await self._collection.find_one(
                        filter={"key": attr, "lang": "en"},
                        projection=["text"]
                    )

                return document['text']

            raise ValueError(
                f"Can't find document for [settings.privacy.chat_id = {chat_id}]"
            )

        return internal_function()
