# The Partition Tax — speaker script and timing

40-minute slot plus 5 minutes Q&A. 54 slides, but a dozen of those are act
dividers and single-line beats that take seconds. Realistic pace is ~45s/slide
with the two interactive moments absorbing the slack.

## Timing plan

The deck is laid out in two dimensions: **each act is a horizontal column,
and its slides run vertically beneath it.**

| → | Act | Slides deep | Target | Running |
|---|-----|-------------|--------|---------|
| 1 | Title | 1 | 0:30 | 0:30 |
| 2 | Audience poll | 3 | 3:00 | 3:30 |
| 3 | The playbook | 1 | 0:30 | 4:00 |
| 4 | The Tax | 13 | 11:00 | 15:00 |
| 5 | Prevent | 4 | 3:00 | 18:00 |
| 6 | Clean | 3 | 3:00 | 21:00 |
| 7 | Fix the root cause | 17 | 13:00 | 34:00 |
| 8 | Patch | 6 | 4:00 | 38:00 |
| 9 | Close | 6 | 2:00 | 40:00 |

The title stands alone — nothing sits beneath it, so `Down` does nothing and
you start by pressing `Right`.

**Driving it:** `Space` or `Down` to advance normally, fragment by fragment.
`Right` jumps straight to the next act — it ignores any fragments still pending
on the current slide, so it is a reliable "I am out of time, move on" key.
`Left` goes back an act. `O` shows the whole grid at once, which is the fastest
way to reach a specific slide during Q&A.

Because Right skips an act outright, the cut list below is executable live: if
you are three minutes down entering Prevent, press Right twice and you are in
Fix with the whole argument intact.

**If you are running long**, cut in this order:
1. Act 5's proxy-mechanism slide (the metadata rewrite) — say it in one sentence instead
2. Act 1's per-broker cost list — the Jun Rao quote alone carries it
3. Act 4's "what share consumers give you" — go straight to the out-of-order quote

**Never cut**: the hands-up opener, the latency arithmetic, head-of-line
blocking, the offset-commit slide, or either takeaway slide.

---

## Open — the cold open (4 min)

The hands-up is the whole opening and it only works if you actually wait for
answers. First slide: *"Every topic needs at least one partition. How many
topics do you run?"* Take shouted answers. Anchor on roughly 1,000.

The poll slide is built on four clicks — do not rush them:

| Click | On screen | What you do |
|-------|-----------|-------------|
| 1 | ↑ "more than 1,000 partitions?" | most hands go up — look round, acknowledge it |
| 2 | ↓ "more than 10 GB/s?" | almost every hand drops — **wait**, the silence is the argument |
| 3 | bar fills to a tenth | "this is what a genuinely busy cluster actually does" |
| 4 | the line | say it, then move on — do not over-explain |

10 MB/s per partition is deliberately conservative; say so, because someone
will otherwise challenge it and they'd be right to. A single partition on
decent hardware does considerably better.

864 TB/day is the number to let hang in the air. Then: **your partition count
is not set by throughput.** Everything after this answers what does set it.

## Act 1 — the tax (11 min)

The argument runs: consumers set the partition count → consumer parallelism is
set by *latency*, not data volume → and the decision is irreversible.

The latency arithmetic is the most important slide in the deck. 200ms per
record → 5 records/sec per consumer → 1,000 rec/s needs 200 consumers → 200
partitions, carrying 1 MB/s. Walk it slowly. Nobody in that story behaved
unreasonably; that's what makes it expensive.

The mea culpa slide matters more than it looks. Own it cheerfully — it buys the
credibility for the next 30 minutes, and it's true.

Then the cost, split by deployment:
- **Managed** — the bill argues for you. Move fast.
- **Self-managed** — this is where the room pushes back, and it's the good part.
  Replicas set broker count: 100k × RF3 = 300k ÷ 4,000 = 75 brokers when the
  throughput needs ~4. Concede the AWS 12,000/broker figure openly; 25 is still
  six times too many.
- **KRaft** — be genuinely appreciative. It fixed the cluster, not the broker.

Land Act 1 on leader elections, not on money. Cost gets deferred to next
quarter; rolling-restart windows get fixed. 10,000 idle partitions is 10,000
elections, and idle partitions skip the catch-up but never the election.

## Acts 2 and 3 — prevent and clean (6 min combined)

Deliberately brisk. These are organisationally important and intellectually
simple, and the room's energy should be banked for Act 4.

**Prevent**: the failure mode is becoming a ticket queue. The policy *is* the
review. The highest-leverage hour in the whole talk is changing a template
default from 30 to 1 — the ceiling stops the worst case, the default decides
the median.

**Clean**: cloud tags stop at the resource boundary, and the cluster is one
resource hiding forty tenants. That's why FinOps teams stall on Kafka
specifically. Be honest that chargeback works through budget and visibility,
not through dashboards.

## Act 4 — the root cause (13 min, the centrepiece)

Structure: the ticket → the diagnosis → the reframe → the wrong tool → the hard
part → the tools → the decision.

Key beats:

- *"We need more partitions, our consumer can't keep up"* — a correct
  observation with the wrong remedy attached.
- The diagnosis is IO-bound processing. One partition = one unit of work = one
  thread, which was fine when processing took microseconds.
- Head-of-line blocking: B, C and D are different entities with no business
  relationship to A. They wait because a hash function put them in one bucket.
- **The reframe** — partitions are infrastructure, keys are domain. Slow down
  here, it's the intellectual centre.
- Share groups: give them a *full and fair* hearing first. They're excellent
  for job queues. The objection is narrow — they're being pointed at as the
  replacement for Parallel Consumer, and they aren't that. "Records in a
  share-partition can be delivered out of order." Resurrected deleted user.
- The Postgres/Redis line is the quotable one. Say it, then stop for two beats.
- Offset-commit correctness is what kills homegrown attempts. Two wrong
  answers, then the right one.
- Virtual threads: right execution layer, not a contract layer.
- Three libraries. Recommend the *category*, not a vendor. Say the llingr
  licensing caveat out loud — patent pending, licence unpublished — rather than
  burying it. If asked what to start with: the astubbs fork, Apache 2.0,
  maintained by the person who wrote the original.

Close the act on the decision tree, and the observation that "add more
partitions" isn't an answer to any of its three branches.

## Act 5 — patch (4 min)

Framing: layer three assumed *somebody will change the consumer*. Often nobody
will. The platform team owns the cost and the app team owns the fix — that gap
is where waste lives permanently.

- **Lie 1, virtualisation** — shipping. Start with non-prod when selling this
  internally: real isolation requirement, near-zero throughput requirement, and
  nobody is emotionally attached to a dev cluster.
- **Lie 2, concentration** — shipping. Volunteer the caveat before anyone asks:
  it does not shrink an existing topic. It changes the destination, not the
  need to migrate.
- **Lie 3, virtual partitions** — **NOT IMPLEMENTED.** Say this out loud at
  least twice. Not built, not on a roadmap, not purchasable. It's in the talk
  because this room contains the people who can tell me why it breaks, and the
  failure modes (offset semantics, per-key ordering when two virtual partitions
  share a real one, simulated rebalancing) are more interesting than the idea.

## Act 6 — close (2 min)

Both takeaway slides are screenshot bait; leave them up long enough.

On the checklist, stress **peak not average** throughput in step 2 — averaging
over a week hides the nightly batch spike and someone will correctly challenge
the result.

On the framework, the compression is: **does per-key order matter, and can you
change the app?** Two questions, one row.

End on the Monday action — an afternoon of work, nobody's approval needed, and
no purchase. Never end a cost talk asking people to buy something.

## Q&A — expected

- **"What about tiered storage?"** Helps the storage cost, does nothing for
  per-broker replica overhead or leader elections. Orthogonal.
- **"Does this apply to Kafka Streams?"** Yes, and worse — internal repartition
  and changelog topics inherit the input partition count, so one
  over-partitioned input multiplies across several internal topics.
- **"Isn't 1 MB/s too low a bar?"** That's the point. It's deliberately
  conservative so the result is unarguable. 10 MB/s topics usually run on one
  partition too.
- **Someone defending share groups.** Welcome it. Agree they're good, hold the
  line that they're a different tool. Don't win it rudely — there will be
  people in the room who worked on KIP-932.
- **"What do you actually sell?"** Answer straight and briefly, then return to
  the material.

## Pre-flight

- [ ] Confirm the conference name and year on the title and footer slides
- [ ] Press `S` and check speaker view opens on the right display
- [ ] Rehearse the Right-arrow act jumps — confirm they land where you expect
- [ ] Load the deck once on venue wifi, then verify it still works with wifi off
- [ ] Export a PDF fallback (`?print-pdf`) onto the local disk
- [ ] Check the diagrams from the back of the room, not from the lectern
