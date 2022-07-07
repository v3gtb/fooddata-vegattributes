from abc import ABCMeta, abstractmethod
from typing import Generic, Iterable, Tuple, TypeVar

from ..close_on_exit import CloseOnExit

from .abstract_indexable_linkable_bytes_store import (
  LinkTargets
)


T = TypeVar("T")  # JSONable

class AbstractIndexableLinkableJsonableStore(
  Generic[T], CloseOnExit, metaclass=ABCMeta
):
  @abstractmethod
  def close(self): ...

  @abstractmethod
  def put_entries(
    self, index_name: str, index_values_and_data: Iterable[Tuple[str, T]]
  ): ...

  @abstractmethod
  def put_links(
    self,
    index_name: str,
    index_values_and_targets: Iterable[Tuple[str, LinkTargets]],
  ):
    """
    Targets have the semantics `(target_index_name, target_index_value)`.
    """
    ...

  @abstractmethod
  def get_entry(self, index_name: str, index_value: str) -> T: ...

  @abstractmethod
  def iter_entries(
    self, index_name: str, index_value: str
  ) -> Iterable[bytes]: ...

  @abstractmethod
  def iter_index(self, index_name: str) -> Iterable[str]: ...
