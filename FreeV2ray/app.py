import os
from pathlib import Path

from pyrogram import idle
from pyromod import Client, listen

from dotenv import dotenv_values
import logging

import FreeV2ray

path = os.path.dirname(FreeV2ray.__file__)

config_path = str(Path(path).resolve().parents[0]) + "/.env"
config = dotenv_values(config_path)

logger = logging.getLogger("telegram")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

app = Client(
    name=config.get("APP_NAME"),
    api_id=config.get("API_ID"),
    api_hash=config.get("API_HASH"),
    bot_token=config.get("API_TOKEN"),
    plugins=dict(root="plugins/")
)

if config.get("PROXY_HOSTNAME") is not None:
    proxy = dict(
        scheme=config.get("PROXY_SCHEME"),
        hostname=config.get("PROXY_HOSTNAME"),
        port=int(config.get("PROXY_PORT")),
    )
    if username := config.get("PROXY_USERNAME"):
        proxy["username"] = username
    if password := config.get("PROXY_PASSWORD"):
        proxy["password"] = password

    app.proxy = proxy


if __name__ == "__main__":
    with app:
        logger.info("Telegram Bot Is Running ...")
        idle()
