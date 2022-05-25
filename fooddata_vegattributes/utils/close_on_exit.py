from abc import abstractmethod
from contextlib import AbstractContextManager


class CloseOnExit(AbstractContextManager):
  """
  Mixin
  """
  @abstractmethod
  def close(self): ...

  def __exit__(self, *args, **kwargs):
    self.close()
