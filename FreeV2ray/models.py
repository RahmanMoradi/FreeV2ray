import asyncio
import peewee
import peewee_async

database = peewee_async.MySQLDatabase('test')
database.set_allow_sync(False)

objects = peewee_async.Manager(database)


class BaseModel(peewee.Model):
    class Meta:
        database = database


class V2rayConfig(BaseModel):
    id = peewee.PrimaryKeyField()
    add = peewee.CharField(max_length=255),
    host = peewee.CharField(max_length=255),
    uuid = peewee.CharField(max_length=255),
    path = peewee.CharField(max_length=255),
    port = peewee.CharField(max_length=7),
    ps = peewee.CharField(max_length=255),
    sni = peewee.CharField(max_length=255),


class User(BaseModel):
    id = peewee.PrimaryKeyField()
    v2ray_config = peewee.ForeignKeyField(V2rayConfig, null=True, default=None)
    chat_id = peewee.IntegerField(unique=True)
    created_at = peewee.DateTimeField()


if __name__ == '__main__':
    async def setup():
        ...


    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup())
    loop.close()
