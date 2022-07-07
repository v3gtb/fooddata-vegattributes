from abc import ABCMeta, abstractmethod
from typing import Iterable, Union

from .fooddata import FoodDataDict
from .utils.indexed_jsonable_store import AbstractIndexedJsonableStore
from .utils.close_on_exit import CloseOnExit


class AbstractIndexedFoodDataJson(CloseOnExit, metaclass=ABCMeta):
  indexed_json: AbstractIndexedJsonableStore

  @abstractmethod
  def close(self): ...

  def write_fooddata_dicts(self, ds: Iterable[FoodDataDict]):
    self.indexed_json.put_entries(ds)

  def get_fooddata_dict_by_fdc_id(
    self, fdc_id: Union[int, str]
  ) -> FoodDataDict:
    return self.indexed_json.get_entry("fdc-id", str(fdc_id))

  def get_fooddata_dict_by_ingredient_code(
    self, ingredient_code: Union[int, str]
  ) -> FoodDataDict:
    return self.indexed_json.get_entry(
      "ingredient-code", str(ingredient_code)
    )

  def get_all_fdc_ids(self) -> Iterable[int]:
    return [int(x) for x in self.indexed_json.iter_index("fdc-id")]

  def get_fooddata_dicts_by_fdc_category(
    self, fdc_category_description: str
  ) -> Iterable[FoodDataDict]:
    return self.indexed_json.iter_entries(
      "fdc-category-description", fdc_category_description
    )
