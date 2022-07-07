from pathlib import Path
from typing import Dict

import pytest

from fooddata_vegattributes.utils.indexed_jsonable_store \
.caching_zipped_indexable_linkable_bytes_store import (
  CachingZippedIndexableLinkableBytesStore
)


@pytest.fixture()
def sample_entries_by_id() -> Dict[str, bytes]:
  return {"1": b"hello", "2": b"world", "3": b"!"}

def test_write_and_read_entries(
  sample_entries_by_id: Dict[str, bytes], tmp_path: Path
):
  path = tmp_path/"store.zip"
  with (
    CachingZippedIndexableLinkableBytesStore.from_path(path, mode="w")
  ) as store:
    # test with generator to ensure compatibility with iterables (=> no double
    # iterations)
    store.put_entries("id", (x for x in sample_entries_by_id.items()))
    # test reading back without re-opening
    assert store.get_entry("id", "1") == b"hello"
    assert store.get_entry("id", "2") == b"world"
  # test reading back after re-opening
  with (
    CachingZippedIndexableLinkableBytesStore.from_path(path, mode="r")
  ) as store:
    assert store.get_entry("id", "1") == b"hello"
    assert store.get_entry("id", "2") == b"world"
    assert sorted(list(store.iter_index("id"))) == ["1", "2", "3"]

def test_links(
  sample_entries_by_id: Dict[str, bytes], tmp_path: Path
):
  path = tmp_path/"store.zip"
  with (
    CachingZippedIndexableLinkableBytesStore.from_path(path, mode="w")
  ) as store:
    store.put_entries("id", sample_entries_by_id.items())
    category_links = {
      "word": [("id", "1"), ("id", "2")],
      "punctuation": [("id", "3")],
    }
    # test with generator to ensure compatibility with iterables
    store.put_links("category", (x for x in category_links.items()))
  # test reading back after re-opening
  with (
    CachingZippedIndexableLinkableBytesStore.from_path(path, mode="r")
  ) as store:
    words = store.iter_entries("category", "word")
    assert sorted(words) == [b"hello", b"world"]
    assert store.get_entry("category", "punctuation") == b"!"
    categories = list(store.iter_index("category"))
    assert sorted(categories) == ["punctuation", "word"]
