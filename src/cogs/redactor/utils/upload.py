import os

import aiohttp

from src.models import User
from src.utils.http import get


async def load_code_from_github(owner: str, repo: str, user: User, file_path: str = ""):
    """
    Load from GitHub Repository,
    This function Parse Jsom from github
    and download with "download_url" in json reposnse
    i guess it ll be slow function

    :param owner: need for find github repo
    :param repo: repo name
    :param user: user for path
    :param file_path:
    :return:
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    user_path = user.user_path
    await download_n_upload(user_path, url)


async def download_n_upload(user_path: str, url: str):
    if not os.path.exists(user_path):
        return

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            json = await resp.text()
            pass  # I Cant