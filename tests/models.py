from uuid import uuid4

from django.db.models import (CASCADE, BooleanField, CharField, ForeignKey,
                              IntegerField, Model, UUIDField)
from django.utils.translation import gettext_lazy as _

__all__ = [
    'Album',
    'Song'
]


class Album(Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    title = CharField(max_length=100, verbose_name=_(
        "Title"), help_text=_("The title of the Album"))
    genre = CharField(
        choices=(('POP', 'Pop'), ('ROCK', 'Rock')),
        max_length=10,
        verbose_name=_("Genre"),
        help_text=_("Wich kind of genre this Album represents")
    )
    year = IntegerField(verbose_name=_("Year"),
                        help_text=_("The release year"))
    released = BooleanField(verbose_name=_("Released"),
                            help_text=_("Is this Album released or not?"))


class Song(Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)

    title = CharField(max_length=100)
    length = IntegerField()
    album = ForeignKey(
        to=Album,
        related_name="singles",
        related_query_name="single",
        on_delete=CASCADE
    )


class User(Model):

    username = CharField(max_length=50, primary_key=True)
    password = CharField(max_length=128)
