from contextlib import ExitStack
from dataclasses import dataclass, field
from os import PathLike
from typing import Iterable, Mapping, Union

from .abstract_food_store import AbstractFoodStore
from .food import Food
from .indexed_fooddata import CompressedIndexedFoodDataJson


@dataclass
class IndexedFoodDataFoodStore(AbstractFoodStore):
  indexed_fooddata_json: CompressedIndexedFoodDataJson
  close_stack: ExitStack = field(init=False, default_factory=ExitStack)

  @classmethod
  def from_path(
    cls, path: Union[PathLike, str, bytes], mode="r",
  ) -> "IndexedFoodDataFoodStore":
    indexed_fooddata_json = CompressedIndexedFoodDataJson.from_path(path, mode)
    obj = cls(indexed_fooddata_json=indexed_fooddata_json)
    obj.close_stack.enter_context(indexed_fooddata_json)
    return obj

  def close(self):
    self.close_stack.close()

  def __enter__(self):
    return self

  def __exit__(self, *args, **kwargs):
    self.close()

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
