<!-- Clean — 3 slide(s). "---" starts a new slide (Down). -->

<!-- .slide: class="center-slide" data-state="act" -->

<p class="kicker">Layer two</p>

# Clean

<div class="spine" data-act="2"></div>

Deal with the waste you already have
<!-- .element: class="mute pad-top" -->

---

## You cannot clean what you cannot attribute


<div class="cols pad-top">
    <div class="panel bad">
      <h4>Cloud tags</h4>
      <li>useless for Kafka resource attribution</li>
      <li>encourages poor practices like single-tenant clusters</li>
    </div>
    <div class="panel good">
      <h4>Attribute Kafka resources to their owners</h4>
      <li>partition-hours</li>
      <li>ingress / egress</li>
      <li>connector task-hours</li>
      <li>storage</li>
    </div>
  </div>

FinOps teams are typically at a loss when it comes to Kafka. They just charge the platform team or incentivize single-tenant architecture, which is also wasteful.
<!-- .element: class="pad-top fragment small mute" -->

Note:
If there are FinOps people in the room this is the slide they photograph.
It explains a frustration they've had for years but couldn't articulate.

---

## Ownership has to be declared

<div class="cols tight"><div><pre><code data-trim data-noescape class="language-yaml"># Defines ownership
apiVersion: self-serve/v1
kind: Application
metadata:
  name: payments
  labels:
    cost-center: ABCD
spec:
  title: "Payments"
  owner: "payments-team" # <- mapped to IdP; gets billed
</code></pre></div><div><pre><code data-trim data-noescape class="language-yaml"># Defines resource boundary
apiVersion: self-serve/v1
kind: ApplicationInstance
metadata:
  application: payments
  name: payments-prod
spec:
  serviceAccount: sa-payments-prod
  cluster: prod
  resources:
    - type: TOPIC
      patternType: PREFIXED
      name: "payments."</code></pre></div></div>

Every topic under <code>payments.</code> on prod now has a named owner. Now we can implement chargeback / showback.
<!-- .element: class="small mute pad-top" -->

Note:
This is the piece people skip, and then wonder why the cost report is
useless. You cannot attribute spend to a team until a team is a declared
object with a name.

The ApplicationInstance does the real work — the docs call it the thing that
"ties everything together": cluster, service account, resource ownership and
policies in one declaration. The same prefix that says who owns payments. is
the prefix that generates their Kafka ACLs, so ownership and access cannot
drift apart.

The two apiVersions across these slides differ and that is correct:
TopicTemplate is v2, the Self-service resources are self-serve/v1.

---

## Accountability → efficiency

<img src="assets/images/chargeback.png" alt="Application owner sees exactly how their usage impacts the cost.">

Note:
Be honest about the mechanism: this works because of embarrassment and
budget, not because of dashboards. A team that can see its own line item
next to its peers' will act. A team looking at a cluster-wide number will
not, because it isn't theirs.

I've watched this recover more partitions than any technical fix in this
talk, and it requires no engineering at all.
