# The Partition Tax

A playbook for right-sizing your Kafka clusters — talk slides for **Current 2026**.

**View the deck:** https://chuck-alt-delete.github.io/partition-tax

## The talk

Internal research across sophisticated Kafka users suggests 40–70% of cluster
spend is wasted on excess partitions. These aren't beginners — Kafka simply
makes over-provisioning the path of least resistance, and once a topic is keyed,
you can't take partitions back.

The deck lays out four layers, organised by who can act and when:

| Layer | Who acts | When |
|-------|----------|------|
| **Prevent** | platform team | at provisioning |
| **Clean** | app teams | quarterly |
| **Fix** | app teams | at design time |
| **Patch** | platform team | without app changes |

## Running it locally

Needs a web server — opening `index.html` over `file://` will fail to load the
diagrams.

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

## Presenting

The deck is two-dimensional: **each act is a horizontal column, and its slides
run vertically beneath it.**

```
Title → Poll → Playbook → The Tax → Prevent → Clean → Fix → Patch → Close
  ·      ↓        ·          ↓         ↓        ↓      ↓      ↓       ↓
  1      3        1         13         4        3     17      6       6
```

The title stands alone with nothing beneath it, so `Down` does nothing there —
press `Right` to begin. The playbook slide is also its own column, so one
`Left` brings the map back up during Q&A.

| Key | Does |
|-----|------|
| `Space` / `↓` | advance normally — fragment by fragment, then the next slide in the act |
| `→` | jump to the next act, skipping any fragments still pending |
| `←` | back to the previous act |
| `↑` | back one slide within the act |
| `S` | speaker view — notes, timer, next slide |
| `F` | fullscreen |
| `O` | overview — the whole grid at once |
| `.` | black the screen |
| `Alt`+click | zoom into a diagram |

`→` deliberately ignores pending fragments (reveal's default walks them first),
so it is a dependable way to cut an act short when you are running long.

Speaker notes are embedded in `index.html` as `<aside class="notes">`. The
longer-form narrative script lives in [`notes/script.md`](notes/script.md).

### Export to PDF

Open <http://localhost:8000/?print-pdf> and print to PDF from the browser.

## Layout

```
content/*.md            THE SLIDES — one Markdown file per act. Edit these.
content/README.md       authoring syntax: separators, notes, attributes
index.html              shell only — loads the content files, ~110 lines
css/theme.css           theme, built on Conduktor's palette (#072024 / #bcfe68)
assets/diagrams/*.svg   diagrams, authored for projection not for a blog column
lib/reveal/             reveal.js 5.2.1, vendored — the deck must work offline
notes/script.md         speaker script and timing plan
tools/                  the one-shot HTML→Markdown migration script
```

Slide content lives in `content/`, not in `index.html`. Each file is one act;
`---` on its own line starts the next slide and `Note:` begins the speaker
notes. See [`content/README.md`](content/README.md).

reveal.js is committed rather than pulled from a CDN, deliberately: conference
wifi is not a dependency worth taking.

The Pages workflow stamps every local asset URL with the commit SHA at deploy
time (`css/theme.css?v=<sha>`). GitHub Pages serves assets with
`cache-control: max-age=600`, so without that a browser can keep showing a
stale stylesheet or diagram for ten minutes after a deploy. The committed
source stays clean — the stamping happens in CI, not in the repo.

## Sources

Every figure in the deck is on the final Sources slide. The two background
posts are [The Surprising Cost of Kafka Partition Waste](https://www.conduktor.io/blog/the-surprising-cost-of-kafka-partition-waste)
and [Kafka Partitions are the Wrong Ordering Abstraction, Keys Are](https://www.conduktor.io/blog/kafka-partitions-are-the-wrong-ordering-abstraction-keys-are).

## Licence

Slide content © Chuck Larrieu Casias. reveal.js is MIT — see `lib/reveal/LICENSE`.
