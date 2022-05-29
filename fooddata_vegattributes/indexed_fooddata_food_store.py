from dataclasses import dataclass
from os import PathLike
from typing import Iterable, Mapping, Union

from .abstract_food_store import AbstractFoodStore
from .food import Food
from .compressed_indexed_fooddata import CompressedIndexedFoodDataJson
from .utils.close_on_exit import CloseOnExit
from .utils.close_via_stack import CloseViaStack


@dataclass
class IndexedFoodDataFoodStore(CloseViaStack, AbstractFoodStore, CloseOnExit):
  indexed_fooddata_json: CompressedIndexedFoodDataJson

  @classmethod
  def from_path(
    cls, path: Union[PathLike, str, bytes], mode="r",
  ) -> "IndexedFoodDataFoodStore":
    indexed_fooddata_json = CompressedIndexedFoodDataJson.from_path(path, mode)
    obj = cls(indexed_fooddata_json=indexed_fooddata_json)
    obj.close_stack.enter_context(indexed_fooddata_json)
    return obj

  def get_mapped_by_fdc_ids(
    self, fdc_ids: Iterable[int]
  ) -> Mapping[int, Food]:
    fdc_ids_to_food_ds = {
      fdc_id: self.indexed_fooddata_json.get_fooddata_dict_by_fdc_id(fdc_id)
      for fdc_id in fdc_ids
    }
    return {
     fdc_id: Food.from_fdc_food_dict(food_d)
     for fdc_id, food_d in fdc_ids_to_food_ds.items()
    }

  def get_by_fdc_id(self, fdc_id: int) -> Food:
    return self.get_mapped_by_fdc_ids([fdc_id])[fdc_id]

  def get_all_fdc_ids(self) -> Iterable[int]:
    return self.indexed_fooddata_json.get_all_fdc_ids()
