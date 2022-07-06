from collections import defaultdict
from typing import Dict, Iterable, Set, Tuple

from .abstract_indexable_linkable_bytes_store import (
  Links,
  LinksForSourceIndexName,
  LinkTargets,
)
from .zipped_indexable_linkable_bytes_store import (
  ZipFile,
  ZippedIndexableLinkableBytesStore,
)


class CachingZippedIndexableLinkableBytesStore(
  ZippedIndexableLinkableBytesStore
):
  def __init__(self, zipfile: ZipFile):
    super().__init__(zipfile)

    # caches:
    self._links: Links = defaultdict(lambda: {})
    self._data: Dict[str, Dict[str, bytes]] = defaultdict(lambda: {})
    # these are also keys in _data, but as you can load index values without
    # loading contents, we need a separate cache:
    self._data_index_values: Dict[str, Set] = defaultdict(lambda: set())
    self._data_index_values_is_complete: Dict[str, bool] = defaultdict(
      lambda: False
    )

  def put_entries(
    self, index_name: str, index_values_and_data: Iterable[Tuple[str, bytes]]
  ):
    # iterables don't have to be re-entrant (and in this case actually aren't)
    # TODO better way?
    index_values_and_data = list(index_values_and_data)
    super().put_entries(index_name, index_values_and_data)
    self._data[index_name].update(index_values_and_data)
    self._data_index_values[index_name].update(
      k for k, v in index_values_and_data
    )

  def _get_entry_no_resolve(self, index_name: str, index_value: str) -> bytes:
    if index_value in self._data[index_name]:
      return self._data[index_name][index_value]
    entry_bytes = super()._get_entry_no_resolve(index_name, index_value)
    self._data[index_name][index_value] = entry_bytes
    self._data_index_values[index_name].add(index_value)
    return entry_bytes

  def _iter_data_index(self, index_name: str) -> Iterable[str]:
    if self._data_index_values_is_complete[index_name]:
      for index_value in self._data_index_values[index_name]:
        yield index_value
    else:
      for index_value in super()._iter_data_index(index_name):
        yield index_value
        self._data_index_values[index_name].add(index_value)
      self._data_index_values_is_complete[index_name] = True

  def _is_data_index(self, index_name: str) -> bool:
    if index_name in self._data or index_name in self._data_index_values:
      return True
    return super()._is_data_index(index_name)

  def _is_link_index(self, index_name: str) -> bool:
    if index_name in self._links:
      return True
    return super()._is_link_index(index_name)

  def _load_links(self, index_name: str) -> LinksForSourceIndexName:
    if index_name not in self._links:
      self._links[index_name] = super()._load_links(index_name)
    return self._links[index_name]

  def put_links(
    self,
    index_name: str,
    index_values_and_targets: Iterable[Tuple[str, LinkTargets]],
  ):
    """
    Targets have the semantics `(target_index_name, target_index_value)`.
    """
    # see comment above
    index_values_and_targets = list(index_values_and_targets)
    super().put_links(index_name, index_values_and_targets)
    self._links[index_name].update(index_values_and_targets)
