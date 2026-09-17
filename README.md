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

| Key | Does |
|-----|------|
| `S` | speaker view — notes, timer, next slide |
| `F` | fullscreen |
| `O` | slide overview |
| `.` | black the screen |
| `Alt`+click | zoom into a diagram |

Speaker notes are embedded in `index.html` as `<aside class="notes">`. The
longer-form narrative script lives in [`notes/script.md`](notes/script.md).

### Export to PDF

Open <http://localhost:8000/?print-pdf> and print to PDF from the browser.

## Layout

```
index.html              the deck — all 54 slides, with speaker notes
css/theme.css           theme, built on Conduktor's palette (#072024 / #bcfe68)
assets/diagrams/*.svg   diagrams, authored for projection not for a blog column
lib/reveal/             reveal.js 5.2.1, vendored — the deck must work offline
notes/script.md         speaker script and timing plan
```

reveal.js is committed rather than pulled from a CDN, deliberately: conference
wifi is not a dependency worth taking.

## Sources

Every figure in the deck is on the final Sources slide. The two background
posts are [The Surprising Cost of Kafka Partition Waste](https://www.conduktor.io/blog/the-surprising-cost-of-kafka-partition-waste)
and [Kafka Partitions are the Wrong Ordering Abstraction, Keys Are](https://www.conduktor.io/blog/kafka-partitions-are-the-wrong-ordering-abstraction-keys-are).

## Licence

Slide content © Chuck Larrieu Casias. reveal.js is MIT — see `lib/reveal/LICENSE`.
