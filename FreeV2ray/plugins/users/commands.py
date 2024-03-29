from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    ReplyKeyboardMarkup,
)
from pyrogram.errors import UserNotParticipant
from pyromod import listen, ikb

from FreeV2ray.app import config, scheduler, v2rayng_picture
from FreeV2ray.models import add_user, get_all_users
from FreeV2ray.v2ray.api import V2ray

from datetime import datetime, timedelta
from jdatetime import jalali


async def send_to_everyone(client: Client, message: Message):
    if message.from_user.id != int(config.get('ADMIN_ID')):
        await message.reply("دستور نامعتبر! لطفا دوباره امتجان کنید:")
        return await start_handler(client, message)

    message = await message.chat.ask(
        "سلام ادمین گرامی لطفا پیامی که میخای برای همه ارسال بشه رو برام ارسال کن!",
        reply_markup=ReplyKeyboardMarkup([
            ["انصراف"]
        ], resize_keyboard=True)
    )

    if message.text == "انصراف":
        return await start_handler(client, message)

    users = get_all_users()
    for user in users:
        await message.copy(chat_id=user.chat_id)
    else:
        await message.reply("این پیام برای همه ارسال شد!")
        return await start_handler(client, message)


async def send_notification(client: Client, chat_id):
    await client.send_message(
        chat_id=chat_id,
        text="تنها یک روز دیگر تا پایان اعتبار کانفیگ شما باقیست! جهت تمدید دقیقا ۲۴ ساعت اینده به ربات مراجعه کنید!"
    )


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


@Client.on_message(filters.private & filters.command("start"))
async def start_handler(client: Client, message: Message):
    await add_user(message.from_user.id)
    await client.send_photo(
        message.chat.id,
        v2rayng_picture,
        "با سلام به ربات دریافت v2ray شخصی رایگان خوش امدید!",
        reply_markup=ReplyKeyboardMarkup([
            ["دریافت کانفیگ"],
            ["پشتیبانی", "کانفیگ من"],
        ], resize_keyboard=True)
    )


@Client.on_message(filters.private & filters.command("دریافت کانفیگ", prefixes=""))
async def get_config_handler(client: Client, message: Message):
    panel = V2ray(config.get("PANEL_USERNAME"), config.get("PANEL_PASSWORD"))
    v2ray_config, created = panel.get_or_create_client(str(message.from_user.id))
    expire_days = int(config.get("EXPIRE_TIME"))
    if created:
        notification_days = int(config.get("NOTIFICATION_TIME"))
        expire_date = datetime.now() + timedelta(expire_days - notification_days)
        scheduler.add_job(send_notification, "date", run_date=expire_date, args=(client, message.chat.id))

        return await message.reply(
            ("کانفیگ رایگان یک هفته ای شما با موفقیت ساخته شد!"
             "\n"
             f"کانفیگ: `{v2ray_config}`"
             )
        )

    else:
        v2ray_client = v2ray_config
        now_timestamp = int(datetime.now().timestamp() * 1000)
        expire_timestamp = v2ray_client.get("expiryTime")
        if now_timestamp > expire_timestamp:
            panel.extend_client_date(v2ray_client.get("email"))
            notification_days = int(config.get("NOTIFICATION_TIME"))
            expire_date = datetime.now() + timedelta(expire_days - notification_days)
            scheduler.add_job(send_notification, "date", run_date=expire_date, args=(client, message.chat.id))

            return await message.reply("کانفیگ رایگان شما به مدت یک هفته با موفقیت تمدید شد!")

        else:
            expire_date = datetime.fromtimestamp(int(str(expire_timestamp)[:-3]))
            remaining_days = (expire_date - datetime.now()).days
            return await message.reply(
                f"از اعتبار کانفیگ شما هنوز {remaining_days} روز دیگر باقیست! لطفا بعد تمام شدن اعتبار اقدام به دریافت مجدد کنید!")


@Client.on_message(filters.private & filters.command("کانفیگ من", prefixes=""))
async def my_config_handler(client: Client, message: Message):
    panel = V2ray(config.get("PANEL_USERNAME"), config.get("PANEL_PASSWORD"))
    v2ray_client = panel.get_client(str(message.from_user.id))
    if not v2ray_client:
        return await message.reply("شما در حال حاضر هیچ کانفیگی دریافت نکرده اید!")

    else:
        expire_date = datetime.fromtimestamp(int(str(v2ray_client["expiryTime"])[:-3]))
        expire_date = jalali.GregorianToJalali(expire_date.year, expire_date.month, expire_date.day)
        email = v2ray_client['email']
        v2ray_config = panel.generate_config(email, config.get('V2RAY_PROTOCOL'))

        text = (f"نام کاربری: {email}"
                "\n"
                f"تاریخ انقضا: {expire_date.jyear}/{expire_date.jmonth}/{expire_date.jday}"
                "\n"
                f"کانفیگ: `{v2ray_config}`")

        return await message.reply(text)


@Client.on_message(filters.private & filters.command("پشتیبانی", prefixes=""))
async def support_handler(client: Client, message: Message):
    text = f"جهت هرگونه سوال یا مشکل به این ایدی مراجعه فرمایین: {config.get('ADMIN')}"
    return await message.reply(text)
