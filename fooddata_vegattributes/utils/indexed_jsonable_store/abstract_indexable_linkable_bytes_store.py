from abc import ABCMeta, abstractmethod
from typing import Dict, Iterable, List, Tuple

from ..close_on_exit import CloseOnExit


# links are (confusingly) 1-to-n; should probably be named tags or secondary
# indices or something like that
LinkTargets = List[Tuple[str, str]]  # TODO rename
LinksForSourceIndexName = Dict[str, LinkTargets]
Links = Dict[str, LinksForSourceIndexName]

class AbstractIndexableLinkableBytesStore(
  CloseOnExit, metaclass=ABCMeta
):
  @abstractmethod
  def close(self): ...

  @abstractmethod
  def put_entries(
    self, index_name: str, index_values_and_data: Iterable[Tuple[str, bytes]]
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
  def get_entry(self, index_name: str, index_value: str) -> bytes: ...

  @abstractmethod
  def iter_entries(
    self, index_name: str, index_value: str
  ) -> Iterable[bytes]: ...

  @abstractmethod
  def iter_index(self, index_name: str) -> Iterable[str]: ...
