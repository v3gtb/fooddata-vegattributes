from contextlib import ExitStack
from typing import Optional


class CloseStackOwner:
  """
  Mixin
  """
  # implemented the way it is to avoid having to do __init__() shennanigans
  # (cooperative multiple inheritance and all that)
  _close_stack: Optional[ExitStack] = None

  @property
  def close_stack(self) -> ExitStack:
    if self._close_stack is None:
      self._close_stack = ExitStack()
    return self._close_stack
