import pytest

from fooddata_vegattributes.utils.compressed_indexed_json import (
  CompressedIndexedJson
)


def test_index_not_present(tmp_path):
  path = tmp_path/"compressed_indexed_json.jsons.zip"
  with CompressedIndexedJson.from_path(path, mode="w") as cij:
    cij.write_index_jsonable_tuples(index_jsonable_tuples=[])
  with CompressedIndexedJson.from_path(path) as cij:
    with pytest.raises(
      KeyError,
      match="Entry with key .* not in indexed JSON file"
    ):
      cij.get_jsonable_by_index("123")
