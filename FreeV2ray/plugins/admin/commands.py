from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup


from FreeV2ray.app import  config
from FreeV2ray.plugins.users.commands import start_handler
from FreeV2ray.models import get_all_users


ADMIN = int(config.get('ADMIN_ID'))


@Client.on_message(filters.user(ADMIN), filters.command("all"))
async def send_to_everyone(client: Client, message: Message):
    message = message.chat.ask(
        "سلام ادمین گرامی لطفا پیامی که میخای برای همه ارسال بشه رو برام ارسال کن!",
        reply_markup=ReplyKeyboardMarkup([
            ["انصراف"]
        ], resize_keyboard=True)
    )

    if message.text == "انصراف":
        return start_handler(client, message)

    users = get_all_users()
    for user in users:
        await message.copy(chat_id=user.chat_id)
    else:
        await message.reply("این پیام برای همه ارسال شد!")
        return start_handler(client, message)

