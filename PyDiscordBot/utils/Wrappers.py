from typing import Optional

from aiohttp import ClientSession

from PyDiscordBot.utils import DataUtils


async def pastebin_paste(data, paste_format: Optional[str] = "python") -> str:
    """
    :return: URL of pastebin link
    :rtype: str
    """

    key = DataUtils.config["pastebin_key"]
    to_post = {
        "api_option": "paste",
        "api_paste_format": paste_format,
        "api_dev_key": key,
        "api_paste_code": str(data)
    }
    async with ClientSession() as session:
        async with session.post("https://pastebin.com/api/api_post.php", data=to_post) as post:
            return await post.text()
