"""Tests for the rename engine (Milestone 2).

Run from the repo root:  python3 -m pytest tests/ -v
"""

from __future__ import annotations

import os
from datetime import date

import pytest

from backend.engine import (
    Config,
    RenameFile,
    build_files,
    check_duplicates,
    compute,
    preview,
)
from backend.engine.models import (
    AddConfig,
    CountingConfig,
    DateConfig,
    IfThenConfig,
    RemoveConfig,
    ReplaceConfig,
    split_name,
)


def one(name: str, path: str = "") -> RenameFile:
    return RenameFile(name=name, path=path, row=0)


# --------------------------------------------------------------------------- #
# split_name
# --------------------------------------------------------------------------- #

class TestSplitName:
    def test_simple_extension(self):
        assert split_name("photo.txt") == ("photo", ".txt")

    def test_last_dot_wins(self):
        assert split_name("archive.tar.gz") == ("archive.tar", ".gz")

    def test_no_extension(self):
        assert split_name("README") == ("README", "")

    def test_leading_dot_hidden_file(self):
        # dot at index 0 -> empty base, whole name is the "extension" (matches Qt)
        assert split_name(".bashrc") == ("", ".bashrc")

    def test_multiple_dots(self):
        assert split_name("a.b.c") == ("a.b", ".c")


# --------------------------------------------------------------------------- #
# Add modifier (5a)
# --------------------------------------------------------------------------- #

class TestAdd:
    def test_prefix(self):
        f = one("world")
        compute([f], Config(add=AddConfig(enabled=True, prefix="hello ")))
        assert f.new_base == "hello world"

    def test_suffix(self):
        f = one("hello")
        compute([f], Config(add=AddConfig(enabled=True, suffix=" world")))
        assert f.new_base == "hello world"

    def test_insert_at_position(self):
        f = one("helloworld")
        compute([f], Config(add=AddConfig(enabled=True, insert=" ", insert_pos=5)))
        assert f.new_base == "hello world"

    def test_insert_clamped_to_end(self):
        f = one("abc")
        compute([f], Config(add=AddConfig(enabled=True, insert="X", insert_pos=99)))
        assert f.new_base == "abcX"

    def test_insert_applied_before_wrap(self):
        # insert first, then prefix+suffix wrap (original order)
        f = one("world")
        compute([f], Config(add=AddConfig(enabled=True, prefix="[", suffix="]", insert="-x", insert_pos=0)))
        assert f.new_base == "[-xworld]"

    def test_empty_strings_are_noops(self):
        f = one("name")
        compute([f], Config(add=AddConfig(enabled=True)))  # all empty
        assert f.new_base == "name"

    def test_disabled_is_noop(self):
        f = one("name")
        compute([f], Config(add=AddConfig(enabled=False, prefix="X")))
        assert f.new_base == "name"


# --------------------------------------------------------------------------- #
# Remove modifier (5d)
# --------------------------------------------------------------------------- #

class TestRemove:
    def test_front(self):
        f = one("hello")
        compute([f], Config(remove=RemoveConfig(enabled=True, front=2)))
        assert f.new_base == "llo"

    def test_back(self):
        f = one("hello")
        compute([f], Config(remove=RemoveConfig(enabled=True, back=2)))
        assert f.new_base == "hel"

    def test_front_exceeds_length_empties(self):
        f = one("abc")
        compute([f], Config(remove=RemoveConfig(enabled=True, front=10)))
        assert f.new_base == ""

    def test_back_exceeds_length_empties(self):
        f = one("abc")
        compute([f], Config(remove=RemoveConfig(enabled=True, back=10)))
        assert f.new_base == ""

    def test_range_middle(self):
        # remove 1-based positions 3..5 ('c','d','e') from "abcdefghij"
        f = one("abcdefghij")
        compute([f], Config(remove=RemoveConfig(enabled=True, range_enabled=True, range_start=3, range_end=5)))
        assert f.new_base == "abfghij"

    def test_range_until_end(self):
        f = one("hello")
        compute([f], Config(remove=RemoveConfig(enabled=True, range_enabled=True, range_start=3, until_end=True)))
        assert f.new_base == "he"

    def test_range_clamped_to_actual_end(self):
        # range runs past the end of a short name -> clamp, no out-of-bounds
        f = one("abc")
        compute([f], Config(remove=RemoveConfig(enabled=True, range_enabled=True, range_start=2, range_end=99)))
        assert f.new_base == "a"

    def test_front_back_then_range(self):
        # front 1 ("h"), back 1 ("o") -> "ell", then range pos2..3 ("l","l") -> "e"
        f = one("hello")
        compute([f], Config(remove=RemoveConfig(enabled=True, front=1, back=1, range_enabled=True, range_start=2, range_end=3)))
        assert f.new_base == "e"


# --------------------------------------------------------------------------- #
# Replace modifier (5c)
# --------------------------------------------------------------------------- #

class TestReplace:
    def test_plain_case_sensitive(self):
        f = one("Hello World")
        compute([f], Config(replace=ReplaceConfig(enabled=True, search="World", replace="there")))
        assert f.new_base == "Hello there"

    def test_plain_case_insensitive(self):
        f = one("hello world")
        compute([f], Config(replace=ReplaceConfig(enabled=True, search="WORLD", replace="there")))
        assert f.new_base == "hello there"

    def test_replaces_all_occurrences(self):
        f = one("a-b-c")
        compute([f], Config(replace=ReplaceConfig(enabled=True, search="-", replace="_")))
        assert f.new_base == "a_b_c"

    def test_regex(self):
        f = one("a1b2c3")
        compute([f], Config(replace=ReplaceConfig(enabled=True, search=r"\d", replace="#", regex=True)))
        assert f.new_base == "a#b#c#"

    def test_regex_case_insensitive(self):
        f = one("ABC")
        compute([f], Config(replace=ReplaceConfig(enabled=True, search="abc", replace="xyz", regex=True)))
        assert f.new_base == "xyz"

    def test_applied_exactly_once(self):
        # regression: the original double-applied; a single 'a' -> one replacement
        f = one("a")
        compute([f], Config(replace=ReplaceConfig(enabled=True, search="a", replace="aa")))
        assert f.new_base == "aa"

    def test_invalid_regex_is_noop(self):
        f = one("abc")
        compute([f], Config(replace=ReplaceConfig(enabled=True, search="(", replace="#", regex=True)))
        assert f.new_base == "abc"


# --------------------------------------------------------------------------- #
# Counting / Number modifier (5e)
# --------------------------------------------------------------------------- #

class TestCounting:
    def test_prefix_sequence(self):
        files = build_files("", ["a", "b", "c"])
        compute(files, Config(counting=CountingConfig(enabled=True, position="prefix", start=1)))
        assert [f.new_base for f in files] == ["1a", "2b", "3c"]

    def test_suffix_with_start_offset(self):
        files = build_files("", ["a", "b"])
        compute(files, Config(counting=CountingConfig(enabled=True, position="suffix", start=10)))
        assert [f.new_base for f in files] == ["a10", "b11"]

    def test_zero_padding(self):
        files = build_files("", ["a", "b"])
        compute(files, Config(counting=CountingConfig(enabled=True, position="prefix", start=1, padding=3)))
        assert [f.new_base for f in files] == ["001a", "002b"]

    def test_insert_at_position(self):
        f = one("helloworld")
        compute([f], Config(counting=CountingConfig(enabled=True, position="insert", start=1, insert_pos=5)))
        assert f.new_base == "hello1world"

    def test_numbering_follows_list_order_not_alphabetical(self):
        # rows are 0,1 in the given (non-alphabetical) order -> numbering follows that
        files = build_files("", ["zeta", "alpha"])
        compute(files, Config(counting=CountingConfig(enabled=True, position="prefix", start=1)))
        assert [f.new_base for f in files] == ["1zeta", "2alpha"]


# --------------------------------------------------------------------------- #
# If-Then modifier (5b)
# --------------------------------------------------------------------------- #

class TestIfThen:
    def test_contains_plain_insensitive(self):
        f = one("PHOTO.jpg")  # base "PHOTO"
        compute([f], Config(ifthen=IfThenConfig(enabled=True, expression="photo", action="suffix", string="_x")))
        assert f.new_base == "PHOTO_x"

    def test_contains_not(self):
        f = one("report.txt")  # base "report" does not contain "photo"
        compute([f], Config(ifthen=IfThenConfig(enabled=True, contains_not=True, expression="photo", action="suffix", string="_skip")))
        assert f.new_base == "report_skip"

    def test_contains_not_no_match(self):
        f = one("photo.txt")  # base "photo" DOES contain "photo" -> condition false
        compute([f], Config(ifthen=IfThenConfig(enabled=True, contains_not=True, expression="photo", action="suffix", string="_x")))
        assert f.new_base == "photo"

    def test_regex_condition(self):
        f = one("file2.txt")  # base "file2" ends in a digit
        compute([f], Config(ifthen=IfThenConfig(enabled=True, expression=r"\d+$", regex=True, action="prefix", string="n")))
        assert f.new_base == "nfile2"

    def test_case_sensitive(self):
        f = one("Photo.jpg")  # base "Photo"; searching lowercase 'photo' case-sensitively -> no match
        compute([f], Config(ifthen=IfThenConfig(enabled=True, expression="photo", case_sensitive=True, action="suffix", string="_x")))
        assert f.new_base == "Photo"

    def test_condition_uses_original_base(self):
        # Replace runs first (new_base loses "final"), but If-Then tests the ORIGINAL base.
        f = one("report_final.txt")  # base "report_final"
        cfg = Config(
            replace=ReplaceConfig(enabled=True, search="final", replace="end"),
            ifthen=IfThenConfig(enabled=True, expression="final", action="suffix", string="_v2"),
        )
        compute([f], cfg)
        # replace -> "report_end"; ifthen condition on original "report_final" still matches
        assert f.new_base == "report_end_v2"

    def test_empty_expression_is_noop(self):
        f = one("anything")
        compute([f], Config(ifthen=IfThenConfig(enabled=True, expression="", action="suffix", string="_x")))
        assert f.new_base == "anything"


# --------------------------------------------------------------------------- #
# Date modifier (5f)
# --------------------------------------------------------------------------- #

class TestDate:
    def test_custom_ymd_suffix(self):
        # The date is appended directly (no separator between name and date), matching the original.
        f = one("report")
        cfg = Config(date=DateConfig(enabled=True, source="custom", custom_date=date(2024, 5, 1), format="ymd", separator="-", position="suffix"))
        compute([f], cfg)
        assert f.new_base == "report2024-05-01"

    def test_custom_dmy(self):
        f = one("report")
        cfg = Config(date=DateConfig(enabled=True, source="custom", custom_date=date(2024, 5, 1), format="dmy", separator="-"))
        compute([f], cfg)
        assert f.new_base == "report01-05-2024"

    def test_custom_mdy(self):
        f = one("report")
        cfg = Config(date=DateConfig(enabled=True, source="custom", custom_date=date(2024, 5, 1), format="mdy", separator="/"))
        compute([f], cfg)
        assert f.new_base == "report05/01/2024"

    def test_prefix_position(self):
        f = one("report")
        cfg = Config(date=DateConfig(enabled=True, source="custom", custom_date=date(2024, 1, 9), format="ymd", position="prefix"))
        compute([f], cfg)
        assert f.new_base == "2024-01-09report"

    def test_insert_position(self):
        f = one("report")
        cfg = Config(date=DateConfig(enabled=True, source="custom", custom_date=date(2024, 1, 9), format="ymd", position="insert", insert_pos=0))
        compute([f], cfg)
        assert f.new_base == "2024-01-09report"

    def test_modified_source_reads_filesystem(self, tmp_path):
        p = tmp_path / "data.txt"
        p.write_text("x")
        os.utime(p, (1700000000, 1700000000))  # fixed mtime
        f = RenameFile(name="data.txt", path=str(tmp_path), row=0)
        cfg = Config(date=DateConfig(enabled=True, source="modified", format="ymd"))
        compute([f], cfg)
        # exact calendar date depends on local TZ; assert a well-formed "data" + 10-char ymd
        assert f.new_base.startswith("data") and len(f.new_base) == len("data2023-11-14")

    def test_created_source_is_well_formed(self, tmp_path):
        p = tmp_path / "data.txt"
        p.write_text("x")
        f = RenameFile(name="data.txt", path=str(tmp_path), row=0)
        cfg = Config(date=DateConfig(enabled=True, source="created", format="ymd"))
        compute([f], cfg)
        assert f.new_base.startswith("data") and len(f.new_base) == len("data2023-11-14")


# --------------------------------------------------------------------------- #
# Pipeline ordering (AGENTS.md section 3) — the critical contract
# --------------------------------------------------------------------------- #

class TestPipelineOrder:
    def test_counting_then_date(self):
        f = one("name")
        cfg = Config(
            counting=CountingConfig(enabled=True, position="suffix", start=1, padding=2),
            date=DateConfig(enabled=True, source="custom", custom_date=date(2024, 5, 1), format="ymd"),
        )
        compute([f], cfg)
        # number suffix -> "name01"; then date suffix appends directly (no separator)
        assert f.new_base == "name012024-05-01"

    def test_replace_before_add(self):
        f = one("foo_bar")
        cfg = Config(
            replace=ReplaceConfig(enabled=True, search="_", replace="-"),
            add=AddConfig(enabled=True, prefix="X_"),
        )
        compute([f], cfg)
        # replace -> "foo-bar"; add prefix -> "X_foo-bar"
        assert f.new_base == "X_foo-bar"

    def test_remove_before_counting(self):
        f = one("prefix_name")
        cfg = Config(
            remove=RemoveConfig(enabled=True, front=7),  # drop "prefix_" -> "name"
            counting=CountingConfig(enabled=True, position="suffix", start=1),
        )
        compute([f], cfg)
        assert f.new_base == "name1"

    def test_full_sequence(self):
        # Replace -> If-Then -> Remove -> Add -> Counting -> Date
        f = one("IMG_final 01.jpg")  # base "IMG_final 01"
        cfg = Config(
            replace=ReplaceConfig(enabled=True, search="IMG", replace="img"),   # -> "img_final 01"
            ifthen=IfThenConfig(enabled=True, expression="final", action="suffix", string="_v2"),  # cond on original base; -> "img_final 01_v2"
            remove=RemoveConfig(enabled=True, front=8),                          # drop 8 chars "img_fina" -> "l 01_v2"
            add=AddConfig(enabled=True, suffix="!"),                             # -> "l 01_v2!"
            counting=CountingConfig(enabled=True, position="prefix", start=1),   # -> "1l 01_v2!"
            date=DateConfig(enabled=True, source="custom", custom_date=date(2024, 5, 1), format="ymd"),
        )
        compute([f], cfg)
        # date appends directly (no separator): "1l 01_v2!" + "2024-05-01"
        assert f.new_base == "1l 01_v2!2024-05-01"

    def test_is_idempotent_across_calls(self):
        # same inputs -> same outputs no matter how many times we run it
        files = build_files("", ["a", "b"])
        cfg = Config(counting=CountingConfig(enabled=True, position="prefix", start=1))
        first = {f.name: f.new_base for f in compute(build_files("", ["a", "b"]), cfg)}
        second = {f.name: f.new_base for f in compute(build_files("", ["a", "b"]), cfg)}
        assert first == second == {"a": "1a", "b": "2b"}


# --------------------------------------------------------------------------- #
# preview + check_duplicates helpers
# --------------------------------------------------------------------------- #

class TestPreviewAndDuplicates:
    def test_preview_returns_new_base(self):
        files = build_files("", ["a.txt", "b.txt"])
        cfg = Config(counting=CountingConfig(enabled=True, position="prefix", start=1))
        result = preview(files, cfg)
        assert result["a.txt"]["new_base"] == "1a"
        assert result["b.txt"]["new_base"] == "2b"
        assert result["a.txt"]["ext"] == ".txt"
        assert result["a.txt"]["full_new_name"] == "1a.txt"

    def test_preview_unchanged_flag(self):
        files = build_files("", ["a.txt"])
        result = preview(files, Config())  # no modifiers -> unchanged
        assert result["a.txt"]["changed"] is False

    def test_duplicate_detected(self, tmp_path):
        (tmp_path / "target.txt").write_text("existing")
        files = build_files(str(tmp_path), ["source.txt"])
        cfg = Config(replace=ReplaceConfig(enabled=True, search="source", replace="target"))
        assert check_duplicates(files, cfg) == 1

    def test_unchanged_file_not_counted_as_duplicate(self, tmp_path):
        (tmp_path / "a.txt").write_text("x")
        files = build_files(str(tmp_path), ["a.txt"])
        cfg = Config()  # no change -> a.txt stays a.txt (exists) but is unchanged
        assert check_duplicates(files, cfg) == 0


# --------------------------------------------------------------------------- #
# Config (de)serialization for the JSON API
# --------------------------------------------------------------------------- #

class TestConfigSerialization:
    def test_round_trip(self):
        cfg = Config(
            add=AddConfig(enabled=True, prefix="p", suffix="s"),
            replace=ReplaceConfig(enabled=True, search="a", replace="b", regex=True),
        )
        assert Config.from_dict(cfg.to_dict()) == cfg

    def test_partial_config_uses_defaults(self):
        cfg = Config.from_dict({"counting": {"enabled": True, "start": 5}})
        assert cfg.counting.enabled is True
        assert cfg.counting.start == 5
        assert cfg.add.enabled is False  # untouched -> default

    def test_empty_dict_gives_all_disabled(self):
        cfg = Config.from_dict({})
        assert not any(
            [cfg.add.enabled, cfg.ifthen.enabled, cfg.replace.enabled,
             cfg.remove.enabled, cfg.counting.enabled, cfg.date.enabled]
        )

    def test_custom_date_parsed_from_string(self):
        cfg = Config.from_dict({"date": {"enabled": True, "source": "custom", "custom_date": "2024-05-01"}})
        assert cfg.date.custom_date == date(2024, 5, 1)
