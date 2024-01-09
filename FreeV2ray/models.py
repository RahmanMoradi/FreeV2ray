import asyncio
import peewee

from datetime import datetime

database = peewee.SqliteDatabase("db.sqlite")


class BaseModel(peewee.Model):
    class Meta:
        database = database


# class V2rayConfig(BaseModel):
#     id = peewee.PrimaryKeyField()
#     add = peewee.CharField(max_length=255),
#     host = peewee.CharField(max_length=255),
#     uuid = peewee.CharField(max_length=255),
#     path = peewee.CharField(max_length=255),
#     port = peewee.CharField(max_length=7),
#     ps = peewee.CharField(max_length=255),
#     sni = peewee.CharField(max_length=255),


class User(BaseModel):
    id = peewee.PrimaryKeyField()
    chat_id = peewee.IntegerField(unique=True)
    created_at = peewee.DateTimeField()


async def add_user(user_id: int):
    user, created = User.get_or_create(defaults=dict(chat_id=user_id), created_at=datetime.now())
    return user


if __name__ == '__main__':
    async def setup():
        ...


    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup())
    loop.close()
