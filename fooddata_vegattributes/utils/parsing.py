import re

class MaxiMunchTokenFinder:
  def __init__(self, tokens):
    self.regex = re.compile(
      "("
      +
      "|".join(
        re.escape(token) for token in sorted(tokens, key=len, reverse=True)
      )
      +
      ")"
    )

  def find_all(self, s: str):
    return self.regex.findall(s)
