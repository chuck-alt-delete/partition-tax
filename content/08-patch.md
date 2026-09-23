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

<p class="kicker">Lie #1</p>

## "You have your own cluster."

Virtual clusters. You don't need dedicated hardware to isolate environments.
<!-- .element: class="pad-top" -->

<figure class="fig-compact">
  <img src="assets/diagrams/virtual-clusters.svg" alt="Dev, QA and staging applications each connect to their own virtual cluster inside a Kafka proxy, and all three are served by one physical Kafka cluster.">
</figure>


Note:
Read it left to right: three environments, three sets of credentials, three
topic namespaces — and one set of brokers. Nobody can see anyone else's topics.

The typical before-state is several non-prod clusters, each with its own
brokers and its own per-broker partition overhead, running at a few percent
utilisation. Consolidating them deletes that overhead outright.

Start with non-prod when selling this internally. It's the lowest-risk
consolidation and usually the biggest raw saving, because non-prod clusters
are provisioned like prod and used like a laptop.

---

<p class="kicker">Lie #2</p>

### "You have your own topic."

<figure class="fig-compact">
  <img src="assets/diagrams/concentration.svg" alt="Five dead-letter topics of twelve partitions each are presented to clients by a Kafka proxy under a concentration rule, and folded behind it onto one physical topic with three partitions.">
</figure>

The long tail — dead-letter queues, audit topics, per-tenant topics, non-prod scratch
<!-- .element: class="pad-top small mute" -->

---


<p class="kicker">Lie #3</p>

## "You have more partitions than you do."

<figure>
  <img src="assets/diagrams/virtual-partitions.svg" alt="A three-partition topic read by two apps through a Kafka proxy. The proxy reports three partitions to one app and twelve virtual partitions to the slow one. Keys are placed with hash mod twelve, and virtual partition v is served from physical partition v mod 3, so v0, v3, v6 and v9 all come from p0.">
</figure>

Note:
The mechanism, so the room can attack something specific rather than a vibe.

The producer already placed keys with hash(key) % 3. The proxy uses the
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
subset of a real log, so the proxy has to invent an offset space and
translate commits. And every physical partition gets fetched once per
virtual partition mapped to it — 4x the read load here.

And it is brittle in a way I would want to fix before believing in it: it
assumes the proxy's hash matches whatever partitioner the producer used.
Different client, custom partitioner, and the mapping silently misroutes.

If someone in the room has a fix for the offset problem, that is the
conversation I came for.
