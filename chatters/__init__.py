from json import dumps

import aiohttp


async def get_chatters():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://tmi.twitch.tv/group/user/sudokid/chatters', timeout=25) as resp:
            if resp.status != 200:
                response = await resp.text()
            else:
                response = dumps(await resp.json())

            await save_chatters(response)


async def save_chatters(msg: str):
    print(msg)
