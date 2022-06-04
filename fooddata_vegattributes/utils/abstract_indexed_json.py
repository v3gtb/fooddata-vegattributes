from abc import ABCMeta, abstractmethod
from typing import Generic, Iterable, Tuple, TypeVar

from .close_on_exit import CloseOnExit


T = TypeVar("T")

class AbstractIndexedJson(Generic[T], CloseOnExit, metaclass=ABCMeta):
  @abstractmethod
  def close(self): ...

  @abstractmethod
  def write_jsonables(
    self, index_name: str, index_values_and_jsonables: Iterable[Tuple[str, T]]
  ): ...

  @abstractmethod
  def write_links(
    self,
    index_name: str,
    index_values_and_targets: Iterable[Tuple[str, Tuple[str, str]]]
  ):
    """
    Targets have the semantics `(target_index_name, target_index_value)`.
    """
    ...

  @abstractmethod
  def get_jsonable(self, index_name: str, index_value: str) -> T: ...

  @abstractmethod
  def iter_index(self, index_name: str) -> Iterable[str]: ...
