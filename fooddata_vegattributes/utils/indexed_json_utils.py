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


T = TypeVar("T")

@dataclass
class IndexSpec(Generic[T]):
  name: str
  func: Callable[[T], str]

class IndexingIterator(Generic[T]):
  def __init__(
    self,
    elements: Iterable[T],
    primary_index: IndexSpec,
    secondary_indices: Sequence[IndexSpec],
  ):
    self.elements = elements
    self.primary_index = primary_index
    self.secondary_indices = secondary_indices
    # note that this is explicitly part of the public interface:
    self.secondary_maps: Mapping[str, Mapping[str, MutableSequence[str]]] = {
      s.name: defaultdict(lambda: []) for s in self.secondary_indices
    }

  def __iter__(self) -> Generator[Tuple[str, T], None, None]:
    for element in self.elements:
      primary = self.primary_index.func(element)
      for secondary in self.secondary_indices:
        self.secondary_maps[secondary.name][secondary.func(element)].append(
          primary
        )
      yield primary, element
