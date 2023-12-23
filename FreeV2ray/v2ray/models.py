import peewee

database = peewee.SqliteDatabase("cookie.db")


class BaseModel(peewee.Model):
    class Meta:
        database = database


class XuiSession(BaseModel):
    id = peewee.PrimaryKeyField()
    session_string = peewee.CharField(max_length=255)
    created_at = peewee.DateTimeField()


database.create_tables([
    XuiSession,
])
