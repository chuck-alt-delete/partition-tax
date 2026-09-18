<!-- The Tax — 13 slide(s). "---" starts a new slide (Down). -->

<!-- .slide: class="center-slide" data-state="act" -->

<p class="kicker">Act one</p>

# The Tax

What it costs, and why you already have it
<!-- .element: class="mute" -->

---

## Consumers set your partition count

<figure>
    <img src="assets/diagrams/consumer-parallelism.svg" alt="A topic with four partitions feeds four consumers, one each. A fifth consumer has no partition to take and sits idle.">
  </figure>

Note:
The structural fact everybody knows but few price: within a consumer group,
one partition goes to exactly one consumer. Add a consumer beyond the
partition count and it does nothing at all.

So the moment a team needs more consumer parallelism, the only lever Kafka
offers them is partitions. They are not being careless. They are using the
only knob on the machine.

---

## And that lever is pulled by <em>latency</em>

<figure>
    <img src="assets/diagrams/latency-math.svg" alt="200 ms per record gives 5 records per second per consumer; 1,000 records per second therefore needs 200 consumers and so 200 partitions, to carry just 1 MB/s of data.">
  </figure>

Note:
Walk this slowly, it is the most important arithmetic in the talk.

One external call per record, 200ms. That consumer thread now does five
records a second. Not five thousand. Five.

Topic does 1,000 records a second, so you need 200 consumers, so you create
200 partitions. And the data underneath is one megabyte a second — a tenth
of what a single partition handles.

Nobody in that story did anything unreasonable. That is what makes this
expensive.

---

## And you can't take it back

<pre><code data-trim data-noescape class="language-text">hash("user-123") % 6  ->  partition 2
hash("user-123") % 4  ->  partition 0</code></pre>

Drop the partition count and every key relocates. Ordering breaks, compaction breaks, downstream state breaks.
<!-- .element: class="small fragment" -->

Kafka will happily let you go <em>up</em>. There is no route back down except building a new topic and migrating onto it.
<!-- .element: class="small fragment" -->

<strong>Over-provisioning is a one-way door that costs nothing to walk through.</strong>
<!-- .element: class="pad-top fragment" -->

Note:
This asymmetry is the engine of the whole problem. Adding partitions is a
one-line change with no approval and no downtime. Removing them is a
multi-day migration with a cutover. Of course clusters drift in one
direction.

---

<p class="kicker">And in fairness</p>

## Everyone's advice says over-provision

<blockquote class="small">
    "When in doubt, slightly over-provision. Adding partitions is easy; removing them is not."
  </blockquote>

<blockquote class="small fragment">
    "Small cluster: 3 × broker count per topic. If you expect 20 consumers, start with at least 20 partitions."
  </blockquote>

Both of those are from <em>our own</em> internal guidance. We never published them. I'd have written the same thing five years ago.
<!-- .element: class="pad-top fragment mute small" -->

Note:
Say this cheerfully and own it. I am not here to tell anyone they were
stupid — I am telling you the default advice, including ours, points one
way, and the economics point the other.

This buys the credibility I need for the next thirty minutes. Don't skip it
and don't be defensive about it.

---

## How I define waste — conservatively

<figure>
    <img src="assets/diagrams/waste-definition.svg" alt="Fifty partitions on a 1 MB/s topic read by three consumers: three are working, forty-seven are pure overhead.">
  </figure>

Note:
I want this bar so low that nobody can argue with it. A partition only
counts as wasted if the topic does under 1 MB/s AND there are more
partitions than the largest consumer group has members.

That is not aggressive. Ten MB/s topics could usually run on one partition
too. I'm leaving that on the table so the number is unarguable.

Across the clusters we analyse, that conservative bar still finds 40 to 70
percent of infrastructure cost.

---

<p class="kicker">The easy case</p>

## Managed Kafka puts it on the invoice

<div class="cols pad-top">
    <div class="panel">
      <h4>What you're billed for</h4>
      <p>Per partition-hour, plus hard ceilings per unit of capacity. Confluent Cloud allows 4,500 partitions per CKU.</p>
    </div>
    <div class="panel bad">
      <h4>What that means</h4>
      <p>Partition waste can have you buying a cluster rated for 240 MB/s produce and 720 MB/s consume — to move about 10 MB/s.</p>
    </div>
  </div>

<strong>On a large cluster, the conservative figure lands in the hundreds of thousands of dollars a year.</strong>
<!-- .element: class="pad-top fragment" -->

Note:
On managed, I don't have to work to make this argument. The bill makes it.
Move through this quickly — the self-managed case is where the room starts
arguing with me, and that's the interesting part.

---

<!-- .slide: class="center-slide" -->

## "But we self-manage.
<!-- .element: class="mute" -->

## We're not charged per partition."
<!-- .element: class="mute" -->

True. And not the same thing as free.
<!-- .element: class="pad-top fragment lime" -->

Note:
I hear this in almost every conversation. Pause here — let people who were
thinking it feel seen before I answer it.

---

## Replicas set your broker count

<figure>
    <img src="assets/diagrams/broker-math.svg" alt="100,000 partitions at replication factor 3 is 300,000 replicas; at 4,000 per broker that is 75 brokers, against about 4 needed for the actual throughput.">
  </figure>

Note:
The recommended ceiling is 4,000 to 6,000 replicas per broker, and that
counts total replicas, not leaders.

Yes, better hardware raises it. AWS publishes about 12,000 for a tuned
m7g.8xlarge. Fine — that's 25 brokers instead of 75. The throughput still
only needs about four.

On most clusters I look at, replica count is the binding constraint. Not
throughput. Not storage.

---

<!-- .slide: class="center-slide" -->

## "We upgraded to KRaft.
<!-- .element: class="mute" -->

## For us the sky is the limit."
<!-- .element: class="mute" -->

KRaft fixed the cluster. It did not fix the broker.
<!-- .element: class="pad-top fragment lime" -->

Note:
Be genuinely appreciative about KRaft here — it IS a real improvement, and
I don't want to sound like I'm knocking it. It raised the cluster-wide
metadata ceiling, cut broker startup times, sped up reassignment and topic
creation enormously.

None of which touches the per-broker cost of a partition.

---

## What every partition still costs each broker

<ul class="small">
    <li><strong>File descriptors</strong> — every replica is log segment files on disk</li>
    <li class="fragment"><strong>Memory</strong> — Kafka holds an in-memory buffer per partition</li>
    <li class="fragment"><strong>Random I/O</strong> — more partitions, more scattered reads and writes</li>
    <li class="fragment"><strong>Replication latency</strong> — one fetcher thread per broker pair by default</li>
    <li class="fragment"><strong>Request handling</strong> — even empty partitions generate replication fetches</li>
  </ul>

<blockquote class="small fragment">
    "Replicating 1000 partitions from one broker to another can add about 20 ms latency, which implies that the end-to-end latency is at least 20 ms."
    <span class="attrib">Jun Rao, Confluent</span>
  </blockquote>

Note:
Don't read the list aloud item by item, that's deadly. Hit file descriptors
and memory, then land on the Jun Rao quote — it's from one of Kafka's
original authors and it's about latency, which the room cares about more
than disk.

---

<p class="kicker">The one that actually hurts</p>

## Extra partitions look free until you move a broker

Failure, restart, routine upgrade — every partition that broker led needs a leader election.
<!-- .element: class="pad-top" -->

<div class="cols pad-top">
    <div class="panel">
      <h4>Fixed cost, per partition</h4>
      <p>The election is the same work whether the partition carries 100 MB/s or nothing at all.</p>
    </div>
    <div class="panel bad">
      <h4>So idle isn't cheap</h4>
      <p>An idle partition skips the data catch-up. It does not skip the election. 10,000 idle partitions is 10,000 elections.</p>
    </div>
  </div>

This is the one that turns a cost conversation into an availability conversation — and that's usually when people start listening.
<!-- .element: class="pad-top fragment small mute" -->

Note:
If I only get one point across in Act 1, make it this one. Cost arguments
get deferred to next quarter. Rolling-restart windows and failover times
get fixed.

---

<!-- .slide: class="center-slide" -->

## Managed: it hits the invoice.

## Self-managed: it sets your broker count.

<strong>Either way, partition waste often dominates the cost of running Kafka.</strong>
<!-- .element: class="pad-top lime" -->

The good news: most of it is recoverable.
<!-- .element: class="pad-top mute small" -->

Note:
End of Act 1. Take a breath here. The next 30 minutes are all remedy.
