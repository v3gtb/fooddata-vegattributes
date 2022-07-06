from abc import abstractmethod, ABCMeta
from dataclasses import dataclass
from typing import (
  Callable,
  Generic,
  Iterable,
  Sequence,
  TypeVar,
)

from ..close_on_exit import CloseOnExit


T = TypeVar("T")  # JSONable

@dataclass
class IndexSpec(Generic[T]):
  name: str
  func: Callable[[T], str]

  @classmethod
  def from_dict_key(cls, name):
    return cls(name, lambda x: x[name])

class AbstractIndexedJsonableStore(Generic[T], CloseOnExit, metaclass=ABCMeta):
  primary_index: IndexSpec
  secondary_indices: Sequence[IndexSpec]

  @abstractmethod
  def close(self): ...

  @abstractmethod
  def put_entries(self, entries: Iterable[T]): ...

  @abstractmethod
  def get_entry(self, index_name: str, index_value: str) -> T: ...

  @abstractmethod
  def iter_entries(
    self, index_name: str, index_value: str
  ) -> Iterable[bytes]: ...

  @abstractmethod
  def iter_index(self, index_name: str) -> Iterable[str]: ...
