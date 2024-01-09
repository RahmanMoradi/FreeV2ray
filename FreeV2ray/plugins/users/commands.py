from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    ReplyKeyboardMarkup,
)
from pyrogram.errors import UserNotParticipant
from pyromod import listen, ikb

from FreeV2ray.app import config, scheduler
from FreeV2ray.models import add_user
from FreeV2ray.v2ray.api import V2ray

from datetime import datetime, timedelta
from jdatetime import jalali


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
async def start_handler(client: Client, message: Message, text=None):
    if not text:
        await add_user(message.from_user.id)
        text = "با سلام به ربات دریافت v2ray شخصی رایگان خوش امدید!"

    message = await message.chat.ask(
        text,
        reply_markup=ReplyKeyboardMarkup([
            ["دریافت کانفیگ"],
            ["پشتیبانی", "کانفیگ من"],
        ], resize_keyboard=True)
    )

    commands = {
        "دریافت کانفیگ": get_config_handler,
        "کانفیگ من": my_config_handler,
        "پشتیبانی": support_handler,
    }

    # if message.text == "/all":
    #     return message.continue_propagation()

    command = commands.get(message.text)

    if command:
        await command(client, message)
    else:
        await message.reply("دستور نامعتبر! لطفا دوباره امتجان کنید:")
        return await start_handler(client, message)


async def get_config_handler(client: Client, message: Message):
    panel = V2ray(config.get("PANEL_USERNAME"), config.get("PANEL_PASSWORD"))
    v2ray_config, created = panel.get_or_create_client(str(message.from_user.id))
    if created:
        expire_days = int(config.get("EXPIRE_TIME"))
        notification_days = int(config.get("NOTIFICATION_TIME"))
        expire_date = datetime.now() + timedelta(expire_days - notification_days)
        job = scheduler.add_job(send_notification, "date", run_date=expire_date, args=(client, message.chat.id))

        return await start_handler(client, message,
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

            expire_days = int(config.get("EXPIRE_TIME"))
            notification_days = int(config.get("NOTIFICATION_TIME"))
            expire_date = datetime.now() + timedelta(expire_days - notification_days)
            job = scheduler.add_job(send_notification, "date", run_date=expire_date, args=(client, message.chat.id))

            return await start_handler(
                client, message,"کانفیگ رایگان شما به مدت یک هفته با موفقیت تمدید شد!")

        else:
            expire_date = datetime.fromtimestamp(int(str(expire_timestamp)[:-3]))
            remaining_days = (expire_date - datetime.now()).days
            await start_handler(
                client, message, f"از اعتبار کانفیگ شما هنوز {remaining_days} روز دیگر باقیست! لطفا بعد تمام شدن اعتبار اقدام به دریافت مجدد کنید!")


async def my_config_handler(client: Client, message: Message):
    panel = V2ray(config.get("PANEL_USERNAME"), config.get("PANEL_PASSWORD"))
    client = panel.get_client(str(message.from_user.id))
    if not client:
        text = "شما در حال حاضر هیچ کانفیگی دریافت نکرده اید!"
        return await start_handler(client, message, text=text)
    else:
        expire_date = datetime.fromtimestamp(int(str(client["expiryTime"])[:-3]))
        expire_date = jalali.GregorianToJalali(expire_date.year, expire_date.month, expire_date.day)
        email = client['email']
        v2ray_config = panel.generate_config(email, config.get('V2RAY_PROTOCOL'))

        text = (f"نام کاربری: {email}"
                "\n"
                f"تاریخ انقضا: {expire_date.jyear}/{expire_date.jmonth}/{expire_date.jday}"
                "\n"
                f"کانفیگ: `{v2ray_config}`")

        return await start_handler(client, message, text=text)


async def support_handler(client: Client, message: Message):
    text = f"جهت هرگونه سوال یا مشکل به این ایدی مراجعه فرمایین: {config.get('ADMIN')}"
    return await start_handler(client, message, text)
