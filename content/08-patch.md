<!-- Patch — 6 slide(s). "---" starts a new slide (Down). -->

<!-- .slide: class="center-slide" data-state="act" -->

<p class="kicker">Layer four</p>

# Patch

<div class="spine" data-act="4"></div>

What lies you can tell when you can't change the app
<!-- .element: class="mute pad-top" -->

---

## Layer three assumed something

That somebody will change the consumer.
<!-- .element: class="pad-top" -->

<ul class="pad-top small">
    <li class="fragment">The team that wrote it left</li>
    <li class="fragment">A contractor wrote it and the contract ended</li>
    <li class="fragment">It's a vendor binary you don't have source for</li>
    <li class="fragment">The team exists, agrees with you, and has it at #14 on the backlog</li>
  </ul>

<strong>The platform team owns the cost. The app team owns the fix. That gap is where partition waste lives permanently.</strong>
<!-- .element: class="pad-top fragment" -->

Note:
Every platform engineer knows this gap intimately. They can see the waste,
they can price the waste, and they cannot touch the code that causes it.

That's what this layer is for. It is not the elegant answer. It's the one
available to the person who actually carries the cost.

---

## Why a Kafka proxy can do anything at all

It is not a reverse proxy. It parses the Kafka wire protocol — every request typed, versioned and decoded before it reaches a broker.
<!-- .element: class="pad-top small mute" -->

<pre><code data-trim class="language-text">client  ->  Metadata request
broker  ->  "the brokers are at 10.0.0.5:9092, 10.0.0.6:9092"
proxy   ->  rewrites that to "proxy:9093, proxy:9094"
client  ->  every subsequent connection comes back through the proxy</code></pre>

That rewrite is why a plain TCP load balancer in front of Kafka gets bypassed within one round trip — and why a protocol-aware proxy doesn't.
<!-- .element: class="small fragment" -->

Sitting in the protocol path means the client's view of the cluster is something you control rather than something you report.
<!-- .element: class="small mute fragment" -->

Note:
Keep this tight — it's mechanism, not payoff. But people need it, because
otherwise the next three slides sound like magic.

The key idea to plant: the client's view of Kafka is negotiable.

---

<p class="kicker">Lie #1 — in production today</p>

## "You have your own cluster."

Virtual clusters. Each team gets isolated bootstrap servers, its own topic namespace, its own ACLs — on shared physical infrastructure.
<!-- .element: class="pad-top" -->

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

<p class="kicker">Lie #2 — in production today</p>

## "You have your own topic."

Topic concentration. Many logical topics fold onto fewer physical partitions behind the proxy. Clients see their own topic and never know.
<!-- .element: class="pad-top" -->

Aimed squarely at the long tail: dead-letter queues, audit topics, per-tenant topics, non-prod scratch. Hundreds of topics, almost no data, all of them holding replicas.
<!-- .element: class="pad-top small" -->

<div class="panel pad-top fragment">
    <h4>The honest caveat</h4>
    <p>This does not shrink an existing topic. Nothing does — you still migrate onto a right-sized topic. What concentration changes is the <em>destination</em>: set the rule up front, and matching topics land on shared physical partitions as they migrate.</p>
  </div>

Note:
Say the caveat before anyone asks. If I let someone in the audience find
the hole, I look like I was hiding it. If I hand it over myself, the rest
of the talk gets more trust, not less.

---

<p class="kicker">Lie #3 — not implemented; I want to argue about it</p>

## "You have more partitions than you do."

A thought experiment, not a product. Nobody has built this. I think it's interesting and I'd like to be told why it's wrong.
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

<strong>Where I expect it to break:</strong> offset semantics across the virtual-to-real mapping, per-key ordering once two virtual partitions share a real one, and consumer group rebalancing that now has to be simulated.
<!-- .element: class="pad-top small fragment" -->

If you can see a fourth reason it breaks, find me afterwards. That's genuinely why it's in this talk.
<!-- .element: class="small lime fragment" -->

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
