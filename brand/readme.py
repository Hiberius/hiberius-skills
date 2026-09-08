#!/usr/bin/env python3
"""One template, ten READMEs. The shared parts are shared by construction.

Run after gen.py:  python3 readme.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import SKILLS  # noqa: E402

# Raw HTML, not markdown: GitHub does not process markdown inside a block-level
# HTML element, so a markdown badge inside <p align="center"> renders as literal text.
BADGE = {
    "mit": '<a href="LICENSE"><img alt="License: MIT" '
           'src="https://img.shields.io/badge/License-MIT-2ea44f.svg"></a>',
    "py": '<img alt="Python 3.8+" '
          'src="https://img.shields.io/badge/python-3.8%2B-3776AB?logo=python&logoColor=white">',
    "deps": '<img alt="Zero dependencies" '
            'src="https://img.shields.io/badge/dependencies-0-6E56CF">',
    "off": '<img alt="No network calls" '
           'src="https://img.shields.io/badge/network-never-8f9bb8">',
    "tests": '<img alt="%d tests" '
             'src="https://img.shields.io/badge/tests-%d%%20passing-2ea44f">',
}


def header(s, extra_badge=None, tests=None):
    n = int(s["chips"][0].split()[0])
    badges = [BADGE["mit"], BADGE["py"], BADGE["deps"], BADGE["off"],
              BADGE["tests"] % (n, n)]
    if extra_badge:
        badges.append(extra_badge)
    return """<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/hero-light.svg">
    <img alt="%s" src="assets/hero-dark.svg" width="100%%">
  </picture>
</p>

<h1 align="center">%s</h1>

<p align="center"><b>%s</b></p>

<p align="center">
%s
</p>

<p align="center">
  <code>npx skills add Hiberius/%s</code>
</p>

<p align="center">
  <sub>Works with Claude Code, Claude Desktop, Codex, Cursor, Windsurf, OpenClaw and
  anything else that reads a <code>SKILL.md</code>.</sub>
</p>

---
""" % (s["hero_alt"], s["title"], s["tagline"], "\n  ".join(badges), s["repo"])


def inside(s):
    return """## How it works inside

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/diagram-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/diagram-light.svg">
    <img alt="%s" src="assets/diagram-dark.svg" width="100%%">
  </picture>
</p>
""" % s["diagram_alt"]


def docs(s):
    lines = ["## Documentation", "",
             "- [`SKILL.md`](SKILL.md) — the skill itself, what the agent reads"]
    for path, desc in s["refs"]:
        lines.append("- [`%s`](%s) — %s" % (path, path, desc))
    return "\n".join(lines) + "\n"


def related(s):
    lines = ["## Related skills", ""]
    for repo, why in s["related"]:
        lines.append("- **[%s](https://github.com/Hiberius/%s)** — %s" % (repo, repo, why))
    lines += ["",
              "All ten in one install:",
              "",
              "```",
              "/plugin marketplace add Hiberius/hiberius-skills",
              "```"]
    return "\n".join(lines) + "\n"


FOOTER = """## Work with me

I build the systems these skills came out of: performance marketing infrastructure,
lead pipelines, ad account tooling, internal automation, and products on the Cloudflare
edge stack. If you need something like this built properly, I take on freelance and
contract work.

**[Christian Calabro — github.com/Hiberius](https://github.com/Hiberius)**

Performance marketing · media buying · TypeScript · Cloudflare Workers · Next.js · Python

---

## Contributing

Issues and pull requests welcome. The rule for a change to the skill itself: it has to
be something you learned by getting it wrong once, not something you read in the docs.

## License

MIT. No network calls, no telemetry, no dependencies.
"""


def build(s):
    parts = [header(s, s.get("extra_badge")), "", s["body_top"], "", inside(s), ""]
    parts += [s["body_bottom"], "", docs(s), "", related(s), "", FOOTER]
    return "\n".join(parts).replace("\n\n\n\n", "\n\n").strip() + "\n"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    repos = os.path.abspath(os.path.join(here, "..", ".."))
    from readme_content import CONTENT
    n = 0
    for s in SKILLS:
        s.update(CONTENT[s["repo"]])
        path = os.path.join(repos, s["repo"], "README.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(build(s))
        n += 1
    print("%d README scritti" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
