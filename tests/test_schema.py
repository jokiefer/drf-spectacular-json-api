from tests import assert_schema, generate_schema
from tests.viewsets import AlbumViewset


def test_schema(no_warnings):

    assert_schema(
        generate_schema('albums', AlbumViewset),
        'tests/test_data/test_schema.yml'
    )
