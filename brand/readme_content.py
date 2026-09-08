# -*- coding: utf-8 -*-
"""The prose. One entry per repository; the shared frame lives in readme.py."""

CONTENT = {

"invisible-text-forensics": {
"tagline": "Detect and remove invisible Unicode: zero-width characters, AI watermarks, "
           "bidirectional overrides, tag-character prompt injection and homoglyphs. "
           "The byte layer every humanizer skill leaves untouched.",
"hero_alt": "Invisible Text Forensics: a Claude Code Agent Skill that detects and removes "
            "zero-width characters, AI watermarks, bidi overrides and homoglyphs from text",
"diagram_alt": "How Invisible Text Forensics works: one pass over the code points, with "
               "neighbour checks that keep emoji ZWJ and Arabic ZWNJ intact",
"refs": [("references/character-catalog.md",
          "every code point this skill knows, by risk level, with the joiner rule"),
         ("references/attack-patterns.md",
          "six attack mechanics with reproducible payloads, from tag smuggling to Trojan Source")],
"related": [("bank-statement-to-table", "the other skill built on proving a document is what it looks like"),
            ("ad-comment-moderation", "comments are attacker-controlled text: this is what fits inside one"),
            ("always-on-agent", "the read-only first pass that never opens a secret's value")],
"body_top": """## The problem

Every de-AI and humanizer skill rewrites **style**: em dashes, "delve", the tricolon.
There are dozens of them and some have tens of thousands of stars. Not one reads the
**bytes**.

Text carries characters that render as nothing and survive copy, paste, email, PDF
extraction and git:

- a zero-width watermark that says which copy of your contract this is
- a run of tag characters spelling `IGNORE PREVIOUS INSTRUCTIONS` inside a prompt
- a bidirectional override making source code render differently from how it compiles
- a no-break space in a CSV header that quietly breaks a column lookup

This is the layer underneath the humanizers. Run one for the prose, run this for
everything the prose is made of.

## What it does

| Command | What you get |
|---|---|
| `scan` | Every hidden or risky character with code point, line, column, risk level and why it matters. `--json` for pipelines, `--fail-on high` as a CI gate. |
| `clean` | Removal at three levels: `safe` (hidden characters only), `aggressive` (+ exotic spaces), `paranoid` (+ homoglyphs and smart typography folded to ASCII). |
| `extract` | Decodes what the invisible characters actually spell: tag characters, variation-selector bytes, zero-width binary. |
| `watermark` | Embeds an invisible copy identifier. Two recipients get visually identical files. |
| `identify` | Reads the identifier back out of a leaked copy. |
""",
"body_bottom": """## Ten seconds

```bash
python3 scripts/itf.py scan document.md
```

```
document.md
  CRITICAL U+202E     line 12 col 18  Right-to-Left Override (RLO)
           reorders rendering; Trojan Source (CVE-2021-42574) in source code
  HIGH     U+200B     line 3 col 41   Zero Width Space (ZWSP)
           invisible; carries watermarks and hidden payloads
  MEDIUM   U+0443     line 3 col 58   Homoglyph of 'y'
           non-Latin letter that renders like ASCII
```

## The detail that matters

`U+200D` (ZWJ) and `U+200C` (ZWNJ) are **not** always removable:

- inside an emoji sequence, ZWJ is what makes 👨‍👩‍👧 one family instead of three people
- in Arabic, Persian, Hindi and other complex scripts they change which letters join, and
  removing them changes the word

Every naive `re.sub` stripper corrupts both. This one checks the neighbouring code points
first and leaves legitimate joiners alone. There is a test for it, with a canary.

## Use it as a CI gate

```yaml
- name: invisible character gate
  run: python3 scripts/itf.py scan . --fail-on critical
```

Blocks pull requests carrying Trojan Source overrides or tag-character payloads.
""",
},

"cpa-profit-ops": {
"tagline": "Profit and ROI by country, campaign, ad account and operator, computed from "
           "real affiliate payouts instead of platform metrics. Plus ad account triage "
           "and break-even CPL for CPA and lead-gen media buying.",
"hero_alt": "CPA Profit Ops: an Agent Skill computing profit, ROI and break-even CPL for "
            "affiliate and lead generation media buying on Meta and Google Ads",
"diagram_alt": "How CPA Profit Ops works: payouts converted into the ad account currency, "
               "then profit, ranking, account triage and target CPL",
"refs": [("references/profit-math.md",
          "formulas, deal types, ROI against ROAS and MER, aggregation rules"),
         ("references/account-health.md",
          "every triage state with its threshold and what to do about it"),
         ("references/cpl-benchmarks.md",
          "how to build benchmarks from your own reconciled data, geo tiering, what moves CPL"),
         ("references/campaign-naming.md",
          "the convention that makes per-operator and per-geo reporting possible")],
"related": [("lead-delivery-reconciliation", "where the accepted rate in your target CPL comes from"),
            ("affiliate-tracker-ops", "the click id and postback layer underneath these numbers"),
            ("incrementality-testing", "whether the spend caused the result or took credit for it")],
"body_top": """## The problem

Meta and Google know what you spent and how many leads they delivered. They do not know
what a lead is worth to you, so **no platform metric can tell you whether you made
money**. ROAS is blind on a CPA deal, CPL is meaningless without a payout next to it, and
a green dashboard on a lead-gen account is a statement about delivery, not about profit.

```
profit = leads x payout(country) - spend        computed inside ONE currency
ROI%   = profit / spend * 100
```

Every paid-media skill on the market audits the platform. This one audits the business.

## What it does

| Command | What you get |
|---|---|
| `rank` | Profit, ROI, revenue and CPL by country, campaign, account or operator. Never sums across currencies. |
| `health` | Account triage: disabled, spend cap reached, low headroom, spending with no leads, CPL above payout, per country. |
| `breakeven` | Break-even and target CPL from the payout, the accepted-lead rate and your margin. |
""",
"body_bottom": """## Ten seconds

```bash
python3 scripts/profit.py rank perf.csv --payouts payouts.csv --fx fx.csv --by country
```

```
COUNTRY                     LEADS      SPEND    REVENUE     PROFIT     ROI%      CPL  CUR
IT                             41     310.00     594.50     284.50     91.8     7.56  EUR
FR                             67     876.30    1139.00     262.70     30.0    13.08  EUR
MA                            214     390.25     449.40      59.15     15.2     1.82  USD
AE                             31     240.00     210.80     -29.20    -12.2     7.74  USD
BE                              7     120.00       0.00    -120.00   -100.0    17.14  EUR  <- incomplete

Incomplete rows are ranked on the revenue that could be computed.
Profit shown is a floor, not the number:
  BE: no payout set for BE
```

Same data, account triage:

```
[CRITICAL] BM1 - Scale  spend 630.25 USD  leads 245  CPL 2.57
    critical AE: CPL 7.74 above payout 6.80, losing 0.94 USD per lead
    warning  MA: CPL 1.82 within 15% of the 2.10 payout, margin nearly gone
```

The account's blended CPL is 2.57 and looks like a disaster. Split by country, one geo is
fine and one is bleeding. **Blended CPL hides the loser inside the winner**, and that rule
is the difference between cutting the right campaign and cutting the wrong one.

## The three currency rules

Spend is in the ad account's currency, the payout is in the network's. Break any of these
and you get a number that looks authoritative and is wrong:

1. Convert the **payout** into the row's currency. Never convert spend, which is a fact.
2. Currency is part of the group key. EUR and USD rows are never summed.
3. A missing payout and a missing FX rate are **different** failures. Reporting both as
   zero revenue turns a configuration gap into a fake loss.

## Input format

Flat CSV. Only `country,currency,spend,leads` are required; every other column adds a
dimension you can rank by. Working examples in [`templates/`](templates/).

## Not in scope

E-commerce ROAS work where the platform sees the revenue, brand campaigns, and platform
mechanics like bidding and audience setup. This skill is about the money, not the buttons.
""",
},

"affiliate-tracker-ops": {
"tagline": "Find where the click id dies between ad, lander, offer and postback. "
           "Postback validation, verified traffic-source macros, and reconciliation "
           "across tracker, ad platform and affiliate network. Zeustrack, Voluum, "
           "Binom, Keitaro.",
"hero_alt": "Affiliate Tracker Ops: an Agent Skill for click id chains, S2S postbacks and "
            "traffic source macros in Zeustrack, Voluum, Binom and Keitaro",
"diagram_alt": "How Affiliate Tracker Ops works: the click id followed by value across ad, "
               "tracking domain, lander, offer, network and postback",
"refs": [("references/postbacks.md",
          "postback anatomy, the duplicate rule, click id integrity, server-side conversion feedback"),
         ("references/troubleshooting.md",
          "decision trees ordered by how often each cause is the real one"),
         ("references/traffic-source-macros.md",
          "verified macro tables for Meta, TikTok, Google, Taboola and Microsoft, with source links"),
         ("references/kpi-reconciliation.md",
          "why tracker, platform and network never match, and which gaps are normal")],
"related": [("cpa-profit-ops", "the money side of the same work"),
            ("lead-delivery-reconciliation", "what happens to the lead after the offer page"),
            ("competitor-ad-intelligence", "what to put in the campaign this chain serves")],
"body_top": """## The problem

A conversion that does not show up is almost never a tracker bug. It is a broken
parameter chain, and there are only four places it can break:

1. the ad URL macro was never replaced
2. the lander does not forward the parameter
3. a redirect strips the query string
4. the offer expects a different parameter name

Every hour spent guessing between those four is an hour not spent buying traffic.

## What it does

| Command | What you get |
|---|---|
| `inspect` | Unreplaced macros, duplicate keys, empty values, unencoded nested URLs, double encoding, missing click id, http, parameters after `#` |
| `chain` | Where the click id dies across ad, lander, offer and postback |
| `postback` | Validates a postback template: click id token, payout token, https, hardcoded values |
| `macros` | Verified macro tables for Meta, TikTok, Google, Taboola and Microsoft, with links to each platform's own documentation |
""",
"body_bottom": """## Find the break

```bash
python3 scripts/track.py chain \\
  ad=https://t.example/click?clickid=abc123 \\
  lp=https://lander.example/?x=1 \\
  offer=https://offer.example/?aff_sub=abc123 \\
  --param clickid
```

```
ad           clickid        ok        abc123
lp           -              missing
offer        s1             ok        abc123

The chain breaks at 'lp' (missing). It was still intact at 'ad', so the problem is in
what 'ad' passes on, not upstream of it.
```

It follows the **value**, not the key name, so it keeps working while the parameter is
renamed from `clickid` to `sub1` to `aff_sub` along the way. That renaming is normal and
is exactly what makes these chains hard to read by eye.

## One malformed URL, explained

```bash
python3 scripts/track.py inspect "http://t.example/c?cid=__CID__&sub1=&sub1=x"
```

```
WARNING   http, not https: browsers and networks will drop or downgrade parameters on redirect
CRITICAL  duplicate parameter 'sub1': the receiver keeps one of them and you cannot predict which
CRITICAL  cid still contains the literal macro __CID__ (TikTok style __MACRO__): it was never
          replaced, so every click sends the same value
WARNING   sub1 is empty: the macro produced nothing or the source never filled it
```

## The macros lie

`__AID__` on TikTok is the ad **group** id, not the ad. `__CID__` is the **creative**, not
the campaign. `{campaign_item_id}` on Taboola is the creative. Getting this wrong produces
a report that looks correct and groups everything at the wrong level.

## Not in scope

Serving different content to ad reviewers than to users. That violates every major
platform's policy, it is not a tracking problem, and nothing here helps with it. Filtering
in this skill means bot and click-fraud filtering.
""",
},

"whatsapp-receptionist-builder": {
"tagline": "Build an AI receptionist on the WhatsApp Cloud API that books real "
           "appointments: webhook signature over the raw body, the 24-hour customer "
           "service window, idempotency against Meta retries, and double-booking "
           "prevention at the database.",
"hero_alt": "WhatsApp Receptionist Builder: an Agent Skill for building an AI appointment "
            "booking assistant on the WhatsApp Cloud API",
"diagram_alt": "How a WhatsApp receptionist works inside: webhook verifies and enqueues, "
               "the worker decides, the outbox sends with retries",
"refs": [("references/architecture.md",
          "webhook, idempotency, outbox, retries, escalation, what to monitor"),
         ("references/whatsapp-api-traps.md",
          "the window, templates, media ids, opt-out, quality rating, delivery statuses"),
         ("references/booking-correctness.md",
          "the exclusion constraint, availability subtraction, timezones and DST, Google Calendar"),
         ("references/gdpr-and-data.md",
          "retention, PII redaction, Art. 15 and 17, tenant isolation, credentials")],
"related": [("ad-comment-moderation", "the other half of a Meta presence: what happens under the ad"),
            ("always-on-agent", "the same queue and approval thinking, on your own machine"),
            ("invisible-text-forensics", "an inbound message is attacker-controlled text")],
"body_top": """## The four traps

**1. The signature is over the raw body.** Parse the JSON before verifying and the digest
never matches. It presents as a wrong secret, and it is not.

**2. The 24-hour window closes on the customer's last message.** Your replies do not
extend it. Every reminder and follow-up you send on a schedule is outside it by
definition, so it must be a template approved in advance.

**3. Meta retries.** On timeouts too. Without an idempotency table on the message id, one
customer gets two answers and, if the first one booked, two appointments.

**4. Double booking is a race.** Two requests read the same free slot in the same
millisecond. No application-level check wins that; a database exclusion constraint does.

## What it does

| Command | What you get |
|---|---|
| `signature` | Computes or verifies `X-Hub-Signature-256` exactly as Meta does, over the raw bytes |
| `window` | Whether you may send free-form or need an approved template, and how long you have |
| `payload` | Realistic webhook bodies: text, voice note, image, button, delivery status. Reuse a `wamid` and you have an idempotency test |
""",
"body_bottom": """## Tools that work without a phone number

```bash
python3 scripts/wa.py window --last-inbound 2026-09-08T09:12:00Z
```

```
window closes  2026-09-09T09:12:00+00:00
state          OPEN
remaining      18h 12m
you may send   free-form
```

```bash
python3 scripts/wa.py payload audio --from 393331234567 > voice.json

curl -X POST localhost:3000/api/webhook/whatsapp \\
  -H "X-Hub-Signature-256: $(python3 scripts/wa.py signature --secret "$APP_SECRET" --body-file voice.json)" \\
  --data-binary @voice.json
```

`--data-binary` matters: `-d` mangles newlines and the signature stops matching.

## Double booking is a race, so the database has to say no

```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;
ALTER TABLE appointments ADD CONSTRAINT no_overlap
  EXCLUDE USING gist (
    resource_id WITH =,
    tstzrange(starts_at, ends_at) WITH &&
  ) WHERE (status <> 'cancelled');
```

Then treat the violation as a normal outcome: apologise, offer the next slot. Under real
load it fires regularly and the customer should never see a stack trace.

## A working implementation

[whatsapp-receptionist](https://github.com/Hiberius/whatsapp-receptionist) is the full
thing: Next.js, Supabase, multi-tenant, GDPR-first, 544 unit tests and 56 E2E tests, MIT.
This skill is the reasoning behind it, usable on any stack.

## Not for

Marketing broadcasts, unofficial WhatsApp clients, or scraping. Those get numbers banned.
The Cloud API is the only path that survives contact with a real business.
""",
},

"lead-delivery-reconciliation": {
"tagline": "Normalise and deduplicate leads before delivery, then reconcile the buyer's "
           "register against what you sent to get acceptance rate and effective payout "
           "per delivered lead. The number no ad platform can show you.",
"hero_alt": "Lead Delivery Reconciliation: an Agent Skill for lead normalisation, "
            "deduplication and payout reconciliation with affiliate networks and lead buyers",
"diagram_alt": "How lead delivery reconciliation works: normalise, dedupe, cap on the sent "
               "date, deliver on your own id, then reconcile against the buyer's register",
"refs": [("references/delivery-pipeline.md",
          "stages, rejects as inventory, deterministic delivery jitter, idempotency"),
         ("references/reconciliation.md",
          "matching rules, the three states, timezones, what to do when acceptance drops")],
"related": [("cpa-profit-ops", "the campaign economics built on the effective payout"),
            ("affiliate-tracker-ops", "the click id layer that got the lead here"),
            ("whatsapp-receptionist-builder", "the other pipeline where an idempotency key decides everything")],
"body_top": """## The number nobody computes

```
effective payout per delivered lead = total revenue / delivered leads
```

Contract payout 17, acceptance 62%, so a delivered lead is worth **10.54**. Every CPL
target built on 17 is wrong by 38%, and the platform dashboard cannot see any of it.

A lead buyer answering *received* or *waiting to validate* is telling you the payload was
well formed. It is not an economic outcome. That arrives hours later, nobody sends it to
you, and until you pull their register and match it against what you sent, the day's
revenue is a guess.

## What it does

| Command | What you get |
|---|---|
| `normalize` | Email, phone (10 countries), postal code and names cleaned; rejects split out with reasons, ready to resell |
| `dedupe` | Duplicates by email **and** phone, since the same person submits both a personal and a work address |
| `cap` | Daily cap usage counted on the sent date, with the overshoot named |
| `reconcile` | Accepted, rejected, pending, revenue, acceptance rate and effective payout, per day; realignment candidates; unmatched rows on both sides |
""",
"body_bottom": """## What a day was actually worth

```bash
python3 scripts/leads.py reconcile sent.csv network.csv --by-day
```

```
DATE         DELIVERED  ACCEPTED  REJECTED  PENDING   REVENUE    ACCEPT%
2026-09-07           2         1         1        0     17.00      50.0%
2026-09-08           3         2         0        1     34.00     100.0%

effective payout per delivered lead: 10.20
This, not the contract payout, is what a lead is worth to you.

1 lead(s) you rejected locally were registered and judged by the network.
Realign them to delivered, or the payout sits on a rejected row and the day's revenue
never sees it:
  d008  local=rejected_local  network=sold  payout=17.00
```

## Four rules that cost real money

**The postal code is a string.** An API field declared "numeric, 5 digits" still receives
`01000` as `1000` the moment any layer parses it as an integer, and answers 422.
Departments 01 and 04 exist.

**The daily cap is consumed on the sent date.** A lead received at 23:50 and queued past
midnight consumes the next day's slot. Count it on the received date and the cap silently
overshoots one day and underuses the other.

**A lead you rejected locally can still have been paid for.** It reached the buyer, they
judged it, they may owe you. Left unrealigned, the payout sits on a row marked rejected,
both sides look internally consistent, and it runs for a month before anyone notices.

**Pending is not accepted.** Acceptance rate over judged leads, effective payout over
delivered leads. Counting pending as accepted inflates the dashboard until settlement.

## Phone normalisation

FR, IT, ES, BE, PT, DE, NL, GB, MA, AE. Each with its dial code, subscriber length and a
plausibility rule: a French subscriber number starts with 1 to 9, so a leading zero means
the prefix was cut in the wrong place and the number is not trustworthy. Rejecting it
locally is free; a quality failure at the buyer is not.
""",
},

"competitor-ad-intelligence": {
"tagline": "Rank competitors' ads from the Meta Ad Library and Google Ads Transparency "
           "Center without spend data: a Winner Score over longevity, variants, geographic "
           "spread, velocity and recency, plus the lineage grouping that makes longevity "
           "honest.",
"hero_alt": "Competitor Ad Intelligence: an Agent Skill that scores competitor creatives "
            "from public ad libraries without spend data",
"diagram_alt": "How competitor ad scoring works: group re-uploads into lineages first, "
               "then score five observable signals, then find the angle gaps",
"refs": [("references/winner-score.md",
          "every signal, its weight, its saturation point, the stage thresholds, how to retune"),
         ("references/sources-and-limits.md",
          "the four public ad libraries, what each gives you, and the five things none of them will")],
"related": [("cpa-profit-ops", "what to do with the budget once you know what to test"),
            ("incrementality-testing", "how to find out whether the new angle actually worked"),
            ("ad-comment-moderation", "the competitors who show up in your own comments")],
"body_top": """## Every spend number you have seen is estimated

Not the Meta Ad Library, not the Google Ads Transparency Center, not the paid tools.
Nobody publishes what a competitor spent on a creative, so every figure in every
competitor-intelligence product is a model output presented as a measurement.

So stop trying to measure spend and score what is actually observable, and what a losing
ad cannot fake for long:

```
score = 0.35·longevity + 0.25·variants + 0.20·geo + 0.10·velocity + 0.10·recency
```

Nobody keeps paying for an ad that loses money, and nobody produces twelve versions of a
loser. Those two facts carry 60% of the weight.

## What it does

| Command | What you get |
|---|---|
| `lineage` | Groups re-uploads of the same concept by advertiser and text similarity, so longevity means something |
| `score` | The Winner Score, the five signal values behind it, and a stage: battle-tested, gaining traction, new test |
| `gaps` | Angles working for competitors and absent from your own account |
""",
"body_bottom": """## Group re-uploads first, or the ranking is wrong

```bash
python3 scripts/adscore.py lineage creatives.csv --out grouped.csv
```
```
9 creatives -> 7 lineages (2 re-uploads collapsed)
Longevity measured before this step would have understated the survivors.
```

Before grouping, the top creative in the sample corpus scores 78.1. After grouping, a
different advertiser takes the top spot at 84.4, because their three "separate" ads were
one concept that had been running for 99 days. An advertiser who rotates creatives on a
schedule looks like someone running short tests, and is not.

```bash
python3 scripts/adscore.py score grouped.csv --top 5
```
```
SCORE  ADVERTISER           HEADLINE                                    DAYS  VAR  GEO  STAGE
 84.4  SolarFast            Pannelli solari a costo zero                  99    3    5  battle-tested
 78.1  CasaVerde            Come funziona davvero il fotovoltaico        183    1    6  battle-tested
 46.3  VecchioSole          Preventivo gratis                             88    1    1  battle-tested
 38.9  SolarFast            Ultimi giorni per l incentivo                 20    1    2  gaining traction
 31.1  EnergiaPlus          Hai gia controllato la tua bolletta?          11    1    1  new test
```

## The output that changes a media plan

```bash
python3 scripts/adscore.py gaps competitors.csv --mine mine.csv
```
```
ANGLE            THEIRS    SHARE     OURS    SHARE     GAP
how-to                1      33%        0       0%     +33%
offer                 2      67%        2      67%      +0%
urgency               0       0%        1      33%     -33%

Working for them, absent from your account: how-to
```

Not "here are their ads". "Here is the thing you are not testing."

## Archive, do not query

The corpus is the asset. Mark disappeared ads as **ended**, never delete them: deleting
destroys the longevity series, which is 35% of the score. Store the creative **file**, not
the URL, because ad image URLs expire and a library of dead links is a library of nothing.

## Collection is out of scope

No scraping code ships here. Use each platform's official API where one exists and its
public interface where one does not, and read the terms of service first. This skill is
about what to do with a corpus once you have one.
""",
},

"incrementality-testing": {
"tagline": "Causal measurement for marketing: sample ratio mismatch, an always-valid "
           "sequential test that survives daily peeking, CUPED variance reduction, sample "
           "sizing, and geo and holdout designs for channels where you cannot randomise "
           "users.",
"hero_alt": "Incrementality Testing: an Agent Skill for A/B testing and causal measurement "
            "in marketing, with SRM checks, mSPRT and CUPED",
"diagram_alt": "How incrementality testing works: check the split for sample ratio mismatch, "
               "then read the p-value your stop rule allows",
"refs": [("references/experiment-design.md",
          "unit of randomisation, deterministic assignment, power, duration, guardrails"),
         ("references/reading-results.md",
          "SRM, which p-value is legal, CUPED, novelty and primacy, Simpson's paradox"),
         ("references/geo-and-holdout.md",
          "geo holdout, audience holdout, ghost ads, switchback, incremental CPA")],
"related": [("cpa-profit-ops", "the profit maths these decisions feed"),
            ("competitor-ad-intelligence", "what to test next"),
            ("lead-delivery-reconciliation", "the outcome data your experiment should be measured on")],
"body_top": """## The same data, two legal answers

```bash
python3 scripts/lift.py lift --control 50120/1204 --treatment 49880/1330
```
```
absolute lift  +0.2642 pp
relative lift  +11.00%   95% CI [+2.89%, +19.11%]
p = 0.00787  significant
```

```bash
python3 scripts/lift.py msprt --control 50120/1204 --treatment 49880/1330
```
```
always-valid p        0.17168
decision              keep collecting
```

Both are correct. The first is what you may claim if you committed to that sample size in
advance and looked once. The second is what you may claim if you have been watching it
daily. **Choosing the first after seeing that it is smaller is the bias itself.**

Checking a fixed-horizon p-value every day and stopping the first time it dips under 0.05
pushes the real false positive rate to around 30%. That is the main reason A/B results do
not replicate, and it is entirely self-inflicted.

The test suite proves the fix: twenty peeks under a true null, 200 simulated experiments,
false positive rate stays at 1%.

## What it does

| Command | What you get |
|---|---|
| `srm` | Chi-square check on the split, per-arm deltas, and a hard stop when it fires |
| `lift` | Absolute and relative lift with a confidence interval and a fixed-horizon p-value |
| `msprt` | Always-valid p-value from a mixture SPRT: peek as often as you like |
| `cuped` | Variance reduction from a pre-period covariate, with the effective sample multiplier |
| `mde` | Sample size per arm for a target lift, alpha and power |

All of it in the standard library: normal CDF and inverse CDF, regularised incomplete
gamma for the chi-square tail, no SciPy.
""",
"body_bottom": """## Check the split before you read anything

```bash
python3 scripts/lift.py srm --arms "control=52000,treatment=48000"
```
```
SAMPLE RATIO MISMATCH. Stop. Do not read the lift.
The assignment, the logging or a filter is broken. A lift computed on a
broken split is not wrong by a little, it is meaningless.
```

Threshold 0.001, not 0.05. It is a smoke alarm, and a false alarm costs an hour while a
missed one costs a decision.

## Free power out of data you already have

```bash
python3 scripts/lift.py cuped experiment.csv --pre-column pre_28d --post-column post
```
```
correlation pre/post       0.5340
variance reduction         28.5%
equivalent to a sample     1.40x larger
```

The covariate is measured before assignment, so the treatment cannot have touched it,
which is what keeps the adjustment unbiased.

## Not significant is not no effect

The confidence interval decides. If it excludes the effect you would act on, you have
learned it is not there. If it still contains it, the test is underpowered, not negative.
The point estimate alone never tells you which.

## When you cannot randomise users

Inside an ad platform you rarely control assignment, and "exposed versus unexposed" is not
an experiment: the platform chose the exposed group precisely because they were more
likely to convert. Geo holdout, audience holdout, ghost ads and switchback designs, with
their failure modes, are in the reference, along with:

```
incrementality factor = incremental conversions / platform-reported conversions
```

A factor of 0.4 means the platform claims two and a half times what the campaign caused.
""",
},

"ad-comment-moderation": {
"tagline": "Moderate the comments under your Facebook and Instagram ads with a rule "
           "engine that states a reason for every verdict, keeps honest criticism "
           "visible, and resolves where the comments on a dark post actually live.",
"hero_alt": "Ad Comment Moderation: an Agent Skill with a rule engine for hiding spam and "
            "scam comments under Facebook and Instagram ads",
"diagram_alt": "How ad comment moderation works: resolve the ad to its page post, then run "
               "allow rules first and the seven rule kinds in priority order",
"refs": [("references/rule-design.md",
          "the seven kinds, ordering, tuning for lead gen, competitor poaching, false positive discipline"),
         ("references/meta-graph-comments.md",
          "dark posts, hide against delete, pagination, rate limits, token handling")],
"related": [("whatsapp-receptionist-builder", "the other side of a Meta presence: the conversation"),
            ("invisible-text-forensics", "what can be hidden inside a comment you feed to a model"),
            ("cpa-profit-ops", "the campaigns whose comments these are")],
"body_top": """## It decides, it does not just delete

Most "hide Facebook comments" scripts hide everything new. That buries genuine questions
and honest criticism along with the spam, which is why the category has the reputation it
has.

Under a lead-gen ad this is not cosmetic. Link drops send your paid traffic to a
competitor, scam replies impersonate you to people who just gave you their number, and
both sit under the ad for as long as it runs.

## What it does

| Command | What you get |
|---|---|
| `test` | A dry run over one comment or a CSV of them, with the deciding rule and its reason |
| `rules` | The starter rule set as JSON, ready to edit |
| `explain` | Every rule that ran, in order, and why each one did or did not match |

Seven rule kinds — `keyword`, `regex`, `link`, `contact`, `emoji_spam`, `min_length`,
`author_allow` — each with an action (`hide`, `flag`, `allow`) and a priority.
""",
"body_bottom": """## Every verdict states a reason

```bash
python3 scripts/modrules.py test comments.csv
```
```
WOULD HIDE             Buy cheap followers at crypto-x(dot)com now
                       Links: contains an obfuscated link: 'crypto-x(dot)com'
WOULD HIDE             🔥🔥🔥🔥🔥🔥🔥
                       Emoji flooding: carries 7 emoji, threshold 6
WOULD HIDE             check my profile
                       Known spam and scam phrases: matched the term 'check my profile'
WOULD KEEP             Honestly the last bag was stale and shipping took nine days.
WOULD KEEP             Servizio PESSIMO non comprate qui

10 comment(s): 6 would be hidden, 4 kept
This is a dry run. Nothing was sent anywhere.
```

The two complaints stay visible. No rule matches them, and a moderation tool has no
business hiding a comment it cannot give a reason for.

## Where ad comments actually live

The thing that stops most people before they start: a comment on your ad is attached to
the **page post** behind the creative, not to the ad. For a dark post, that post exists,
is reachable, and never appears on your page.

```
ad ──► adcreative ──► effective_object_story_id ──► "{page_id}_{post_id}" ──► /{post_id}/comments
```

One post often backs many ads, so you moderate the post, not the ad. Instagram comments on
the same creative are a separate thread reached through the Instagram media id.

## Allow rules run first, always

An allow list that can be outranked by a higher-priority hide rule is not an allow list.
This ordering is why a customer cannot be hidden by a rule someone added in a hurry.

## Dry run, then flag, then hide

`flag` records a verdict and writes nothing anywhere. Add every new rule as `flag`, let it
run for a day on real comments, read what it caught, and only then switch it to `hide`.
Skipping that is how a moderation tool hides its first customer.

## A working implementation

[CommentHide](https://github.com/Hiberius/commenthide-facebook-comment-moderation) is the
full thing: a single Cloudflare Worker with D1, a dashboard, a dry-run inspector and
one-click undo, MIT. This skill is the reasoning behind it, usable on any stack.
""",
},

"bank-statement-to-table": {
"tagline": "Convert a bank statement PDF into a spreadsheet and then prove the extraction "
           "is correct against the statement's own running balance. European and Anglo "
           "number formats, multi-line descriptions, scans. Entirely offline.",
"hero_alt": "Bank Statement to Table: an Agent Skill that converts a bank statement PDF to "
            "Excel or CSV and verifies it against the running balance",
"diagram_alt": "How bank statement extraction works: two document-level decisions, line "
               "classification, then verification against the balance chain",
"refs": [("references/extraction.md",
          "text layer against scan, why -layout, column clustering, year boundaries, Italian vocabulary"),
         ("references/verification.md",
          "the two checks, difference signatures, tolerance, what to record, privacy")],
"related": [("invisible-text-forensics", "the other skill built on proving a document is what it looks like"),
            ("lead-delivery-reconciliation", "the same discipline applied to money owed rather than money moved"),
            ("always-on-agent", "handling private documents on your own machine")],
"body_top": """## Anyone can extract. The question is whether it is right

Every running balance equals the previous balance plus the movement. That is not a
convention, it is what a balance is. So a parse either reproduces the chain from the
opening balance to the closing balance, or it is wrong and the chain says which row.

```
balance[i] == balance[i-1] + amount[i]      every row
opening + sum(amounts) == closing           the whole statement
```

**Never hand over an extraction that has not passed both.** Extraction is guessing.
Verification is knowing.

## What it does

| Command | What you get |
|---|---|
| `detect` | Date order and decimal separator for this document, and whether there is a text layer at all |
| `parse` | Transactions with date, value date, description, amount and balance, from `pdftotext -layout` output |
| `verify` | The chain row by row and the totals for the file, with the difference explained on the row it names |
""",
"body_bottom": """## The proof

```bash
pdftotext -layout statement.pdf - > statement.txt
python3 scripts/statement.py parse  statement.txt --out rows.csv
python3 scripts/statement.py verify rows.csv --opening 1240.55 --closing 2103.11
```

```
rows                7 (7 carry a balance)
chain checks        6
chain breaks        0
sum of movements    862.56
opening + movements 2103.11
stated closing      2103.11
difference          0.00

VERIFIED: the parse reproduces the statement exactly.
```

Change one digit and:

```
NOT VERIFIED: the parse does not reproduce the statement.

  break at row 1, 2026-06-03  PAGAMENTO POS SUPERMERCATO
    2740.55 -8.24 should give 2732.31, the statement says 2658.15 (off by -74.16)
    hint: the difference equals the amount on 2026-06-05: that row is probably
          duplicated or missing
```

## Two decisions made once, never per row

`01/06` is ambiguous and no cleverness resolves a single row: if any date in the file has
a first component above 12, the whole document is day-first. Deciding per row silently
swaps January and October.

`1.234,56` and `1,234.56` are the same number from two different worlds. Deciding per
value turns `1.234` into 1234 on one row and 1.234 on the next, and the totals then miss
by three orders of magnitude.

```bash
python3 scripts/statement.py detect statement.txt
```
```
date order             day-first (dd/mm)
decimal separator      comma (1.234,56)
```

## It handles what real statements do

- **Multi-line descriptions.** A line with a date and an amount starts a transaction; a
  line with neither continues the previous one. Nothing else is a row.
- **Page breaks, repeated column headers, carried-forward lines, opening and closing
  balance lines.** All skipped, and counted so you can see they were.
- **Every negative convention**: `-82,40`, `82,40-`, `(82,40)`, `82.40 DR`.
- **Value date separate from booking date**, kept, because you cannot recover it later.
- **Scans.** `detect` tells you there is no text layer instead of returning an empty table.

## Your statement never leaves your machine

No network calls, no telemetry, no dependencies, by design. A statement carries the
account holder, the IBAN, the balance and a complete map of a person's life by
counterparty.
""",
},

"always-on-agent": {
"tagline": "Build a personal AI agent that runs continuously on your own machine: the four "
           "layers to keep separate, waking a laptop that sleeps, approval gates, and a "
           "read-only first pass that maps projects and credentials without ever reading a "
           "secret's value.",
"hero_alt": "Always-On Agent: an Agent Skill for building a personal AI agent that runs "
            "continuously on your own Mac, with approval gates and a read-only first pass",
"diagram_alt": "How an always-on personal agent works: a gateway that never sleeps queues "
               "and signs, the machine wakes, the loop runs behind approval gates",
"refs": [("references/architecture.md",
          "the four layers, wake architecture, launchd against cron, channel options, approval tiers, cost"),
         ("references/first-run.md",
          "the read-only first pass, its five rules, what to fix first, what to build after")],
"related": [("invisible-text-forensics", "an agent reads text other people wrote"),
            ("whatsapp-receptionist-builder", "the same queue and idempotency thinking, hosted"),
            ("bank-statement-to-table", "processing private documents without sending them anywhere")],
"body_top": """## Phase zero: look before you touch

The first thing an agent does on your machine must be *incapable* of doing harm. Not
careful. Incapable.

```bash
python3 scripts/survey.py secrets ~/
```
```
Key NAMES only. No value in this output was ever read into memory.

/Users/you/work/api/.env  (7 keys, 4 sensitive)   <- TRACKED BY GIT
    STRIPE_SECRET_KEY, DB_PASSWORD, JWT_SECRET, WEBHOOK_SIGNING_KEY
/Users/you/side/bot/.env  (3 keys, 2 sensitive)
    TELEGRAM_TOKEN, OPENAI_API_KEY

2 secret file(s) found.
1 of them are NOT gitignored inside a repository. Fix that before anything else.
```

It reads the name on the left of the assignment and discards everything else before
returning anything. The test suite plants a canary value in every fixture and asserts it
never appears in any output. That is the contract, not a promise.

## What it does

| Command | What you get |
|---|---|
| `projects` | Every git repository, its branch, uncommitted files, unpushed commits and how long since the last one |
| `secrets` | Which files hold credentials and what the keys are called. Never a value. Exits non-zero on a credentials file tracked by git |
| `stale` | Projects untouched for a month with uncommitted work, which is how things get lost on a laptop |
""",
"body_bottom": """## The status board

```bash
python3 scripts/survey.py projects ~/
```
```
PROJECT                      BRANCH            DIRTY  AHEAD   DAYS  LAST COMMIT
old-client-site              main                 34      0    412  wip before holiday
scraper                      feat/retry            6      3     41  handle 429
api                          main                  0      0      2  bump deps

27 repo(s): 4 need attention, 9 have uncommitted or unpushed work
```

## The four layers

```
FACE     what you look at            reads state, never talks to the model
BRAIN    the agent loop              event-driven, does the work
PROFILE  who you are, what you do    private, gitignored, replaceable
VAULT    secrets                     the model never sees a value
```

**The engine is publishable, the profile is not.** Two directories, one gitignored, no
client name ever inside the engine. That split is what lets you open-source the useful
half, and retrofitting it means auditing every file you have written.

## The wake problem

Your laptop sleeps, so the agent misses everything. A laptop that never sleeps has no
battery.

```
event ──► always-on gateway ──► queue ──► signed POST to the Mac ──► the Mac drains it
```

The gateway holds no secrets and does no work. Sign the wake request and verify it, or you
have published an endpoint anyone can use to make your machine run an agent.

On macOS use `launchd`, not cron: launchd runs a job missed during sleep.

## The phone channel, one rule

**Official channels only.** An unofficial client for a messaging platform gets the number
banned, and on a working phone that is the number your clients use. Not an inconvenience,
your business line.

## Four states, and the fourth is the point

**working** · **waiting for you** · **idle** · **drifting**

An agent forty minutes into something nobody asked for is the failure that actually
happens, and it is invisible unless you have named it.
""",
},
}
