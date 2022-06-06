from abc import ABCMeta, abstractmethod
from typing import Dict, Generic, Iterable, List, Tuple, TypeVar

from .close_on_exit import CloseOnExit


T = TypeVar("T")

# links are (confusingly) 1-to-n; should probably be named tags or secondary
# indices or something like that
LinkTargets = List[Tuple[str, str]]  # TODO rename
LinksForSourceIndexName = Dict[str, LinkTargets]
Links = Dict[str, LinksForSourceIndexName]

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
    index_values_and_targets: Iterable[Tuple[str, LinkTargets]]
  ):
    """
    Targets have the semantics `(target_index_name, target_index_value)`.
    """
    ...

  @abstractmethod
  def get_jsonable(self, index_name: str, index_value: str) -> T: ...

  @abstractmethod
  def iter_index(self, index_name: str) -> Iterable[str]: ...
