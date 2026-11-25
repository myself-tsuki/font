# font

A small, self-hosted font collection served free from GitHub + jsDelivr.
Every family, weight, style, variable axis and file is listed in one machine-readable index: **[`fonts.json`](fonts.json)**.

Want to add a font? See **[CONTRIBUTING.md](CONTRIBUTING.md)**.

| Family | Weights | Styles | Axes | License |
| --- | --- | --- | --- | --- |
| Google Sans | 400–700 | normal, italic | `wght` 400–700, `opsz` 17–18, `GRAD` −50–200 | OFL 1.1 |
| Figtree | 300–900 | normal, italic | `wght` 300–900 | OFL 1.1 |
| Outfit | 100–900 | normal | `wght` 100–900 | OFL 1.1 |
| Plus Jakarta Sans | 200–800 | normal, italic | `wght` 200–800 | OFL 1.1 |
| Nunito | 200–1000 | normal, italic | `wght` 200–1000 | OFL 1.1 |
| Inter | 100–900 | normal, italic | `wght` 100–900, `opsz` 14–32 | OFL 1.1 |
| Atkinson Hyperlegible Next | 200–800 | normal, italic | `wght` 200–800 | OFL 1.1 |
| Satoshi\* | 300–900 | normal, italic | `wght` 300–900 | ITF Free Font License |

\* **Satoshi is listed but not hosted here.** Its license (ITF Free Font License) does not allow re-hosting the files in a public repository, so `fonts.json` points to the official Fontshare CSS and download instead (`"hosted": false`).

All other fonts are variable fonts (one file covers every weight) from [Google Fonts](https://github.com/google/fonts), released under the SIL Open Font License 1.1. Each folder in `fonts/` includes its `OFL.txt`.

---

## Use a font on a website

### Option 1: one `<link>` per family

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/myself-tsuki/font@main/css/figtree.css">

<style>
  body { font-family: 'Figtree', sans-serif; font-weight: 450; }
  h1   { font-weight: 800; }
  em   { font-style: italic; }
</style>
```

Available stylesheets (`css/<slug>.css`):
`google-sans.css`, `figtree.css`, `outfit.css`, `plus-jakarta-sans.css`, `nunito.css`, `inter.css`, `atkinson-hyperlegible-next.css`

All of them at once: `https://cdn.jsdelivr.net/gh/myself-tsuki/font@main/css/all.css`

Satoshi (official CDN):

```html
<link rel="stylesheet" href="https://api.fontshare.com/v2/css?f[]=satoshi@1,2&display=swap">
```

### Option 2: CSS `@import`

```css
@import url('https://cdn.jsdelivr.net/gh/myself-tsuki/font@main/css/google-sans.css');

.title {
  font-family: 'Google Sans', sans-serif;
  font-variation-settings: 'GRAD' 50; /* extra variable axes */
}
```

### Option 3: your own `@font-face`

```css
@font-face {
  font-family: 'Nunito';
  src: url('https://cdn.jsdelivr.net/gh/myself-tsuki/font@main/fonts/Nunito/Nunito-VariableFont_wght.ttf') format('truetype');
  font-weight: 200 1000;
  font-style: normal;
  font-display: swap;
}
```

---

## Fetch the index with JavaScript

```js
const res = await fetch('https://cdn.jsdelivr.net/gh/myself-tsuki/font@main/fonts.json');
const { fonts } = await res.json();

// List every family and its variants
for (const f of fonts) {
  console.log(f.family, f.weights, f.styles, f.axes.map(a => a.tag));
}

// Load a font on the fly and use it
const outfit = fonts.find(f => f.slug === 'outfit');
const link = Object.assign(document.createElement('link'), { rel: 'stylesheet', href: outfit.css });
document.head.append(link);
document.body.style.fontFamily = `'${outfit.family}', sans-serif`;
```

Or load a file directly with the FontFace API:

```js
const file = outfit.files[0];
const face = new FontFace(outfit.family, `url(${file.url})`, {
  weight: `${file.axes[0].min} ${file.axes[0].max}`,
  style: file.style,
});
document.fonts.add(await face.load());
```

### `fonts.json` shape

```jsonc
{
  "cdn": "https://cdn.jsdelivr.net/gh/myself-tsuki/font@main/",
  "allCss": ".../css/all.css",
  "count": 8,
  "fonts": [
    {
      "family": "Figtree",
      "slug": "figtree",
      "category": "sans-serif",
      "designer": "Erik Kennedy",
      "license": "SIL Open Font License 1.1",
      "source": "https://fonts.google.com/specimen/Figtree",
      "hosted": true,                    // false = not in this repo (see "download")
      "css": ".../css/figtree.css",      // ready-made @font-face stylesheet
      "axes": [{ "tag": "wght", "min": 300, "max": 900, "default": 300 }],
      "weights": [300, 400, 500, 600, 700, 800, 900],
      "styles": ["normal", "italic"],
      "files": [
        {
          "file": "fonts/Figtree/Figtree-VariableFont_wght.ttf",
          "style": "normal",
          "variable": true,
          "format": "truetype",
          "version": "2.002",
          "axes": [ ... ],
          "weights": [ ... ],
          "size": 62712,
          "url": "https://cdn.jsdelivr.net/gh/...",       // CDN (fast, cached)
          "raw": "https://raw.githubusercontent.com/..."   // direct from GitHub
        }
      ]
    }
  ]
}
```

---

## Download

- **Single file:** open any `url` / `raw` link from `fonts.json`, or browse `fonts/<Family>/` on GitHub and click *Download raw file*.
- **Command line:**
  ```sh
  curl -LO "https://raw.githubusercontent.com/myself-tsuki/font/main/fonts/Outfit/Outfit-VariableFont_wght.ttf"
  ```
- **Everything:** `git clone https://github.com/myself-tsuki/font.git` or *Code → Download ZIP*.
- **Satoshi:** https://www.fontshare.com/fonts/satoshi

Double-click a `.ttf` to install it on your computer (Windows, macOS and Linux).

---

## Repository layout

```
fonts/<Family>/          variable font files + OFL.txt
*.ttf (repo root)        Inter and Atkinson Hyperlegible Next (original uploads, kept in place)
css/<slug>.css           @font-face stylesheet per family
css/all.css              every family in one stylesheet
fonts.json               index of all families, variants and URLs
scripts/build_index.py   regenerates fonts.json and css/
```

## Adding a font / contributing

Want a font added? Read the full guide in **[CONTRIBUTING.md](CONTRIBUTING.md)**. It covers license rules, where files go, naming conventions, regenerating the index, testing, and what to include in a pull request.

Short version:

1. Check that the license allows redistribution (OFL is fine; Fontshare fonts like Satoshi are not).
2. Put the files in `fonts/<FamilyName>/` with `OFL.txt`, named `<FamilyName>-VariableFont_<axes>.ttf`.
3. Run `pip install fonttools && python3 scripts/build_index.py`.
4. Open a PR titled `Add <Family Name>` that includes the source URL, license and version.

## Licenses

Fonts are the property of their designers. The OFL fonts may be used, shared and embedded freely, including commercially; see each `OFL.txt`. Satoshi is © Indian Type Foundry and must be obtained from Fontshare.
