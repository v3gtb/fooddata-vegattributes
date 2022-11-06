import json
from os import PathLike
from typing import Iterable, Generic, Tuple, Union

from ..close_via_stack import CloseViaStack

from .abstract_indexable_linkable_bytes_store import (
  AbstractIndexableLinkableBytesStore
)
from .abstract_indexable_linkable_jsonable_store import (
  AbstractIndexableLinkableJsonableStore, LinkTargets, T
)
from .caching_zipped_indexable_linkable_bytes_store import (
  CachingZippedIndexableLinkableBytesStore
)
from .zipped_indexable_linkable_bytes_store import (
  ZippedIndexableLinkableBytesStore, ZIP_DEFLATED
)


class ZippedIndexableLinkableJsonableStore(
  CloseViaStack, AbstractIndexableLinkableJsonableStore, Generic[T]
):
  def __init__(self, bytes_store: AbstractIndexableLinkableBytesStore):
    self.bytes_store = bytes_store

  @classmethod
  def from_path(
    cls,
    path: Union[PathLike, str, bytes],
    mode="r",
    compression=ZIP_DEFLATED,
    compresslevel=None,
    caching=True,
  ) -> "ZippedIndexableLinkableJsonableStore":
    """
    Opens store for reading or writing depending on the given mode.
    """
    bytes_store_cls = (
      CachingZippedIndexableLinkableBytesStore if caching
      else ZippedIndexableLinkableBytesStore
    )
    bytes_store = bytes_store_cls.from_path(
      path,
      mode=mode,
      compression=compression,
      compresslevel=compresslevel,
    )
    obj = cls(bytes_store=bytes_store)
    obj.close_stack.enter_context(bytes_store)
    return obj

  def put_entries(
    self, index_name: str, index_values_and_data: Iterable[Tuple[str, T]]
  ):
    self.bytes_store.put_entries(
      index_name,
      (
        (index_value, json.dumps(jsonable).encode("utf-8"))
        for index_value, jsonable in index_values_and_data
      )
    )

  def put_links(
    self,
    index_name: str,
    index_values_and_targets: Iterable[Tuple[str, LinkTargets]],
  ):
    """
    Targets have the semantics `(target_index_name, target_index_value)`.
    """
    self.bytes_store.put_links(index_name, index_values_and_targets)

  def get_entry(self, index_name: str, index_value: str) -> T:
    entry_bytes = self.bytes_store.get_entry(index_name, index_value)
    return json.loads(entry_bytes)

  def iter_entries(
    self, index_name: str, index_value: str
  ) -> Iterable[bytes]:
    return (
      json.loads(entry_bytes)
      for entry_bytes in self.bytes_store.iter_entries(index_name, index_value)
    )

  def iter_index(self, index_name: str) -> Iterable[str]:
    return self.bytes_store.iter_index(index_name)
