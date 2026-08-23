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
    CaseConfig,
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

    def test_empty_search_is_noop(self):
        # regression: str.replace("", x) would insert the replacement between every char
        f = one("abc")
        compute([f], Config(replace=ReplaceConfig(enabled=True, search="", replace="X")))
        assert f.new_base == "abc"

    def test_empty_regex_search_is_noop(self):
        f = one("abc")
        compute([f], Config(replace=ReplaceConfig(enabled=True, search="", replace="X", regex=True)))
        assert f.new_base == "abc"


# --------------------------------------------------------------------------- #
# Case modifier
# --------------------------------------------------------------------------- #

class TestCase:
    def test_upper(self):
        f = one("hello World")
        compute([f], Config(case=CaseConfig(enabled=True, mode="upper")))
        assert f.new_base == "HELLO WORLD"

    def test_lower(self):
        f = one("Hello WORLD")
        compute([f], Config(case=CaseConfig(enabled=True, mode="lower")))
        assert f.new_base == "hello world"

    def test_title(self):
        f = one("hello world")
        compute([f], Config(case=CaseConfig(enabled=True, mode="title")))
        assert f.new_base == "Hello World"

    def test_title_apostrophe_quirk(self):
        # str.title capitalizes after apostrophes: "it's" -> "It'S"
        f = one("it's here")
        compute([f], Config(case=CaseConfig(enabled=True, mode="title")))
        assert f.new_base == "It'S Here"

    def test_sentence(self):
        f = one("hELLO wORLD")
        compute([f], Config(case=CaseConfig(enabled=True, mode="sentence")))
        assert f.new_base == "Hello world"

    def test_disabled_is_noop(self):
        f = one("hello")
        compute([f], Config(case=CaseConfig(enabled=False, mode="upper")))
        assert f.new_base == "hello"

    def test_extension_untouched(self):
        f = one("photo.JPG")
        compute([f], Config(case=CaseConfig(enabled=True, mode="lower")))
        assert f.new_base == "photo"
        assert f.new_full_name == "photo.JPG"

    def test_unknown_mode_falls_back_to_upper(self):
        f = one("hello")
        compute([f], Config(case=CaseConfig(enabled=True, mode="bogus")))
        assert f.new_base == "HELLO"

    # word modes: mixed input with camelCase boundaries + all three delimiters
    def test_camel(self):
        f = one("helloWorld_foo-bar baz")
        compute([f], Config(case=CaseConfig(enabled=True, mode="camel")))
        assert f.new_base == "helloWorldFooBarBaz"

    def test_pascal(self):
        f = one("helloWorld_foo-bar baz")
        compute([f], Config(case=CaseConfig(enabled=True, mode="pascal")))
        assert f.new_base == "HelloWorldFooBarBaz"

    def test_snake(self):
        f = one("helloWorld_foo-bar baz")
        compute([f], Config(case=CaseConfig(enabled=True, mode="snake")))
        assert f.new_base == "hello_world_foo_bar_baz"

    def test_kebab(self):
        f = one("helloWorld_foo-bar baz")
        compute([f], Config(case=CaseConfig(enabled=True, mode="kebab")))
        assert f.new_base == "hello-world-foo-bar-baz"

    def test_constant(self):
        f = one("helloWorld_foo-bar baz")
        compute([f], Config(case=CaseConfig(enabled=True, mode="constant")))
        assert f.new_base == "HELLO_WORLD_FOO_BAR_BAZ"

    def test_train(self):
        f = one("helloWorld_foo-bar baz")
        compute([f], Config(case=CaseConfig(enabled=True, mode="train")))
        assert f.new_base == "hello world foo bar baz"

    def test_digits_attach_to_preceding_word(self):
        f = one("file2x")
        compute([f], Config(case=CaseConfig(enabled=True, mode="snake")))
        assert f.new_base == "file2x"

    def test_acronym_naive_split(self):
        # every uppercase starts a new word: X, M, L, Http, Request
        f = one("XMLHttpRequest")
        compute([f], Config(case=CaseConfig(enabled=True, mode="snake")))
        assert f.new_base == "x_m_l_http_request"

    def test_word_mode_empty_base(self):
        f = one(".bashrc")  # leading-dot name -> empty base
        compute([f], Config(case=CaseConfig(enabled=True, mode="snake")))
        assert f.new_base == ""


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

    def test_name_separator_suffix(self):
        f = one("report")
        cfg = Config(date=DateConfig(enabled=True, source="custom", custom_date=date(2024, 5, 1), format="ymd", position="suffix", name_separator="-"))
        compute([f], cfg)
        assert f.new_base == "report-2024-05-01"

    def test_name_separator_prefix(self):
        f = one("report")
        cfg = Config(date=DateConfig(enabled=True, source="custom", custom_date=date(2024, 1, 9), format="ymd", position="prefix", name_separator="_"))
        compute([f], cfg)
        assert f.new_base == "2024-01-09_report"

    def test_name_separator_insert_both_sides(self):
        f = one("report")
        cfg = Config(date=DateConfig(enabled=True, source="custom", custom_date=date(2024, 1, 9), format="ymd", position="insert", insert_pos=2, name_separator="-"))
        compute([f], cfg)
        assert f.new_base == "re-2024-01-09-port"

    def test_name_separator_insert_at_start_has_no_leading_sep(self):
        f = one("report")
        cfg = Config(date=DateConfig(enabled=True, source="custom", custom_date=date(2024, 1, 9), format="ymd", position="insert", insert_pos=0, name_separator="-"))
        compute([f], cfg)
        assert f.new_base == "2024-01-09-report"

    def test_name_separator_empty_base_has_no_dangling_sep(self):
        # A previous modifier (Remove) emptied the base; no dangling separator.
        f = one("x")
        cfg = Config(
            remove=RemoveConfig(enabled=True, front=1),
            date=DateConfig(enabled=True, source="custom", custom_date=date(2024, 5, 1), format="ymd", position="suffix", name_separator="-"),
        )
        compute([f], cfg)
        assert f.new_base == "2024-05-01"

    def test_name_separator_default_empty_is_faithful(self):
        # Default (no name separator) keeps the original's direct concatenation.
        f = one("report")
        cfg = Config(date=DateConfig(enabled=True, source="custom", custom_date=date(2024, 5, 1), format="ymd"))
        compute([f], cfg)
        assert f.new_base == "report2024-05-01"


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

    def test_case_between_replace_and_ifthen(self):
        # Replace -> Case -> If-Then: case transforms the replaced text, and the
        # If-Then condition still tests the ORIGINAL base name.
        f = one("IMG_final 01.jpg")  # base "IMG_final 01"
        cfg = Config(
            replace=ReplaceConfig(enabled=True, search="IMG", replace="img"),   # -> "img_final 01"
            case=CaseConfig(enabled=True, mode="upper"),                        # -> "IMG_FINAL 01"
            ifthen=IfThenConfig(enabled=True, expression="final", action="suffix", string="_v2"),  # cond on original base -> "IMG_FINAL 01_v2"
        )
        compute([f], cfg)
        assert f.new_base == "IMG_FINAL 01_v2"

    def test_full_sequence(self):
        # Replace -> Case -> If-Then -> Remove -> Add -> Counting -> Date
        f = one("IMG_final 01.jpg")  # base "IMG_final 01"
        cfg = Config(
            replace=ReplaceConfig(enabled=True, search="IMG", replace="img"),   # -> "img_final 01"
            case=CaseConfig(enabled=True, mode="upper"),                        # -> "IMG_FINAL 01"
            ifthen=IfThenConfig(enabled=True, expression="final", action="suffix", string="_v2"),  # cond on original base; -> "IMG_FINAL 01_v2"
            remove=RemoveConfig(enabled=True, front=8),                          # drop 8 chars "IMG_FINA" -> "L 01_v2"
            add=AddConfig(enabled=True, suffix="!"),                             # -> "L 01_v2!"
            counting=CountingConfig(enabled=True, position="prefix", start=1),   # -> "1L 01_v2!"
            date=DateConfig(enabled=True, source="custom", custom_date=date(2024, 5, 1), format="ymd"),
        )
        compute([f], cfg)
        # date appends directly (no separator): "1L 01_v2!" + "2024-05-01"
        assert f.new_base == "1L 01_v2!2024-05-01"

    def test_is_idempotent_across_calls(self):
        # same inputs -> same outputs no matter how many times we run it
        files = build_files("", ["a", "b"])
        cfg = Config(counting=CountingConfig(enabled=True, position="prefix", start=1))
        first = {f.name: f.new_base for f in compute(build_files("", ["a", "b"]), cfg)}
        second = {f.name: f.new_base for f in compute(build_files("", ["a", "b"]), cfg)}
        assert first == second == {"a": "1a", "b": "2b"}


# --------------------------------------------------------------------------- #
# custom pipeline order (Config.pipeline_order)
# --------------------------------------------------------------------------- #

class TestCustomPipelineOrder:
    def test_none_order_is_canonical(self):
        f = one("abc")
        cfg = Config(
            counting=CountingConfig(enabled=True, position="suffix", start=1, padding=2),
            remove=RemoveConfig(enabled=True, back=1),
        )
        compute([f], cfg)  # canonical: remove before counting -> "ab" + "01"
        assert f.new_base == "ab01"

    def test_custom_order_changes_result(self):
        # counting before remove: "abc" -> "abc01" -> drop last char -> "abc0"
        f = one("abc")
        cfg = Config(
            counting=CountingConfig(enabled=True, position="suffix", start=1, padding=2),
            remove=RemoveConfig(enabled=True, back=1),
            pipeline_order=["counting", "remove"],
        )
        compute([f], cfg)
        assert f.new_base == "abc0"

    def test_partial_custom_order_appends_missing_canonical_ids(self):
        # only "counting" given: it runs first, missing ids are appended in
        # canonical order (so remove still runs, after counting) -> "abc0"
        f = one("abc")
        cfg = Config(
            counting=CountingConfig(enabled=True, position="suffix", start=1, padding=2),
            remove=RemoveConfig(enabled=True, back=1),
            pipeline_order=["counting"],
        )
        compute([f], cfg)
        assert f.new_base == "abc0"

    def test_unknown_ids_are_dropped(self):
        # "nope" is dropped; counting stays first of the remaining ids
        f = one("abc")
        cfg = Config(
            counting=CountingConfig(enabled=True, position="suffix", start=1, padding=2),
            remove=RemoveConfig(enabled=True, back=1),
            pipeline_order=["nope", "counting"],
        )
        compute([f], cfg)
        assert f.new_base == "abc0"


class TestPipelineOrderSerialization:
    def test_round_trip(self):
        cfg = Config(pipeline_order=["counting", "remove"])
        assert Config.from_dict(cfg.to_dict()).pipeline_order == ["counting", "remove"]

    def test_null_order_becomes_none(self):
        assert Config.from_dict({"pipeline_order": None}).pipeline_order is None

    def test_non_list_order_becomes_none(self):
        assert Config.from_dict({"pipeline_order": "counting"}).pipeline_order is None

    def test_non_string_entries_become_none(self):
        assert Config.from_dict({"pipeline_order": [1, "counting"]}).pipeline_order is None


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

    def test_null_numeric_falls_back_to_default(self):
        # a cleared UI number input serializes as null; it must not crash the engine
        cfg = Config.from_dict({"add": {"enabled": True, "insert_pos": None},
                                "remove": {"front": None, "back": None}})
        assert cfg.add.insert_pos == 0
        assert cfg.remove.front == 0 and cfg.remove.back == 0

    def test_null_bool_falls_back_to_default(self):
        cfg = Config.from_dict({"replace": {"enabled": None, "regex": None}})
        assert cfg.replace.enabled is False and cfg.replace.regex is False

    def test_null_custom_date_stays_none(self):
        cfg = Config.from_dict({"date": {"enabled": True, "source": "custom", "custom_date": None}})
        assert cfg.date.custom_date is None
