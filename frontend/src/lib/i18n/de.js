// German UI strings. Wording is taken from the original Qt app's translation file
// (`ARenamerTool/languages/ARenamerTool_de_DE.ts`), modernized to standard German
// capitalization (the original used all-caps / lowercase in places). Same key set as en.js.

export const de = {
  // header / path bar
  "app.title": "A-Renamer Tool",
  "app.subtitle": "Dateien auswählen, Modifikatoren konfigurieren, neue Namen in der Vorschau prüfen und dann umbenennen.",
  "app.home": "Home",
  "app.homeTitle": "Das Home-Verzeichnis öffnen",
  "app.up": "Hoch",
  "app.upTitle": "Das übergeordnete Verzeichnis öffnen",
  "app.open": "Öffnen",

  // language switcher (option labels stay in their own language)
  "lang.label": "Sprache",

  // shared across components
  "common.loading": "Wird geladen…",
  "common.regex": "Regex",
  "common.caseSensitive": "Groß-/Kleinschr. beachten",
  "common.pos": "Pos.",

  // modifiers sidebar
  "modifiers.title": "Modifikatoren",

  // file list
  "fileList.selectAll": "Alle auswählen",
  "fileList.clear": "Auswahl aufheben",
  "fileList.name": "Name",
  "fileList.newName": "Neuer Name",
  "fileList.empty": "Keine Dateien in diesem Verzeichnis.",

  // directory tree
  "tree.directories": "Verzeichnisse",
  "tree.empty": "Kein Verzeichnisbaum verfügbar.",
  "tree.expand": "Aufklappen",
  "tree.collapse": "Zuklappen",

  // rename workflow (button + dialogs)
  "rename.button": "Umbenennen",
  "rename.renaming": "Wird umbenannt…",
  "rename.dupTitle": "Warnung",
  "rename.dupMsg": "Für {n} neue(n) Dateinamen bereits existierende Datei(en) mit selbem Namen gefunden!",
  "rename.confirmTitle": "Umbenennen",
  "rename.confirmMsg": "Benenne {n} Datei(en) um?",
  "rename.successTitle": "Fertig",
  "rename.successMsg": "Erfolgreich {n} Datei(en) umbenannt!",
  "rename.errorNote": "{n} Datei(en) konnten nicht umbenannt werden.",

  // dialog buttons
  "dialog.ok": "OK",
  "dialog.abort": "Abbrechen",

  // replace modifier
  "replace.title": "Ersetzen",
  "replace.search": "Suche",
  "replace.replaceWith": "Ersetzen mit",
  "replace.searchPh": "z. B. _old",
  "replace.replacePh": "z. B. _new",

  // case modifier
  "case.title": "Groß-/Kleinschreibung",
  "case.mode": "Modus",
  "case.upper": "GROSSBUCHSTABEN",
  "case.lower": "kleinschreibung",
  "case.titleCase": "Titel-Großschreibung",
  "case.sentenceCase": "Satz-Großschreibung",
  "case.camel": "camelCase",
  "case.pascal": "PascalCase",
  "case.snake": "snake_case",
  "case.kebab": "kebab-case",
  "case.constant": "CONSTANT_CASE",
  "case.train": "train case",

  // if-then modifier
  "ifthen.title": "Wenn-Dann",
  "ifthen.ifTag": "WENN",
  "ifthen.thenTag": "DANN",
  "ifthen.condTitle": "Bedingung – wird am ursprünglichen Namen geprüft",
  "ifthen.consTitle": "Folge – wird angewendet, wenn die Bedingung zutrifft",
  "ifthen.contains": "Enthält",
  "ifthen.notContains": "Enthält nicht",
  "ifthen.exprPh": "z. B. report",
  "ifthen.stringPh": "z. B. [archiviert]",
  "ifthen.asPrefix": "als Präfix",
  "ifthen.atPosition": "an Position",
  "ifthen.asSuffix": "als Suffix",

  // remove modifier
  "remove.title": "Entfernen",
  "remove.first": "Anfang",
  "remove.last": "Ende",
  "remove.firstTitle": "Entferne die ersten n Zeichen",
  "remove.lastTitle": "Entferne die letzten n Zeichen",
  "remove.range": "Zeichenbereich",
  "remove.from": "Von",
  "remove.to": "Bis",
  "remove.fromTitle": "Position (ab 1) des ersten zu entfernenden Zeichens",
  "remove.toTitle": "Position (ab 1) des letzten zu entfernenden Zeichens",
  "remove.untilEnd": "bis Ende",

  // add / insert modifier
  "add.title": "Hinzufügen/Einfügen",
  "add.prefix": "Präfix",
  "add.suffix": "Suffix",
  "add.insert": "Einfügen",
  "add.prefixPh": "z. B. IMG_",
  "add.suffixPh": "z. B. _final",
  "add.insertPh": "z. B. -copy",

  // position select (shared by counting + date)
  "position.prefix": "Präfix",
  "position.suffix": "Suffix",
  "position.insert": "An Position",

  // counting / number modifier
  "counting.title": "Nummerierung",
  "counting.start": "Start",
  "counting.startTitle": "Erste Nummer der Sequenz (Dateien werden in Listenreihenfolge nummeriert)",
  "counting.pad": "Auffüllen",
  "counting.padTitle": "Nummer mit Nullen auf diese Breite auffüllen (z. B. 3 → 001)",
  "counting.insertAt": "An Position einfügen",

  // date modifier (format options DD-MM-YYYY etc. are codes, not translated)
  "date.title": "Datum",
  "date.separator": "Datums-Trennzeichen",
  "date.sepTitle": "Zeichen zwischen Tag, Monat und Jahr",
  "date.nameSeparator": "Namens-Trennzeichen",
  "date.nameSepTitle": "Zeichen zwischen Datum und Rest des Namens (leer = keines)",
  "date.created": "Erstellt",
  "date.modified": "Zuletzt geändert",
  "date.today": "Heute",
  "date.custom": "Benutzerdefiniert…",
};
