from uuid import uuid4

from django.db.models import (CASCADE, BooleanField, CharField, ForeignKey,
                              IntegerField, Model, UUIDField)


class Album(Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    title = CharField(max_length=100)
    genre = CharField(
        choices=(('POP', 'Pop'), ('ROCK', 'Rock')),
        max_length=10
    )
    year = IntegerField()
    released = BooleanField()


class Song(Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    album = ForeignKey(Album, on_delete=CASCADE)

    title = CharField(max_length=100)
    length = IntegerField()
