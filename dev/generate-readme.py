#!/usr/bin/env python3
"""
Terrible pre-commit hook to generate a README.md from the GH Pages index.md.

Must be run from the project root dir.
"""
from tempfile import TemporaryDirectory
import os
from pathlib import Path
import re
from shutil import move
from subprocess import Popen, PIPE, run

def make_urls_absolute(md_content, base_url):
  return re.sub(r"\]\((?!http)", f"]({base_url}", md_content)

"https://v3gtb.github.io/fooddata-vegattributes/category-lists",

def render_readme_into_file(f):
  # generate category lists & categories TOC
  run(
    ["python3", "./.gh-pages/generate-pages.py"],
    env={'PYTHONPATH': os.getcwd()},
    check=True,
  )

  # template out index.md
  run(r'''(
    cd .gh-pages/content && bundle exec ../../dev/template-out-pages-index.rb
    )''',
    shell=True,
    check=True,
  )

  # filter index.md -> README.md
  proc = Popen(r'''(
    echo -n '# '
    grep 'name = ' setup.cfg | awk '{ print $3 }'
    tail -n +4 .gh-pages/content/_index-liquid-rendered.md
    )''',
    encoding="utf-8",
    shell=True,
    stdout=PIPE,
  )

  for line in proc.stdout:
    f.write(
      make_urls_absolute(
        line, "https://v3gtb.github.io/fooddata-vegattributes/"
      )
    )

def is_repo_readme_changed():
  r = run(["git", "diff", "--exit-code", "HEAD", "--", "README.md"])
  if r.returncode == 0:
    return False
  elif r.returncode == 1:
    return True
  else:
    r.check_returncode()


if __name__ == "__main__":
  with TemporaryDirectory() as tmpdir:
    tmpdir_path = Path(tmpdir)
    tmp_readme_path = (tmpdir_path/"README.md")
    with tmp_readme_path.open("w") as f:
      render_readme_into_file(f)
    r = run(["diff", "README.md", tmp_readme_path])
    if r.returncode == 1:
      if is_repo_readme_changed():
        print(
          "Not doing anything because the README in the repo has changed in "
          "an unexpected manner (see above). It should only be modified by "
          "changing the GH Pages files and then running this utility. "
          "Move your changes there or restore the unmodified file from Git."
        )
        exit(2)
      else:
        move(tmp_readme_path, "README.md")
        # this was actually successful but pre-commit should fail anyway the
        # first time round so it can double as a check in CI
        exit(1)
    else:
      r.check_returncode()
