from .close_stack_owner import CloseStackOwner


class CloseViaStack(CloseStackOwner):
  """
  Mixin
  """
  def close(self):
    self.close_stack.close()
