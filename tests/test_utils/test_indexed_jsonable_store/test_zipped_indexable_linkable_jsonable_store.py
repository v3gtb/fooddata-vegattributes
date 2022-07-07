from pathlib import Path
from typing import Any, Dict

import pytest

from fooddata_vegattributes.utils.indexed_jsonable_store \
.zipped_indexable_linkable_jsonable_store import (
  ZippedIndexableLinkableJsonableStore
)


@pytest.fixture()
def sample_entries_by_id() -> Dict[str, Any]:
  return {"1": [1,2,3], "2": "hello", "3": [4, 5]}

@pytest.mark.parametrize("caching", [True, False])
def test_write_and_read_entries(
  sample_entries_by_id: Dict[str, Any], tmp_path: Path, caching: bool
):
  path = tmp_path/"store.zip"
  with ZippedIndexableLinkableJsonableStore.from_path(
    path, mode="w", caching=caching
  ) as store:
    # test with generator to ensure compatibility with iterables (=> no double
    # iterations)
    store.put_entries("id", (x for x in sample_entries_by_id.items()))
    # test reading back without re-opening
    assert store.get_entry("id", "1") == [1,2,3]
    assert store.get_entry("id", "2") == "hello"
  # test reading back after re-opening
  with ZippedIndexableLinkableJsonableStore.from_path(
    path, mode="r", caching=caching
  ) as store:
    assert store.get_entry("id", "1") == [1,2,3]
    assert store.get_entry("id", "2") == "hello"
    assert sorted(list(store.iter_index("id"))) == ["1", "2", "3"]

@pytest.mark.parametrize("caching", [True, False])
def test_links(
  sample_entries_by_id: Dict[str, Any], tmp_path: Path, caching: bool
):
  path = tmp_path/"store.zip"
  with ZippedIndexableLinkableJsonableStore.from_path(
    path, mode="w", caching=caching
  ) as store:
    store.put_entries("id", sample_entries_by_id.items())
    category_links = {
      "numbers": [("id", "1"), ("id", "3")],
      "word": [("id", "2")],
    }
    # test with generator to ensure compatibility with iterables
    store.put_links("category", (x for x in category_links.items()))
  # test reading back after re-opening
  with ZippedIndexableLinkableJsonableStore.from_path(
    path, mode="r", caching=caching
  ) as store:
    numbers = store.iter_entries("category", "numbers")
    assert sorted(numbers) == [[1, 2, 3], [4, 5]]
    assert store.get_entry("category", "word") == "hello"
    categories = list(store.iter_index("category"))
    assert sorted(categories) == ["numbers", "word"]
