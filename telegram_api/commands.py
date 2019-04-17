import aiohttp

token="731461938:AAHBePXz0g-QtDTHLOHX0CqcYRm71_apgcg"
base_url="https://api.telegram.org/bot<token>/METHOD_NAME"

def make_url_from(token, method_name):
  return "https://api.telegram.org/bot{token}/{method_name}".format(token, method_name)

async def help_command():
  async with aiohttp.ClientSession() as session:
    url = make_url_from(token, "sendMessage")
    async with session.post(url) as resp:
      print(resp.status)
      print(await resp.text())