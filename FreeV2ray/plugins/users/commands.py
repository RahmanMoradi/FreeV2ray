from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from pyrogram.errors import UserNotParticipant
from pyromod import listen, ikb, array_chunk

from FreeV2ray.app import config
from FreeV2ray.v2ray.api import V2ray

from datetime import datetime
from jdatetime import jalali



@Client.on_message(filters.private)
async def check_join(client: Client, message: Message):
    instagram = "https://www.instagram.com/" + config.get('INSTAGRAM')
    channel = await client.get_chat(config.get("CHANNEL"))

    try:
        await client.get_chat_member(channel.id, message.from_user.id)
        await message.continue_propagation()
    except UserNotParticipant:
        return await client.send_message(
            message.chat.id,
            "لطفا برای دریافت کانفیگ v2ray رایگان اول اینستاگرام مارا فالو کرده سپس در کانال تلگرامی ما جوین شوید!",
            reply_markup=ikb([
                [("پیج اینستاگرام ما", instagram, "url")],
                [("کانال تلگرام ما", channel.invite_link, "url")],
                [("عضو شدم", "joined")]
            ])
        )


async def wait_for_answer(client: Client, message: Message):
    commands = {
        "دریافت کانفیگ": get_config_handler,
        "کانفیگ من": my_config_handler,
        "پشتیبانی": support_handler,
    }
    command = commands.get(message.text)

    if command:
        await command(client, message)
    else:
        await message.reply("دستور نامعتبر! لطفا دوباره امتجان کنید:")
        return await start_handler(client, message)


@Client.on_message(filters.private & filters.command("start"))
async def start_handler(client: Client, message: Message):
    message = await message.chat.ask(
        "با سلام به ربات دریافت v2ray شخصی رایگان خوش امدید!",
        reply_markup=ReplyKeyboardMarkup([
            ["دریافت کانفیگ"],
            ["پشتیبانی", "کانفیگ من"],
        ], resize_keyboard=True)
    )

    await wait_for_answer(client, message)


async def get_config_handler(client: Client, message: Message):
    panel = V2ray(config.get("PANEL_USERNAME"), config.get("PANEL_PASSWORD"))
    v2ray_config, created = panel.get_or_create_client(str(message.from_user.id))
    if created:
        # TODO: add the config that has been created to the database
        await message.reply(v2ray_config)
    else:
        await message.reply("شما در حال حاضر کانفیگ دارین!")


async def my_config_handler(client: Client, message: Message):
    panel = V2ray(config.get("PANEL_USERNAME"), config.get("PANEL_PASSWORD"))
    client = panel.get_client(str(message.from_user.id))
    if not client:
        await message.reply("شما در حال حاضر هیچ کانفیگی دریافت نکرده اید!")
    else:
        expire_date = datetime.fromtimestamp(int(str(client["expiryTime"])[:-3]))
        expire_date = jalali.GregorianToJalali(expire_date.year, expire_date.month, expire_date.day)
        email = client['email']
        v2ray_config = panel.generate_config(email)

        await message.reply(f"نام کاربری: {email}"
                            "\n"
                            f"تاریخ انقضا: {expire_date.jyear}/{expire_date.jmonth}/{expire_date.jday}"
                            "\n"
                            f"کانفیگ: `{v2ray_config}`"
                            )


async def support_handler(client: Client, message: Message):
    return await message.reply(f"جهت هرگونه سوال یا مشکل به این ایدی مراجعه فرمایین: {config.get('ADMIN')}")
