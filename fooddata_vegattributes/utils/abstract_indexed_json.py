from abc import ABCMeta, abstractmethod
from typing import Generic, Iterable, Tuple, TypeVar


T = TypeVar("T")

class AbstractIndexedJson(Generic[T], metaclass=ABCMeta):
  @abstractmethod
  def close(self): ...

  def __enter__(self):
    return self

  def __exit__(self, *args, **kwargs):
    self.close()

  @abstractmethod
  def write_index_jsonable_tuples(
    self, index_jsonable_tuples: Iterable[Tuple[str, T]]
  ): ...

  @abstractmethod
  def get_jsonable_by_index(self, index: str) -> T: ...

  @abstractmethod
  def iter_all_indices(self) -> Iterable[str]: ...
