from abc import ABCMeta, abstractmethod
from typing import Generic, Iterable, Tuple, TypeVar

from .close_on_exit import CloseOnExit


T = TypeVar("T")

class AbstractIndexedJson(Generic[T], CloseOnExit, metaclass=ABCMeta):
  @abstractmethod
  def close(self): ...

  @abstractmethod
  def write_index_jsonable_tuples(
    self, index_jsonable_tuples: Iterable[Tuple[str, T]]
  ): ...

  @abstractmethod
  def get_jsonable_by_index(self, index: str) -> T: ...

  @abstractmethod
  def iter_all_indices(self) -> Iterable[str]: ...
