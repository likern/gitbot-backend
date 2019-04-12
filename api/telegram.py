import aiohttp
from models import SendMessage, ChatId


BASE_URL = "https://api.telegram.org/bot"


class Telegram:
    def __init__(self, base_url=BASE_URL, *, token, client):
        self.base_url = f"{base_url}{token}/"
        self._client = client

    async def send_message(self, chat_id: ChatId, text: str):
        payload = SendMessage(chat_id=chat_id, text=text).dict(
            skip_defaults=True)
        url = f"{self.base_url}sendMessage"
        async with self._client.post(url, json=payload) as resp:
            print(f"Response status [{resp.status}]")
            json = await resp.json()
            print(f"Response body: [{json}]")
