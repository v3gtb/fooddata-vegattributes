from abc import ABCMeta, abstractmethod
from typing import Iterable, Union

from .fooddata import FoodDataDict
from .utils.abstract_indexed_json import AbstractIndexedJson
from .utils.close_on_exit import CloseOnExit
from .utils.indexed_json_utils import IndexingIterator, IndexSpec


class AbstractIndexedFoodDataJson(CloseOnExit, metaclass=ABCMeta):
  indexed_json: AbstractIndexedJson

  @abstractmethod
  def close(self): ...

  def write_fooddata_dicts(self, ds: Iterable[FoodDataDict]):
    indexed_ds = IndexingIterator(
      elements=ds,
      primary_index=IndexSpec("fdc-id", lambda d: str(d["fdcId"])),
      secondary_indices=[
        IndexSpec(
          "ingredient-code",
          lambda d: str(d.get("foodCode") or d.get("ndbNumber")),
        ),
        IndexSpec(
          "fdc-category-description",
          lambda d: (
            d.get("wweiaFoodCategory", {}).get("wweiaFoodCategoryDescription")
            or d.get("foodCategory", {}).get("description")
          ),
        ),
      ]
    )
    self.indexed_json.write_jsonables(
      indexed_ds.primary_index.name, indexed_ds
    )
    for name, map in indexed_ds.secondary_maps.items():
      self.indexed_json.write_links(
        name,
        (
          (k, [(indexed_ds.primary_index.name, target) for target in targets])
          for k, targets in map.items()
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

  def get_fooddata_dicts_by_fdc_category(
    self, fdc_category_description: str
  ) -> Iterable[FoodDataDict]:
    return self.indexed_json.get_jsonables(
      "fdc-category-description", fdc_category_description
    )
