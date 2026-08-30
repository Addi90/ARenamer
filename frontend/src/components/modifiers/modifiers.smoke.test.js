// @vitest-environment jsdom
/**
 * Smoke tests for the seven modifier panels (Replace, Case, If-Then, Remove,
 * Add, Counting, Date). Every panel is a `<fieldset class="controls">` whose
 * disabled attribute mirrors `state.config.<key>.enabled` (the enable toggle
 * itself lives in ModifierCard) — so the generic disabled-state behaviour is
 * checked for all seven at once, plus a few panel-specific bindings
 * (including the conditional inputs: If-Then / Counting / Date insert
 * position, Remove range, Date custom picker).
 *
 * happy-dom crashes inside Svelte 5 checkbox mounting, hence jsdom.
 */
import { describe, it, expect, beforeEach } from "vitest";
import { render, fireEvent, cleanup } from "@testing-library/svelte";
import { state } from "../../lib/state/store.svelte.js";
import { setLanguage } from "../../lib/i18n/index.svelte.js";
import { defaultConfig } from "../../lib/config.js";

// Store bindings write synchronously, but Svelte 5 flushes the resulting DOM
// updates (classes, {#if} visibility, disabled attributes) on a later tick —
// flush before asserting on the DOM.
const settle = () => new Promise((r) => setTimeout(r, 0));

import ReplaceModifier from "./ReplaceModifier.svelte";
import CaseModifier from "./CaseModifier.svelte";
import IfThenModifier from "./IfThenModifier.svelte";
import RemoveModifier from "./RemoveModifier.svelte";
import AddModifier from "./AddModifier.svelte";
import CountingModifier from "./CountingModifier.svelte";
import DateModifier from "./DateModifier.svelte";

// The panels bind directly to the module-level store singleton; hand every
// test a fresh default config (all seven modifiers start disabled).
beforeEach(() => {
  cleanup();
  setLanguage("en");
  state.config = defaultConfig();
});

// ---- generic panel behaviour (all seven) ----------------------------------

const PANELS = [
  ["replace", ReplaceModifier],
  ["case", CaseModifier],
  ["ifthen", IfThenModifier],
  ["remove", RemoveModifier],
  ["add", AddModifier],
  ["counting", CountingModifier],
  ["date", DateModifier],
];

it.each(PANELS)(
  "%s panel: the controls fieldset is disabled while the modifier is off",
  async (key, Comp) => {
    const { container } = render(Comp);
    const controls = container.querySelector(".controls");
    expect(controls).toBeInstanceOf(HTMLFieldSetElement);

    // fresh default config: disabled
    expect(state.config[key].enabled).toBe(false);
    await settle(); // the disabled attribute flushes asynchronously
    expect(controls.disabled).toBe(true);

    state.config[key].enabled = true; // what the card's toggle writes
    await settle();
    expect(controls.disabled).toBe(false);
  }
);

// ---- panel-specific bindings -----------------------------------------------

describe("ReplaceModifier", () => {
  it("writes the search/replace inputs and the option checkboxes into the store", () => {
    const { container } = render(ReplaceModifier);
    const [search, replace] = container.querySelectorAll('input[type="text"]');
    fireEvent.input(search, { target: { value: "foo" } });
    fireEvent.input(replace, { target: { value: "bar" } });
    expect(state.config.replace.search).toBe("foo");
    expect(state.config.replace.replace).toBe("bar");

    const [regex, caseSensitive] = container.querySelectorAll(".check input");
    fireEvent.click(regex);
    fireEvent.click(caseSensitive);
    expect(state.config.replace.regex).toBe(true);
    expect(state.config.replace.case_sensitive).toBe(true);
  });
});

describe("CaseModifier", () => {
  it("lists all ten case modes and writes the choice into the store", () => {
    const { container } = render(CaseModifier);
    const select = container.querySelector("select");
    expect(select.querySelectorAll("option")).toHaveLength(10);
    expect(select.value).toBe("upper"); // the default
    fireEvent.change(select, { target: { value: "snake" } });
    expect(state.config.case.mode).toBe("snake");
  });

  it("disables the controls again when the modifier is disabled", async () => {
    const { container } = render(CaseModifier);
    state.config.case.enabled = true; // enable
    await settle();
    state.config.case.enabled = false; // disable again
    await settle();
    // <fieldset disabled> cascades a real disabled state to every control
    expect(container.querySelector(".controls").disabled).toBe(true);
  });
});

describe("IfThenModifier", () => {
  it("writes the condition and consequence into the store", () => {
    const { container } = render(IfThenModifier);
    const [condSel, actionSel] = container.querySelectorAll("select");
    const [expr, str] = container.querySelectorAll('input[type="text"]');

    // the condition select is one-way (value + inline onchange), not bind:value
    fireEvent.change(condSel, { target: { value: "not" } });
    expect(state.config.ifthen.contains_not).toBe(true);

    fireEvent.input(expr, { target: { value: ".log" } });
    fireEvent.input(str, { target: { value: "x_" } });
    fireEvent.change(actionSel, { target: { value: "suffix" } });
    expect(state.config.ifthen.expression).toBe(".log");
    expect(state.config.ifthen.string).toBe("x_");
    expect(state.config.ifthen.action).toBe("suffix");
  });

  it("shows the position input only when the consequence is an insert", async () => {
    const { container } = render(IfThenModifier);
    // the panel has two selects: the one-way condition select, then the action select
    const [, actionSel] = container.querySelectorAll("select");
    expect(container.querySelector("label.pos input")).toBeNull();

    fireEvent.change(actionSel, { target: { value: "insert" } });
    await settle(); // the {#if} flushes asynchronously
    const pos = container.querySelector("label.pos input");
    expect(pos).toBeTruthy();
    fireEvent.input(pos, { target: { value: "3" } });
    expect(state.config.ifthen.insert_pos).toBe(3);
  });
});

describe("RemoveModifier", () => {
  it("writes the front/back counts into the store", () => {
    const { container } = render(RemoveModifier);
    const [front, back] = container.querySelectorAll('input[type="number"]');
    fireEvent.input(front, { target: { value: "2" } });
    fireEvent.input(back, { target: { value: "3" } });
    expect(state.config.remove.front).toBe(2);
    expect(state.config.remove.back).toBe(3);
  });

  it("enables the range inputs only while range is on; until-end disables the end field", async () => {
    const { container } = render(RemoveModifier);
    const [rangeCb, untilCb] = container.querySelectorAll(".check input");
    const [, , start, end] = container.querySelectorAll('input[type="number"]');

    expect(rangeCb.checked).toBe(false);
    expect(start.disabled).toBe(true);
    expect(end.disabled).toBe(true);
    expect(untilCb.disabled).toBe(true);

    fireEvent.click(rangeCb);
    await settle(); // disabled attributes flush asynchronously
    expect(start.disabled).toBe(false);
    expect(end.disabled).toBe(false);
    expect(untilCb.disabled).toBe(false);

    fireEvent.click(untilCb);
    await settle();
    expect(end.disabled).toBe(true); // "until end" replaces the explicit end
  });
});

describe("AddModifier", () => {
  it("writes the prefix/suffix/insert texts and position into the store", () => {
    const { container } = render(AddModifier);
    const [prefix, suffix, insert] = container.querySelectorAll('input[type="text"]');
    fireEvent.input(prefix, { target: { value: "p-" } });
    fireEvent.input(suffix, { target: { value: "-s" } });
    fireEvent.input(insert, { target: { value: "x" } });
    fireEvent.input(container.querySelector('input[type="number"]'), { target: { value: "1" } });
    expect(state.config.add).toMatchObject({ prefix: "p-", suffix: "-s", insert: "x", insert_pos: 1 });
  });
});

describe("CountingModifier", () => {
  it("writes the position/start/padding into the store", () => {
    const { container } = render(CountingModifier);
    const select = container.querySelector("select");
    fireEvent.change(select, { target: { value: "suffix" } });
    const [start, pad] = container.querySelectorAll('input[type="number"]');
    fireEvent.input(start, { target: { value: "5" } });
    fireEvent.input(pad, { target: { value: "2" } });
    expect(state.config.counting).toMatchObject({ position: "suffix", start: 5, padding: 2 });
  });

  it("shows the insert position only in insert mode", async () => {
    const { container } = render(CountingModifier);
    const select = container.querySelector("select");
    expect(container.querySelectorAll('input[type="number"]')).toHaveLength(2); // start, padding
    fireEvent.change(select, { target: { value: "insert" } });
    await settle(); // the {#if} flushes asynchronously
    expect(container.querySelectorAll('input[type="number"]')).toHaveLength(3); // + insert position
  });

  it("disables the controls again when the modifier is disabled", async () => {
    const { container } = render(CountingModifier);
    state.config.counting.enabled = true; // enable
    await settle();
    state.config.counting.enabled = false; // disable again
    await settle();
    // <fieldset disabled> cascades a real disabled state to every control
    expect(container.querySelector(".controls").disabled).toBe(true);
  });
});

describe("DateModifier", () => {
  it("writes the separators into the store and reveals the picker in custom mode", async () => {
    const { container } = render(DateModifier);
    const [sep, nameSep] = container.querySelectorAll('input[type="text"]');
    fireEvent.input(sep, { target: { value: "." } });
    fireEvent.input(nameSep, { target: { value: " " } });
    expect(state.config.date.separator).toBe(".");
    expect(state.config.date.name_separator).toBe(" ");

    // the panel has three selects: format, source, position
    const [, sourceSel] = container.querySelectorAll("select");
    expect(container.querySelector('input[type="date"]')).toBeNull();
    fireEvent.change(sourceSel, { target: { value: "custom" } });
    await settle(); // the {#if} flushes asynchronously
    expect(container.querySelector('input[type="date"]')).toBeTruthy();
  });

  it("shows the insert position only in insert mode", async () => {
    const { container } = render(DateModifier);
    const [, , positionSel] = container.querySelectorAll("select");
    expect(container.querySelectorAll('input[type="number"]')).toHaveLength(0); // default: suffix/today
    fireEvent.change(positionSel, { target: { value: "insert" } });
    await settle(); // the {#if} flushes asynchronously
    expect(container.querySelectorAll('input[type="number"]')).toHaveLength(1); // + insert position
  });

  it("disables the controls again when the modifier is disabled", async () => {
    const { container } = render(DateModifier);
    state.config.date.enabled = true; // enable
    await settle();
    state.config.date.enabled = false; // disable again
    await settle();
    // <fieldset disabled> cascades a real disabled state to every control
    expect(container.querySelector(".controls").disabled).toBe(true);
  });
});