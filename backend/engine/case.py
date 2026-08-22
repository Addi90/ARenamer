"""Case modifier.

Changes the letter case of the base name.

Simple (whole-name) modes:
  - "upper":    all characters uppercase
  - "lower":    all characters lowercase
  - "title":    first character of each word uppercase (``str.title``)
  - "sentence": first character uppercase, rest lowercase (``str.capitalize``)

Word modes (the name is split into words, then rejoined in the target case):
  - "camel":    helloWorld
  - "pascal":   HelloWorld
  - "snake":    hello_world
  - "kebab":    hello-world
  - "constant": HELLO_WORLD
  - "train":    hello world

Word splitting: the name is split on delimiters (space, underscore, hyphen) and
before every uppercase letter. Digits never split a word (``file2x`` stays one
word). Acronyms are split naively, one letter per word
(``XMLHttpRequest`` -> ``x``, ``m``, ``l``, ``http``, ``request``).

Note: ``str.title`` capitalizes after apostrophes ("it's" -> "It'S"); that is the
documented, faithful behavior of the mode (see AGENTS.md section 4).
"""

from __future__ import annotations

import re

from .models import CaseConfig, RenameFile

_SIMPLE_MODES = {
    "upper": str.upper,
    "lower": str.lower,
    "title": str.title,
    "sentence": str.capitalize,
}

_WORD_MODES = {"camel", "pascal", "snake", "kebab", "constant", "train"}


def _split_words(name: str) -> list[str]:
    """Split a base name into lowercase words (see module docstring)."""
    words: list[str] = []
    for chunk in re.split(r"[\s_\-]+", name):
        if not chunk:
            continue
        for part in re.split(r"(?=[A-Z])", chunk):
            if part:
                words.append(part.lower())
    return words


def _word_case(name: str, mode: str) -> str:
    words = _split_words(name)
    if not words:
        return ""
    cap = lambda w: w[:1].upper() + w[1:]  # noqa: E731
    if mode == "camel":
        return words[0] + "".join(cap(w) for w in words[1:])
    if mode == "pascal":
        return "".join(cap(w) for w in words)
    if mode == "snake":
        return "_".join(words)
    if mode == "kebab":
        return "-".join(words)
    if mode == "constant":
        return "_".join(w.upper() for w in words)
    return " ".join(words)  # train


def modify(files: list[RenameFile], cfg: CaseConfig) -> None:
    mode = cfg.mode
    if mode in _SIMPLE_MODES:
        fn = _SIMPLE_MODES[mode]
    elif mode in _WORD_MODES:
        fn = lambda name: _word_case(name, mode)  # noqa: E731
    else:
        fn = str.upper  # unknown mode -> upper (a safe, visible default)
    for f in files:
        f.new_base = fn(f.new_base)
