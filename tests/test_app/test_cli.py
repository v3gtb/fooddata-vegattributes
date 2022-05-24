import pytest
from unittest.mock import patch

from fooddata_vegattributes.app.cli import main


def test_cli_help_doesnt_crash():
  """
  Really stupid test just to guard against the most egregious errors.
  """
  with patch("sys.argv", ["fooddata-vegattributes", "--help"]):
    with pytest.raises(SystemExit) as exc_info:
      main()
    assert exc_info.value.args[0] == 0
