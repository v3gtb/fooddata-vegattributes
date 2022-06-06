from collections import defaultdict
from zipfile import ZipFile
from typing import Dict, Generic, Iterable, Tuple


from .abstract_indexed_json import Links, LinksForSourceIndexName
from .compressed_indexed_json import CompressedIndexedJson, T

class CachingCompressedIndexedJson(CompressedIndexedJson, Generic[T]):
  def __init__(self, zipfile: ZipFile):
    super().__init__(zipfile)

    # caches:
    self._links: Links = {}
    self._jsonables: Dict[str, Dict[str, T]] = defaultdict(lambda: {})

  def write_jsonables(
    self, index_name: str, index_values_and_jsonables: Iterable[Tuple[str, T]]
  ):
    super().write_jsonables(index_name, index_values_and_jsonables)
    self._jsonables[index_name].update(index_values_and_jsonables)

  def _get_jsonable_no_resolve(self, index_name: str, index_value: str) -> T:
    if index_value in self._jsonables[index_name]:
      return self._jsonables[index_name][index_value]
    jsonable = super()._get_jsonable_no_resolve(index_name, index_value)
    self._jsonables[index_name][index_value] = jsonable
    return jsonable

  def _iter_data_index(self, index_name: str) -> Iterable[str]:
    if index_name in self._jsonables:
      return self._jsonables[index_name].keys()
    return super()._iter_data_index(index_name)

  def _is_data_index(self, index_name: str) -> bool:
    if index_name in self._jsonables:
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

  def _write_links(
    self,
    index_name: str,
    links_for_index: LinksForSourceIndexName,
  ):
    super()._write_links(index_name, links_for_index)
    self._links[index_name] = links_for_index
