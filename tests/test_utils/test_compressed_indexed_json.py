import pytest

from fooddata_vegattributes.utils.compressed_indexed_json import (
  CompressedIndexedJson
)


def test_index_not_present(tmp_path):
  path = tmp_path/"compressed_indexed_json.jsons.zip"
  with CompressedIndexedJson.from_path(path, mode="w") as cij:
    cij.write_jsonables("fdc-id", [])
  with CompressedIndexedJson.from_path(path) as cij:
    with pytest.raises(
      KeyError,
      match="Entry for .* not in indexed JSON file"
    ):
      cij.get_jsonable("fdc-id", "123")
