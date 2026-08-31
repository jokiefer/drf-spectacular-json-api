from django.test.testcases import SimpleTestCase

from drf_spectacular_jsonapi.schemas.utils import get_serializer_pk_field_name
from tests.serializers import SongSerializer, SpecialSongSerializer


class TestUtils(SimpleTestCase):

    def test_get_serializer_pk_field_name_model_inheritance(self):
        pk_field_name = get_serializer_pk_field_name(
            serializer=SpecialSongSerializer())

        self.assertEqual("id", pk_field_name)

    def test_get_serializer_pk_field_name(self):
        pk_field_name = get_serializer_pk_field_name(
            serializer=SongSerializer())

        self.assertEqual("id", pk_field_name)
