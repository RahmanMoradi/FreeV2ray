import asyncio
import peewee
import peewee_async

database = peewee_async.MySQLDatabase('test')
database.set_allow_sync(False)

objects = peewee_async.Manager(database)


class BaseModel(peewee.Model):
    class Meta:
        database = database


class User(BaseModel):
    id = peewee.PrimaryKeyField()
    chat_id = peewee.IntegerField(unique=True)
    created_at = peewee.DateTimeField()

    


if __name__ == '__main__':
    async def setup():
        ...


    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup())
    loop.close()
