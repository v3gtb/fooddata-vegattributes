from pathlib import Path
from typing import Any, Dict, List

import pytest

from fooddata_vegattributes.utils.indexed_jsonable_store import (
  IndexedJsonableStore, IndexSpec
)


@pytest.fixture()
def sample_entries() -> List[Dict[str, Any]]:
  return [
    {
      "id": "1",
      "name": "Harold",
      "profession": "Accountant",
    },
    {
      "id": "2",
      "name": "Olivia",
      "profession": "Accountant",
    },
    {
      "id": "3",
      "name": "Matthew",
      "profession": "Former child",
    },
  ]

@pytest.mark.parametrize("caching", [True, False])
def test_write_and_read_entries_and_links(
  sample_entries: List[Dict[str, Any]], tmp_path: Path, caching: bool
):
  path = tmp_path/"store.zip"
  with IndexedJsonableStore.from_path(
    path,
    primary_index=IndexSpec.from_dict_key("id"),
    secondary_indices=[IndexSpec.from_dict_key("profession")],
    mode="w",
    caching=caching,
  ) as store:
    # test with generator to ensure compatibility with iterables (=> no double
    # iterations)
    store.put_entries(x for x in sample_entries)
    # test reading back without re-opening
    assert store.get_entry("id", "1")["name"] == "Harold"
    assert store.get_entry("id", "2")["name"] == "Olivia"
  # test reading back after re-opening
  with IndexedJsonableStore.from_path(
    path,
    primary_index=IndexSpec.from_dict_key("id"),
    secondary_indices=[IndexSpec.from_dict_key("profession")],
    mode="r",
    caching=caching,
  ) as store:
    assert store.get_entry("id", "1")["name"] == "Harold"
    assert store.get_entry("id", "2")["name"] == "Olivia"
    # test automatic links
    assert sorted(
      x["name"] for x in store.iter_entries("profession", "Accountant")
    ) == ["Harold", "Olivia"]
    # test nonexistent indices
    with pytest.raises(
      KeyError,
      match="Entry for .* not in indexed JSON file"
    ):
      store.get_entry("id", "123")
