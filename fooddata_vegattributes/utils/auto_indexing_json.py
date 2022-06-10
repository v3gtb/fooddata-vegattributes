from collections import defaultdict
from dataclasses import dataclass
from typing import (
  Callable,
  Generator,
  Generic,
  Iterable,
  Mapping,
  MutableSequence,
  Sequence,
  Tuple,
  TypeVar,
)

from .abstract_indexed_json import AbstractIndexedJson


T = TypeVar("T")

@dataclass
class IndexSpec(Generic[T]):
  name: str
  func: Callable[[T], str]

class AutoIndexingJsonableWriter(Generic[T]):
  def __init__(
    self,
    indexed_json: AbstractIndexedJson,
    primary_index: IndexSpec,
    secondary_indices: Sequence[IndexSpec],
  ):
    self.indexed_json = indexed_json
    self.primary_index = primary_index
    self.secondary_indices = secondary_indices
    # note that this is explicitly part of the public interface:
    self.secondary_maps: Mapping[str, Mapping[str, MutableSequence[str]]] = {
      s.name: defaultdict(lambda: []) for s in self.secondary_indices
    }

  def write_jsonables(self, jsonables: Iterable[T]):
    self.indexed_json.write_jsonables(
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
      self.indexed_json.write_links(
        name,
        (
          (k, [(self.primary_index.name, target) for target in targets])
          for k, targets in map.items()
        ),
      )
