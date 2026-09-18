# Authoring the slides

One file per act. Edit these; `../index.html` is only a shell and rarely needs
touching.

| File | Act | Slides |
|------|-----|--------|
| `01-title.md` | Title | 1 |
| `02-poll.md` | Audience poll | 3 |
| `03-playbook.md` | The playbook | 1 |
| `04-tax.md` | The Tax | 13 |
| `05-prevent.md` | Prevent | 4 |
| `06-clean.md` | Clean | 3 |
| `07-fix.md` | Fix the root cause | 17 |
| `08-patch.md` | Patch | 6 |
| `09-close.md` | Close | 6 |

Each file is one horizontal column. Slides inside it stack vertically.

## Syntax

````markdown
## A heading

A paragraph. Plain Markdown.

This one is styled and appears on a click.
<!-- .element: class="small mute fragment" -->

- a list
- another item

Note:
Everything after "Note:" is speaker notes. Press S to see them.
They can run to several paragraphs.

---

<!-- .slide: class="center-slide" data-state="act" -->

## The next slide in this act
````

- `---` on its own line starts the next slide (reached with `Down`).
- `Note:` begins the speaker notes for that slide.
- `<!-- .slide: ... -->` sets attributes on the slide itself.
- `<!-- .element: ... -->` sets attributes on the element immediately above it.

## Classes worth knowing

| Class | Does |
|-------|------|
| `fragment` | reveals on click |
| `center-slide` | centres the text |
| `lime` / `mute` / `faint` | text colour |
| `small` / `smaller` / `tiny` | text size |
| `pad-top` | space above |
| `kicker` | the small uppercase label above a heading |
| `panel` + `good` / `bad` | a bordered box |
| `cols` | side-by-side children |
| `checklist` | the numbered takeaway list |

## The act spine

Act dividers show the four-layer spine. Don't write it out — one line does it:

```html
<div class="spine" data-act="2"></div>
```

`data-act` takes `all` (every layer lit — the playbook map), `1`–`4` (that
layer lit, earlier ones dimmed as done), or `done` (all four finished).

## Images and diagrams

Always wrap them in `<figure>`:

```html
<figure>
  <img src="assets/images/thing.jpg" alt="...">
</figure>
```

A bare `<img>` or `<svg>` is *inline* to the Markdown renderer, so it gets
wrapped in a `<p>` and inherits the slide's left alignment and paragraph
margins. `<figure>` is block-level and the theme already centres it and caps
its height.

## Gotcha

Don't put `<!--` or `-->` inside another HTML comment. The first inner `-->`
closes the outer comment and the remainder renders as visible text on the
slide. (In this file they are safe because they sit inside code fences.)

## Previewing

```bash
python3 -m http.server 8000   # from the repo root, then open localhost:8000
```

A plain `file://` open will not work — the Markdown files are fetched over
HTTP.
