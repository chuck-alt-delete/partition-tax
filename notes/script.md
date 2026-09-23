# The Partition Tax — speaker script and timing

40-minute slot plus 5 minutes Q&A. 55 slides, but a dozen of those are act
dividers and single-line beats that take seconds. Realistic pace is ~45s/slide
with the interactive opener absorbing the slack.

## Timing plan

The deck is laid out in two dimensions: **each act is a horizontal column,
and its slides run vertically beneath it.**

| → | Act | Slides deep | Target | Running |
|---|-----|-------------|--------|---------|
| 1 | Title | 1 | 0:30 | 0:30 |
| 2 | The playbook | 1 | 1:00 | 1:30 |
| 3 | Audience poll | 3 | 3:00 | 4:30 |
| 4 | The Tax | 15 | 10:30 | 15:00 |
| 5 | Prevent | 4 | 3:00 | 18:00 |
| 6 | Clean | 4 | 3:00 | 21:00 |
| 7 | Optimize the consumer | 14 | 13:00 | 34:00 |
| 8 | Patch | 7 | 4:00 | 38:00 |
| 9 | Takeaways | 6 | 2:00 | 40:00 |

Title and playbook stand alone — nothing sits beneath them, so `Down` does
nothing there and you move on with `Right`.

**Driving it:** `Space` or `Down` to advance normally, fragment by fragment.
`Right` jumps straight to the next act — it ignores any fragments still pending
on the current slide, so it is a reliable "I am out of time, move on" key.
`Left` goes back an act. `T` (or the Contents button, top left) opens a
clickable index of every act and slide — the fastest way to reach a specific
slide during Q&A. `O` shows the whole grid.

Because Right skips an act outright, the cut list below is executable live: if
you are three minutes down entering Prevent, press Right twice and you are in
Optimize with the whole argument intact.

**If you are running long**, cut in this order:

1. Act 8's proxy-mechanism slide (the metadata rewrite) — say it in one sentence
2. Act 4's per-broker cost list — the Jun Rao quote alone carries it
3. Act 7's "what share consumers actually give you" — go straight to the
   out-of-order quote
4. Act 8's Lie 3 mechanism diagram — keep the framing slide, drop the how

**Never cut**: the hands-up poll, the processing-speed arithmetic, head-of-line
blocking, the offset-commit slide, or either takeaway slide.

---

## Acts 1–2 — title and playbook (1.5 min)

Bottom line up front, deliberately. People wander in late at Current and decide
inside ninety seconds whether to stay, so the claim and the payoff are both on
screen immediately: **40–70% of your Kafka spend is partitions nobody chose**,
and four layers to get it back.

Do not defend the 40–70% here. State it flatly, point at the four layers, and
move on — the poll proves it on the room two minutes later and Act 4 does the
arithmetic. Promise the two takeaways while you are here: an audit checklist
and a decision framework, both at the end, both screenshot-able.

## Act 3 — the audience poll (3 min)

This only works if you actually wait for answers. First slide: *"Every topic
needs at least one partition. How many topics do you run?"* Take shouted
answers. Anchor on roughly 1,000.

The poll slide is built on four clicks — do not rush them:

| Click | On screen | What you do |
|-------|-----------|-------------|
| 1 | ↑ "more than 1,000 partitions?" | most hands go up — look round, acknowledge it |
| 2 | ↓ "more than 10 GB/s?" | almost every hand drops — **wait**, the silence is the argument |
| 3 | bar fills to a tenth | "this is what a genuinely busy cluster actually does" |
| 4 | the line | say it, then move on — do not over-explain |

864 TB/day is the number to let hang in the air. If anyone challenges the
10 MB/s figure, both sources are Confluent's own: Jun Rao (2015), *"one can
produce at 10s of MB/sec on just a single partition"*, and today's Confluent
Cloud docs, which guide ~12 MB/s ingress per partition on Dedicated. Ten is
below both, so the gap is understated.

Land on: **your partition count is not set by producer throughput.**

## Act 4 — the tax (10.5 min)

The act answers one question: where does the waste come from?

The chain: consumers set the partition count → consumer count is set by
**processing speed**, not data volume → stream processing multiplies whatever
number you picked → and the decision is irreversible.

The arithmetic is the most important slide in the deck. 50ms per record → 20
records/sec per consumer → 1,000 rec/s needs 50 consumers → 50 partitions,
carrying 1 MB/s. Fifty milliseconds is an ordinary internal service call,
nothing pathological, which is the point. Walk it slowly.

Then the multiplier: one input topic at 24 partitions drags seven internal
repartition and changelog topics to 24 each — almost 200 partitions for a job
moving under 100 KB/s. Co-partitioning is documented; the inheritance rule is
not, so cite the source if pushed (`RepartitionTopics.computePartitionCount`,
`ChangelogTopics.setup`, `PartitionGrouper`).

The mea culpa slide matters more than it looks. Both quotes are live on our own
blog right now — do not claim they were never published, because anyone can
pull the URL up in ten seconds. Own it cheerfully; it buys credibility for the
next thirty minutes.

Then the cost, split by deployment:

- **Managed** — the bill argues for you. Move fast.
- **Self-managed** — where the room pushes back, and the good part. Replicas set
  broker count: 100k × RF3 = 300k ÷ 4,000 = 75 brokers when the throughput needs
  ~4. Concede the AWS 12,000/broker figure openly; 25 is still six times too many.
- **KRaft** — be genuinely appreciative. It fixed the cluster, not the broker.

Land the act on leader elections, not money. Cost gets deferred to next quarter;
rolling-restart windows get fixed.

## Acts 5–6 — prevent and clean (6 min combined)

Deliberately brisk. Organisationally important, intellectually simple, and the
room's energy should be banked for Act 7.

**Prevent**: the failure mode is becoming a ticket queue. The policy *is* the
review. Two different jobs and you need both — a `ResourcePolicy` is the
ceiling, a `TopicTemplate` is the default. The docs put it well: templates are
suggestions, not rules. Changing one template default from 30 to 1 is the
highest-leverage hour in the talk; the ceiling stops the worst case, the default
decides the median.

**Clean**: cloud tags stop at the resource boundary, and the cluster is one
resource hiding forty tenants — that is why FinOps teams stall on Kafka
specifically. Ownership has to be a declared object before any of it works:
`Application` names the owner, `ApplicationInstance` binds a topic prefix to a
cluster and a service account. That prefix is the join key chargeback needs.
Be honest that chargeback works through budget and visibility, not dashboards.

## Act 7 — optimize the consumer (13 min, the centrepiece)

Structure: the ticket → the diagnosis → the picture → the wrong tool → the hard
part → the tools → the decision.

Key beats:

- *"We need more partitions, our consumer can't keep up"* — a correct
  observation with the wrong remedy attached.
- The diagnosis is IO-bound processing. One partition = one unit of work = one
  thread, which was fine when processing took microseconds.
- Head-of-line blocking: B, C and D are different entities with no business
  relationship to A. They wait because a hash function put them in one bucket.
- **The picture**: three partitions, four keys, one consumer instance running one
  worker per key — four concurrent workers against three partitions. Concurrency
  is a number you set; partitions are a number you provision in a topic you
  cannot shrink.
- Share groups: give them a *full and fair* hearing. They are excellent for job
  queues. The objection is narrow and specific.
- Offset-commit correctness is what kills homegrown attempts. Two wrong answers,
  then the right one.
- Virtual threads: right execution layer, not a contract layer.
- Three libraries. Recommend the *category*, not a vendor. Say the llingr
  licensing caveat out loud — patent pending, licence unpublished. If asked what
  to start with: the astubbs fork, Apache 2.0, maintained by the person who
  wrote the original.

Close on the decision tree, which is now **two** questions. Key-based ordering?
Parallel Consumer, KEY mode. No? Then the question is per-message ack — the one
thing Parallel Consumer cannot give you, because Kafka commits in batches. Two
of the three leaves are the same library, and "add more partitions" answers
neither question.

## Act 8 — patch (4 min)

Keep this act vendor-neutral: say "a Kafka proxy", not a product name.

Framing: Act 7 assumed *somebody will change the consumer*. Often nobody will.
The platform team owns the cost and the app team owns the fix — that gap is
where waste lives permanently.

- **Lie 1, virtual clusters** — dev, QA and staging each get their own virtual
  cluster and credentials on one set of brokers. Start with non-prod when selling this
  internally: real isolation requirement, near-zero throughput requirement, and
  nobody is emotionally attached to a dev cluster.
- **Lie 2, concentration** — five DLQs at 12 partitions folded onto one
  physical topic with 3: sixty partitions become three, 180 replicas become 9.
  Volunteer the caveat before anyone asks — it does not shrink an existing topic,
  it changes the destination.
- **Lie 3, virtual partitions** — the slides no longer label it, so say out loud
  that this is an idea, not something anyone can deploy today. The mechanism: the producer placed keys with `hash(key) % 3`; the proxy
  uses the same hash with a bigger modulus, `% 12`, and serves virtual partition
  `v` from physical `v % 3`. That only works because 3 divides 12 — V has to be an
  integer multiple of P.

  Per-key ordering **survives** this; two virtual partitions sharing a physical one
  is fine because they hold disjoint keys. What does not survive cleanly: offset
  translation, 4× read amplification, simulated rebalancing, and the day someone
  grows the topic to 4 partitions. It also assumes the proxy's hash matches the
  producer's partitioner.

  It is in the talk because this room contains the people who can tell me why it
  breaks.

## Act 9 — takeaways (2 min)

Both takeaway slides are screenshot bait; leave them up long enough.

On the checklist, stress **peak not average** throughput in step 2 — averaging
over a week hides the nightly batch spike and someone will correctly challenge
the result.

On the framework, the compression is: **does per-key order matter, do you need
per-message ack, and can you change the app?**

End on the Monday action — an afternoon of work, nobody's approval needed, and
no purchase. Never end a cost talk asking people to buy something.

## Q&A — expected

- **"What about tiered storage?"** Helps the storage cost, does nothing for
  per-broker replica overhead or leader elections. Orthogonal.
- **"Does this apply to Kafka Streams?"** There is a slide — jump to it with `T`.
  Yes, and worse: internal repartition and changelog topics inherit the input
  partition count.
- **"Isn't 1 MB/s too low a bar?"** That's the point. Deliberately conservative
  so the result is unarguable.
- **Someone defending share groups.** Welcome it. Agree they're good, hold the
  line that they solve a different problem. Don't win it rudely — there will be
  people in the room who worked on KIP-932.
- **"What do you actually sell?"** Answer straight and briefly, then return to
  the material.

## Pre-flight

- [ ] Confirm the conference name and year on the title and footer slides
- [ ] `python3 tools/check_svg.py` and `python3 tools/check_content.py` both clean
- [ ] Open `tools/check_layout.html` — no slide overflows the stage
- [ ] Press `S` and check speaker view opens on the right display
- [ ] Press `T` and confirm the contents panel lists every act
- [ ] Rehearse the Right-arrow act jumps — confirm they land where you expect
- [ ] Load the deck once on venue wifi, then verify it still works with wifi off
- [ ] Export a PDF fallback (`?print-pdf`) onto the local disk
- [ ] Check the diagrams from the back of the room, not from the lectern
