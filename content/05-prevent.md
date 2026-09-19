<!-- Prevent — 4 slide(s). "---" starts a new slide (Down). -->

<!-- .slide: class="center-slide" data-state="act" -->

<p class="kicker">Layer one</p>

# Prevent

<div class="spine" data-act="1"></div>

Stop making new waste
<!-- .element: class="mute pad-top" -->

---

## Automated guardrails

<div class="cols pad-top">
    <div class="panel bad">
      <h4>Review every topic</h4>
      <p>You become a ticket queue. Teams route around you, or ship late and resent you for it. Neither outcome survives contact with a deadline.</p>
    </div>
    <div class="panel good">
      <h4>Encode the rule once</h4>
      <p>The policy <em>is</em> the review. Teams self-serve at full speed inside a boundary you set, and you are not in the loop.</p>
    </div>
  </div>

<strong>If prevention costs the platform team a meeting per topic, it will not happen.</strong>
<!-- .element: class="pad-top fragment" -->

Note:
Every platform engineer in the room has lived the left-hand box. Name it
plainly and they'll trust the rest.

---

## Guardrails at creation time

<pre><code data-trim data-noescape class="language-yaml">apiVersion: self-serve/v1
kind: ResourcePolicy
metadata:
  name: partition-limit
spec:
  targetKind: Topic
  description: "Limit topic partition count"
  rules:
    - condition: spec.partitions &lt;= 3
      errorMessage: "Plead your case for an exception if you need more than 3 partitions"
</code></pre>

Give a meaningful error at creation time.
<!-- .element: class="small mute" -->

Note:
This is Conduktor's self-service policy format because that's what I use
with customers, but the shape is the point, not the vendor. If you're
building this yourself with an admission controller or a Terraform policy
module, same three properties.

The error message is doing real work. "Denied" makes people open a ticket.
"Needs a measured throughput number" makes them go measure.

---

## Encourage better practices with templates

<pre><code data-trim data-noescape class="language-yaml">apiVersion: v2
kind: TopicTemplate
metadata:
  name: default-topic
spec:
  displayName: "Default topic"
  description: "Under 10 MB/s? One partition. Go up with a measured number."
  defaults:
    metadata:
      name: "{{data-center}}.{{domain}}.{{classification}}.{{description}}.{{version}}"
    spec:
      partitions: 1
      replicationFactor: 3
      configs:
        retention.ms: "604800000"
        min.insync.replicas: "2"</code></pre>


<strong>The policy stops egregious over-partitioning, but the default decides the median usage.</strong>
<!-- .element: class="pad-top fragment" -->

Note:
Two different jobs, and you need both. Conduktor's own docs put it well:
templates are suggestions, not rules — unlike a ResourcePolicy they don't
block anything. Pair the two.

Most of the waste I find isn't a team gaming the limit. It's a template
default nobody has looked at in years, multiplied by a thousand topics.
Somebody chose 30 once, in 2019, for a different topic, and every
copy-paste since has inherited it.

Changing that one number is the single highest-leverage hour in this talk,
and it needs no migration and no permission.
