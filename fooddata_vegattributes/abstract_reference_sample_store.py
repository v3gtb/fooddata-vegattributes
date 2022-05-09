from abc import ABCMeta, abstractmethod
from contextlib import AbstractContextManager
from typing import List

from .reference_sample import ReferenceSample


class AbstractReferenceSampleStore(AbstractContextManager, metaclass=ABCMeta):
  @abstractmethod
  def get_all(self) -> List[ReferenceSample]:
    pass

  @abstractmethod
  def reset_and_put_all(self, reference_samples: List[ReferenceSample]):
    pass