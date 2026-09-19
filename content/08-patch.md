<!-- Patch — 6 slide(s). "---" starts a new slide (Down). -->

<!-- .slide: class="center-slide" data-state="act" -->

<p class="kicker">Layer four</p>

# Patch

<div class="spine" data-act="4"></div>

What lies you can tell when you can't change the app
<!-- .element: class="mute pad-top" -->

---

## It's hard to make application changes

Maybe everyone agrees to use a parallel consumer framework, but
<!-- .element: class="pad-top" -->

<ul class="pad-top small">
    <li class="fragment">The team that wrote it left</li>
    <li class="fragment">A contractor wrote it and the contract ended</li>
    <li class="fragment">It's a vendor binary you don't have source for</li>
    <li class="fragment">The team exists, agrees with you, and has it at #14 on the backlog</li>
  </ul>

Note:
Every platform engineer knows this gap intimately. They can see the waste,
they can price the waste, and they cannot touch the code that causes it.

That's what this layer is for. It is not the elegant answer. It's the one
available to the person who actually carries the cost.

---

## How can a Kafka proxy help?

It is not a reverse proxy. It parses the Kafka wire protocol and cleverly modifies requests and responses.
<!-- .element: class="pad-top small mute" -->

<pre><code data-trim class="language-text">
client  ->  metadata request -> proxy
proxy   ->  forwards metadata request -> broker
broker  ->  "the brokers are at 10.0.0.5:9092, 10.0.0.6:9092"
proxy   ->  rewrites that to "proxy:9093, proxy:9094"
client  ->  every subsequent connection comes back through the proxy</code></pre>

Sitting in the protocol path means the proxy can be "creative with the truth" when it talks to the client.
<!-- .element: class="small fragment" -->

Note:
Keep this tight — it's mechanism, not payoff. But people need it, because
otherwise the next three slides sound like magic.

The key idea to plant: the client's view of Kafka is negotiable.

---

<p class="kicker">Lie #1 — in production today</p>

## "You have your own cluster."

Virtual clusters. You don't need dedicated hardware to isolate environments.
<!-- .element: class="pad-top" -->

Each virtual cluster has its own topic namespace and its own ACLs on shared physical infrastructure.
<!-- .element: class="pad-top mute" -->


<div class="cols pad-top">
    <div class="panel bad"><h4>Before</h4><p>Nine non-prod clusters, each with its own brokers, its own internal topics, its own per-broker partition overhead, all running at 2% utilisation.</p></div>
    <div class="panel good"><h4>After</h4><p>One physical cluster. Nine tenants who cannot see each other. Eight clusters' worth of overhead deleted.</p></div>
  </div>

Non-prod is the easy win: the isolation requirement is real, the throughput requirement is nearly zero, and nobody is emotionally attached to a dev cluster.
<!-- .element: class="small mute fragment pad-top" -->

Note:
Start with non-prod when selling this internally. It's the lowest-risk
consolidation and usually the biggest raw saving, because non-prod clusters
are provisioned like prod and used like a laptop.

---

<p class="kicker">Lie #2 — in available today</p>

### "You have your own topic."

<figure class="fig-compact">
  <img src="assets/diagrams/concentration.svg" alt="Five dead-letter topics of twelve partitions each are presented to clients by the Gateway under a concentration rule, and folded behind it onto one physical topic with three partitions.">
</figure>

The long tail — dead-letter queues, audit topics, per-tenant topics, non-prod scratch
<!-- .element: class="pad-top small mute" -->

---

<p class="kicker">Lie #3 — not implemented, but wouldn't this be cool?</p>

## "You have more partitions than you do."

A thought experiment for now.
<!-- .element: class="pad-top small mute" -->

<div class="cols pad-top">
    <div class="panel">
      <h4>The idea</h4>
      <p>For one specific slow app, the proxy advertises more partitions than the topic really has, then maps them back to the real partitions underneath.</p>
    </div>
    <div class="panel">
      <h4>Why it's tempting</h4>
      <p>The app scales horizontally as if it had the partitions. No library migration, no rewrite, no access to the source needed. The platform team acts alone.</p>
    </div>
  </div>


Note:
BE EXPLICIT AND REPEAT IT: this is not implemented, not on a roadmap, not
something anyone can buy. I am floating an idea at a technical conference
on purpose.

If I get this wrong and someone thinks it's shipping, that's a support
ticket for my colleagues and a credibility problem for me. Say "this does
not exist" out loud at least twice.

The reason to include it: the room is full of exactly the people who can
tell me why it won't work, and the failure modes are more interesting than
the idea.

---

## How the lie would have to work

<figure>
  <img src="assets/diagrams/virtual-partitions.svg" alt="A three-partition topic read by two apps through the gateway. The gateway reports three partitions to one app and twelve virtual partitions to the slow one. Keys are placed with hash mod twelve, and virtual partition v is served from physical partition v mod 3, so v0, v3, v6 and v9 all come from p0.">
</figure>

Note:
The mechanism, so the room can attack something specific rather than a vibe.

The producer already placed keys with hash(key) % 3. The gateway uses the
SAME hash and the same key, just a bigger modulus: hash(key) % 12. Because
3 divides 12, every key's virtual partition still sits inside its real one —
v mod 3 gives you the physical partition back, exactly.

That is why V has to be an integer multiple of P. With 12 and 3 the nesting
is exact. With, say, 10 virtual over 3 physical, a key's virtual partition
no longer determines its physical one and the whole thing collapses.

Worth saying out loud: per-key ordering SURVIVES this. Each key lands in
exactly one virtual partition, so one consumer sees that key's whole
sequence in order. Two virtual partitions sharing a physical one is fine —
they hold disjoint sets of keys.

What does not survive cleanly: offsets. A virtual partition is a sparse
subset of a real log, so the gateway has to invent an offset space and
translate commits. And every physical partition gets fetched once per
virtual partition mapped to it — 4x the read load here.

And it is brittle in a way I would want to fix before believing in it: it
assumes the gateway's hash matches whatever partitioner the producer used.
Different client, custom partitioner, and the mapping silently misroutes.

If someone in the room has a fix for the offset problem, that is the
conversation I came for.
