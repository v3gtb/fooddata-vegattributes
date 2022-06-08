from abc import ABCMeta, abstractmethod
from contextlib import AbstractContextManager
from typing import Iterable, Mapping

from .food import Food


class AbstractFoodStore(AbstractContextManager, metaclass=ABCMeta):
  @abstractmethod
  def get_mapped_by_fdc_ids(
    self, fdc_ids: Iterable[int]
  ) -> Mapping[int, Food]: ...

  @abstractmethod
  def get_by_fdc_id(self, fdc_id: int) -> Food: ...

  @abstractmethod
  def get_by_ingredient_code(self, ingredient_code: int) -> Food: ...

  @abstractmethod
  def get_all_fdc_ids(self) -> Iterable[int]: ...

  @abstractmethod
  def get_mapped_by_fdc_category(
    self, fdc_category_description: str
  ) -> Mapping[int, Food]: ...
