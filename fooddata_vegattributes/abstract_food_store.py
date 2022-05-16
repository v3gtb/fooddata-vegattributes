from abc import ABCMeta, abstractmethod
from contextlib import AbstractContextManager
from typing import Iterable, Mapping

from .food import Food


class AbstractFoodStore(AbstractContextManager, metaclass=ABCMeta):
  @abstractmethod
  def get_mapped_by_fdc_ids(
    self, fdc_ids: Iterable[int]
  ) -> Mapping[int, Food]:
    pass

  @abstractmethod
  def get_all_fdc_ids(self) -> Iterable[int]:
    pass
