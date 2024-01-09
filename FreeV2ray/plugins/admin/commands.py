from pyrogram import Client, filters
from pyrogram.types import Message

from pyromod.helpers import ikb

from FreeV2ray.app import  config


ADMIN = int(config.get('ADMIN'))


@Client.on_message(filters.user(ADMIN), filters.command("/all"))
async def send_to_everyone(client: Client, message: Message):
    message = message.chat.ask(
        "سلام ادمین گرامی لطفا پیامی که میخای برای همه ارسال بشه رو برام ارسال کن!",
        reply_markup=ikb([["انصراف"]])
    )

