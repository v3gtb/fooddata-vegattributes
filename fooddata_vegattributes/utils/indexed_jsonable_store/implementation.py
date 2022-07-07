from collections import defaultdict
from os import PathLike
from typing import (
  Generator,
  Generic,
  Iterable,
  Mapping,
  MutableSequence,
  Sequence,
  Tuple,
  TypeVar,
  Union,
)

from ..close_via_stack import CloseViaStack
from .abstract import (
  AbstractIndexedJsonableStore,
  IndexSpec,
)
from .abstract_indexable_linkable_jsonable_store import (
  AbstractIndexableLinkableJsonableStore,
)
from .zipped_indexable_linkable_jsonable_store import (
  ZippedIndexableLinkableJsonableStore,
  ZIP_DEFLATED,
)


T = TypeVar("T")

class AutoIndexingJsonableWriter(Generic[T]):
  def __init__(
    self,
    jsonable_store: AbstractIndexableLinkableJsonableStore,
    primary_index: IndexSpec,
    secondary_indices: Sequence[IndexSpec],
  ):
    self.jsonable_store = jsonable_store
    self.primary_index = primary_index
    self.secondary_indices = secondary_indices
    # note that this is explicitly part of the public interface:
    self.secondary_maps: Mapping[str, Mapping[str, MutableSequence[str]]] = {
      s.name: defaultdict(lambda: []) for s in self.secondary_indices
    }

  def put_entries(self, jsonables: Iterable[T]):
    self.jsonable_store.put_entries(
      self.primary_index.name, self._iter_primary_indexed_jsonables(jsonables)
    )
    self._write_secondary_indices()

  def _iter_primary_indexed_jsonables(
    self, jsonables: Iterable[T]
  ) -> Generator[Tuple[str, T], None, None]:
    for jsonable in jsonables:
      primary = self.primary_index.func(jsonable)
      for secondary in self.secondary_indices:
        self.secondary_maps[secondary.name][secondary.func(jsonable)].append(
          primary
        )
      yield primary, jsonable

  def _write_secondary_indices(self):
    for name, map in self.secondary_maps.items():
      self.jsonable_store.put_links(
        name,
        (
          (k, [(self.primary_index.name, target) for target in targets])
          for k, targets in map.items()
        ),
      )


class IndexedJsonableStore(
  CloseViaStack, AbstractIndexedJsonableStore, Generic[T],
):
  def __init__(
    self,
    indexable_jsonable_store: AbstractIndexableLinkableJsonableStore[T],
    primary_index: IndexSpec,
    secondary_indices: Sequence[IndexSpec]
  ):
    self.indexable_jsonable_store = indexable_jsonable_store
    self.auto_indexing_writer: AutoIndexingJsonableWriter[T] = (
      AutoIndexingJsonableWriter(
        indexable_jsonable_store,
        primary_index,
        secondary_indices,
      )
    )

  @classmethod
  def from_path(
    cls,
    path: Union[PathLike, str, bytes],
    primary_index: IndexSpec[T],
    secondary_indices: Sequence[IndexSpec[T]],
    mode="r",
    compression=ZIP_DEFLATED,
    compresslevel=None,
    caching=True,
  ):
    indexable_store = ZippedIndexableLinkableJsonableStore.from_path(
      path=path,
      mode=mode,
      compression=compression,
      compresslevel=compresslevel,
      caching=caching,
    )
    obj = cls(indexable_store, primary_index, secondary_indices)
    obj.close_stack.enter_context(indexable_store)
    return obj

  def put_entries(self, entries: Iterable[T]):
    self.auto_indexing_writer.put_entries(entries)

  def get_entry(self, index_name: str, index_value: str) -> T:
    return self.indexable_jsonable_store.get_entry(index_name, index_value)

  def iter_entries(
    self, index_name: str, index_value: str
  ) -> Iterable[bytes]:
    return self.indexable_jsonable_store.iter_entries(index_name, index_value)

  def iter_index(self, index_name: str) -> Iterable[str]:
    return self.indexable_jsonable_store.iter_index(index_name)
