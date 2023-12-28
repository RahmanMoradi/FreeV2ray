from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from pyrogram.errors import UserNotParticipant
from pyromod import listen, ikb, array_chunk

from FreeV2ray.app import config
from FreeV2ray.plugins.users.commands import start_handler


@Client.on_callback_query(filters.regex(r"^joined$"))
async def joined_callback(client: Client, query: CallbackQuery):
    message = query.message
    channel = await client.get_chat(config.get("CHANNEL"))

    try:
        chat_member = await client.get_chat_member(channel.id, query.from_user.id)
        await message.delete()
        return await start_handler(client, query.message)
    except UserNotParticipant:
        return await message.reply("شما هنوز در کانال ما عضو نشده اید!")
