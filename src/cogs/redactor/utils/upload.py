import asyncio

import aiohttp

from src.models import User


async def load_code_from_github(owner: str,
                                repo: str,
                                user: User,
                                branch: str):
    """
    Load from GitHub Repository,
    i guess its bad method, but codeload.github.com/ is blocked, FUCK

    :param owner: need for find github repo
    :param repo: repo name
    :param user: user for path
    :param branch:
    :return:
    """
    url = f"https://github.com/{owner}/{repo}/{branch}.zip"
    await upload(repo, user.user_path, url)


async def upload(repo: str, user_path: str, url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            await download_as_zip(f"{user_path}/{repo}.zip", resp)


async def download_as_zip(path: str, resp):
    chunk_size = 30

    with open(path, 'wb') as fd:
        while True:
            chunk = await resp.content.read(chunk_size)
            if not chunk:
                break
            fd.write(chunk)
