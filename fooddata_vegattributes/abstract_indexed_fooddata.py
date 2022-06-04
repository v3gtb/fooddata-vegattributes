from abc import ABCMeta, abstractmethod
from typing import Iterable, Union

from .fooddata import FoodDataDict
from .utils.abstract_indexed_json import AbstractIndexedJson
from .utils.close_on_exit import CloseOnExit


class AbstractIndexedFoodDataJson(CloseOnExit, metaclass=ABCMeta):
  indexed_json: AbstractIndexedJson

  @abstractmethod
  def close(self): ...

  def write_fooddata_dicts(self, ds: Iterable[FoodDataDict]):
    self.indexed_json.write_jsonables(
      "fdc-id",
      ((str(d["fdcId"]), d) for d in ds),
    )
    self.indexed_json.write_links(
      "ingredient-code",
      (
        (str(optional_ingredient_code_any_type), ("fdc-id", str(fdc_id)))
        for optional_ingredient_code_any_type, fdc_id in (
          # TODO as mentioned elsewhere, split up into Survey/SR Legacy funcs
          ((d.get("foodCode") or d.get("ndbNumber")), d["fdcId"]) for d in ds
        )
        if optional_ingredient_code_any_type is not None
      ),
    )

  def get_fooddata_dict_by_fdc_id(
    self, fdc_id: Union[int, str]
  ) -> FoodDataDict:
    return self.indexed_json.get_jsonable("fdc-id", str(fdc_id))

  def get_fooddata_dict_by_ingredient_code(
    self, ingredient_code: Union[int, str]
  ) -> FoodDataDict:
    return self.indexed_json.get_jsonable(
      "ingredient-code", str(ingredient_code)
    )

  def get_all_fdc_ids(self) -> Iterable[int]:
    return [int(x) for x in self.indexed_json.iter_index("fdc-id")]
