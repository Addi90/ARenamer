// English UI strings (source of truth). Flat, namespaced keys; `{var}` placeholders
// are interpolated by `t()`. German lives in `de.js` (identical key set).

export const en = {
  // header / path bar
  "app.title": "A-Renamer Tool",
  "app.subtitle": "Select files and directories, configure modifiers, preview the new names, then rename.",
  "app.home": "Home",
  "app.homeTitle": "Open the home directory",
  "app.up": "Up",
  "app.upTitle": "Open the parent directory",
  "app.open": "Open",

  // language switcher (option labels stay in their own language)
  "lang.label": "Language",

  // shared across components
  "common.loading": "Loading…",
  "common.regex": "Regex",
  "common.caseSensitive": "Case sensitive",
  "common.pos": "Pos.",

  // modifiers sidebar
  "modifiers.title": "Modifiers",
  "modifiers.dragHint": "Drag cards to change the pipeline order",
  "modifiers.resetOrder": "Reset order",

  // file list
  "fileList.selectAll": "Select all",
  "fileList.clear": "Clear",
  "fileList.toggleFiles": "Files",
  "fileList.toggleDirs": "Directories",
  "fileList.name": "Name",
  "fileList.newName": "New Name",
  "fileList.empty": "No entries in this directory.",

  // directory tree
  "tree.directories": "Directories",
  "tree.empty": "No directory tree available.",
  "tree.expand": "Expand",
  "tree.collapse": "Collapse",

  // rename workflow (button + dialogs)
  "rename.button": "Rename",
  "rename.renaming": "Renaming…",
  "rename.dupTitle": "Warning",
  "rename.dupMsg": "Found existing entries for {n} new name(s)!",
  "rename.confirmTitle": "Rename",
  "rename.confirmMsg": "Rename {n} Item(s)?",
  "rename.successTitle": "Done",
  "rename.successMsg": "Successfully renamed {n} Item(s)!",
  "rename.errorNote": "{n} item(s) could not be renamed.",

  // dialog buttons
  "dialog.ok": "Ok",
  "dialog.abort": "Abort",

  // replace modifier
  "replace.title": "Replace",
  "replace.search": "Search",
  "replace.replaceWith": "Replace with",
  "replace.searchPh": "e.g. _old",
  "replace.replacePh": "e.g. _new",

  // case modifier
  "case.title": "Case",
  "case.mode": "Mode",
  "case.upper": "UPPERCASE",
  "case.lower": "lowercase",
  "case.titleCase": "Title Case",
  "case.sentenceCase": "Sentence case",
  "case.camel": "camelCase",
  "case.pascal": "PascalCase",
  "case.snake": "snake_case",
  "case.kebab": "kebab-case",
  "case.constant": "CONSTANT_CASE",
  "case.train": "train case",

  // if-then modifier
  "ifthen.title": "If-Then",
  "ifthen.ifTag": "If",
  "ifthen.thenTag": "Then",
  "ifthen.condTitle": "Condition — tested against the original name",
  "ifthen.consTitle": "Consequence — applied when the condition matches",
  "ifthen.contains": "Contains",
  "ifthen.notContains": "Does not contain",
  "ifthen.exprPh": "e.g. report",
  "ifthen.stringPh": "e.g. [archived]",
  "ifthen.asPrefix": "as prefix",
  "ifthen.atPosition": "at position",
  "ifthen.asSuffix": "as suffix",

  // remove modifier
  "remove.title": "Remove",
  "remove.first": "First",
  "remove.last": "Last",
  "remove.firstTitle": "Remove the first n characters",
  "remove.lastTitle": "Remove the last n characters",
  "remove.range": "Character range",
  "remove.from": "From",
  "remove.to": "To",
  "remove.fromTitle": "1-based position of the first character to remove",
  "remove.toTitle": "1-based position of the last character to remove",
  "remove.untilEnd": "until end",

  // add / insert modifier
  "add.title": "Add / Insert",
  "add.prefix": "Prefix",
  "add.suffix": "Suffix",
  "add.insert": "Insert",
  "add.prefixPh": "e.g. IMG_",
  "add.suffixPh": "e.g. _final",
  "add.insertPh": "e.g. -copy",

  // position select (shared by counting + date)
  "position.prefix": "Prefix",
  "position.suffix": "Suffix",
  "position.insert": "At position",

  // counting / number modifier
  "counting.title": "Number",
  "counting.start": "Start",
  "counting.startTitle": "First number in the sequence (files are numbered in list order)",
  "counting.pad": "Pad",
  "counting.padTitle": "Zero-pad the number to this width (e.g. 3 → 001)",
  "counting.insertAt": "Insert at position",

  // date modifier (format options DD-MM-YYYY etc. are codes, not translated)
  "date.title": "Date",
  "date.separator": "Date separator",
  "date.sepTitle": "Character between day, month and year",
  "date.nameSeparator": "Name separator",
  "date.nameSepTitle": "Character between the date and the rest of the name (empty = none)",
  "date.created": "Created",
  "date.modified": "Last modified",
  "date.today": "Today",
  "date.custom": "Custom date…",
};
