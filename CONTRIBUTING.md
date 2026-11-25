# Contributing: adding a new font

Thanks for helping grow the collection. This guide walks through adding a font family from start to pull request. Most additions take about ten minutes.

- [1. Check the license first](#1-check-the-license-first)
- [2. Get the font files](#2-get-the-font-files)
- [3. Where the files go](#3-where-the-files-go)
- [4. Naming conventions](#4-naming-conventions)
- [5. Add metadata (optional)](#5-add-metadata-optional)
- [6. Regenerate the index and CSS](#6-regenerate-the-index-and-css)
- [7. Test it](#7-test-it)
- [8. Open a pull request](#8-open-a-pull-request)
- [Fonts that can't be hosted (like Fontshare fonts)](#fonts-that-cant-be-hosted-like-fontshare-fonts)
- [Updating an existing font](#updating-an-existing-font)
- [Troubleshooting](#troubleshooting)

---

## 1. Check the license first

This repo is public, and every file in it is redistributed. Only add font **files** whose license allows that.

| License | Can the files go in this repo? |
| --- | --- |
| SIL Open Font License 1.1 (OFL), which covers almost everything on Google Fonts | **Yes.** Include `OFL.txt`. |
| Fontshare / ITF Free Font License (General Sans, Clash Display…) | **No.** List it as an external font instead ([see below](#fonts-that-cant-be-hosted-like-fontshare-fonts)). |
| Commercial, "free for personal use", or no license stated | **No.** Don't add it at all. |

`scripts/build_index.py` labels every hosted family as `SIL Open Font License 1.1`. If you want to add a font under another redistributable license (for example Apache 2.0), open an issue first so the script can be updated to read that license.

## 2. Get the font files

Prefer the **official source**, and the **variable** version when one exists: one file covers every weight, so it is smaller in total and simpler to use.

**From Google Fonts** (recommended). Google's [`google/fonts`](https://github.com/google/fonts) repo has the exact release files and license for every family under `ofl/<familyname>/`, all lowercase without spaces:

```sh
# Example: Manrope
curl -L -o "Manrope[wght].ttf" "https://raw.githubusercontent.com/google/fonts/main/ofl/manrope/Manrope%5Bwght%5D.ttf"
curl -L -O "https://raw.githubusercontent.com/google/fonts/main/ofl/manrope/OFL.txt"
```

To see what files a family has:

```sh
curl -s https://api.github.com/repos/google/fonts/contents/ofl/manrope | grep '"name"'
```

You can also use **Download family** on fonts.google.com. The zip contains the variable files plus a `static/` folder; use the variable files.

**Formats:** add **one format per style**, preferably `.ttf` (`.otf`, `.woff2` and `.woff` also work). Don't add both `Font.ttf` and `Font.woff2` for the same style, or the generated CSS will contain duplicate `@font-face` rules.

## 3. Where the files go

```
fonts/
└── <FamilyName>/                         one folder per family, PascalCase, no spaces
    ├── <FamilyName>-VariableFont_wght.ttf
    ├── <FamilyName>-Italic-VariableFont_wght.ttf   (if the family has italics)
    └── OFL.txt                                     required: the font's license
```

Real examples already in the repo:

```
fonts/Figtree/Figtree-VariableFont_wght.ttf
fonts/Figtree/Figtree-Italic-VariableFont_wght.ttf
fonts/Figtree/OFL.txt
fonts/GoogleSans/GoogleSans-VariableFont_GRAD,opsz,wght.ttf
fonts/Outfit/Outfit-VariableFont_wght.ttf
```

Rules:

- **New fonts go in `fonts/<FamilyName>/`.** Never put font files in the repository root; every family, including Inter and Atkinson Hyperlegible Next, lives in its own folder.
- **One family per folder.** Keep the license in the same folder; the index links to it from there.
- **Don't edit `fonts.json` or `css/` by hand.** They are generated (step 6).

## 4. Naming conventions

Folder and file names become URLs, so keep them predictable. Use the same pattern Google Fonts uses for its downloads:

| Kind | Pattern | Example |
| --- | --- | --- |
| Folder | `fonts/<FamilyName>/`, PascalCase, no spaces | `fonts/PlusJakartaSans/` |
| Variable, upright | `<FamilyName>-VariableFont_<axes>.ttf` | `Nunito-VariableFont_wght.ttf` |
| Variable, italic | `<FamilyName>-Italic-VariableFont_<axes>.ttf` | `Nunito-Italic-VariableFont_wght.ttf` |
| Static (only if there's no variable version) | `<FamilyName>-<Weight>.ttf` | `Manrope-SemiBold.ttf` |
| Static italic | `<FamilyName>-<Weight>Italic.ttf` | `Manrope-SemiBoldItalic.ttf` |

- `<axes>` lists the axis tags in the file's original order, separated by commas, for example `opsz,wght` or `GRAD,opsz,wght`.
- Weight names: `Thin` 100, `ExtraLight` 200, `Light` 300, `Regular` 400, `Medium` 500, `SemiBold` 600, `Bold` 700, `ExtraBold` 800, `Black` 900.
- Files from `google/fonts` use square brackets (`Manrope[wght].ttf`). **Rename them** to the pattern above, because brackets in URLs are awkward:

  ```sh
  mv "Manrope[wght].ttf"        Manrope-VariableFont_wght.ttf
  mv "Manrope-Italic[wght].ttf" Manrope-Italic-VariableFont_wght.ttf   # only if the family has an italic file (Manrope doesn't)
  ```

You don't choose the family name, slug or style yourself. The script reads them from the font file:

- **Family name** (`"family"`, and the CSS `font-family`): the typographic family name inside the font (for example `Plus Jakarta Sans`).
- **Slug** (`"slug"`, and the stylesheet name `css/<slug>.css`): the family name, lowercased, with spaces replaced by hyphens (`plus-jakarta-sans`).
- **Style**: the file counts as `italic` if the font says so, or if its file name contains `Italic`.
- **Weights and axes**: read from the variable axes (or from the weight class of a static file).

## 5. Add metadata (optional)

The font files don't record a category, designer or specimen link. To include them in `fonts.json`, add an entry to the `META` dictionary at the top of `scripts/build_index.py`. The key must match the family name exactly:

```python
META = {
    # ...
    "Manrope": {"category": "sans-serif", "designer": "Mikhail Sharanda", "source": "https://fonts.google.com/specimen/Manrope"},
}
```

Use one of these categories: `sans-serif`, `serif`, `display`, `handwriting`, `monospace`.

## 6. Regenerate the index and CSS

You need Python 3 and fontTools:

```sh
pip install fonttools
python3 scripts/build_index.py
```

It should print something like `Indexed 9 families, 14 files`, and it updates:

- `fonts.json`: adds your family with its axes, weights, styles and the CDN and raw-GitHub URLs of every file
- `css/<slug>.css`: an `@font-face` stylesheet for your family
- `css/all.css`: every family in one stylesheet

Then add your family to the table at the top of `README.md` and to its list of available stylesheets.

## 7. Test it

**Check the index:**

```sh
python3 -c "import json; [print(f['family'], f['weights'], f['styles']) for f in json.load(open('fonts.json'))['fonts']]"
cat css/manrope.css
```

Confirm that your family appears once, with the weights and styles you expect (for example both `normal` and `italic`).

**Check it renders.** Create a throwaway `test.html` in the repo root. It points at your local files, because the CDN URLs only work once the files are merged:

```html
<!doctype html>
<style>
  @font-face { font-family: 'Test'; src: url('fonts/Manrope/Manrope-VariableFont_wght.ttf'); font-weight: 200 800; }
  p { font-family: 'Test', monospace; font-size: 32px; }
</style>
<p style="font-weight:200">ExtraLight 200: The quick brown fox</p>
<p style="font-weight:400">Regular 400: The quick brown fox</p>
<p style="font-weight:800">ExtraBold 800: The quick brown fox</p>
```

Serve the folder with `python3 -m http.server` and open http://localhost:8000/test.html. If the text shows in a monospace font, the font didn't load. Delete `test.html` before you commit.

## 8. Open a pull request

1. Fork the repo and create a branch, for example `add-manrope`.
2. Commit these files:
   - `fonts/<FamilyName>/`: the font files and the license
   - `fonts.json` and `css/`: regenerated, never edited by hand
   - `scripts/build_index.py`: only if you added `META`
   - `README.md`: the table row and the stylesheet list
3. Title the PR **`Add <Family Name>`** (for example `Add Manrope`). Use `Update <Family Name> to <version>` for updates.
4. In the description, include:
   - **Source:** the exact URL the files came from
   - **License:** for example `OFL 1.1`, with confirmation that `OFL.txt` is included
   - **Version:** shown as `"version"` in `fonts.json`
   - **Files:** variable or static, and which styles (upright, italic)
   - **Checks:** confirmation that you ran `build_index.py` and checked rendering

Template:

```markdown
## Add Manrope

- Source: https://github.com/google/fonts/tree/main/ofl/manrope
- License: SIL OFL 1.1 (fonts/Manrope/OFL.txt included)
- Version: 4.505
- Files: variable, wght 200–800, upright only (no italic upstream)

- [x] Files renamed to the repo's naming convention
- [x] `python3 scripts/build_index.py` run; fonts.json and css/ regenerated
- [x] Tested rendering locally at 200 / 400 / 800
- [x] README table and stylesheet list updated
```

A PR will be asked for changes if it includes files without a redistributable license, a missing license file, a hand-edited `fonts.json`, files outside `fonts/<FamilyName>/`, or duplicate formats of the same style.

---

## Fonts that can't be hosted (like Fontshare fonts)

Some fonts are free to use but not to redistribute. Fontshare fonts are an example: their ITF Free Font License forbids hosting the files in a public repository. These fonts can still be listed in `fonts.json`, pointing at the official source, so people can find them.

**Don't commit the files.** Add an entry to the `EXTERNAL` list in `scripts/build_index.py`:

```python
EXTERNAL = [
    {
        "family": "General Sans",
        "slug": "general-sans",
        "category": "sans-serif",
        "designer": "Frode Helland, Indian Type Foundry",
        "license": "ITF Free Font License (no redistribution)",
        "source": "https://www.fontshare.com/fonts/general-sans",
        "hosted": False,
        "note": "The license forbids re-hosting the files, so they are not in this repo.",
        "css": "https://api.fontshare.com/v2/css?f[]=general-sans@1,2&display=swap",
        "download": "https://api.fontshare.com/v2/fonts/download/general-sans",
        "axes": [{"tag": "wght", "min": 200, "max": 700, "default": 400}],
        "weights": [200, 300, 400, 500, 600, 700],
        "styles": ["normal", "italic"],
        "files": [],
    },
]
```

Open the `css` URL in a browser to check that it works before you submit. Then run the script and add the font to the README table, marked with `*` and a note that it is not hosted here.

## Updating an existing font

1. Download the new release from the same source.
2. Replace the files in `fonts/<FamilyName>/` and keep the same file names, so links people already use keep working. Update `OFL.txt` too if it changed.
3. Run `python3 scripts/build_index.py`. The `"version"` field picks up the new version automatically.
4. Open a PR titled `Update <Family Name> to <version>`.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `ModuleNotFoundError: No module named 'fontTools'` | `pip install fonttools` (on Debian/Ubuntu you may need `pip install --break-system-packages fonttools`, or use a virtualenv) |
| The family appears twice in `fonts.json` | The two files report different family names. Run `python3 -c "from fontTools.ttLib import TTFont; print(TTFont('path.ttf')['name'].getDebugName(16) or TTFont('path.ttf')['name'].getDebugName(1))"` on each file, and use files from the same release. |
| The italic file is listed as `normal` | Put `Italic` in the file name (see the naming table). |
| Two `@font-face` rules for the same style | You added two formats of the same file; keep only one. |
| `"licenseFile": null` | `OFL.txt` is missing from the family's folder. |
| The CDN URL returns 404 right after merging | The jsDelivr CDN caches `@main` for a while. The `raw` GitHub URL works immediately. |
