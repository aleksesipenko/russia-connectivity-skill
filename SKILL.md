---
name: russia-connectivity
description: Use when work touches Russia-based users, blocked foreign infrastructure, VPN/proxy setup, self-hosted tunnels, VPS access, or diagnosing whether failures from Russia are caused by DPI, NSDI/DNS tampering, port or ASN filtering, or protocol fingerprinting. Guides live-source refresh, contour selection, routing, and fallbacks for 2026 conditions.
---

# Russia Connectivity

## Overview

Use this whenever a task assumes normal access to foreign infrastructure from Russia. In practice, VPN reachability, DNS behavior, routing mode, and the transport's censorship profile are part of the system design, not an afterthought.

Do not use this skill as a generic VPN-buying guide or a one-protocol recommendation engine. Use it when the task needs diagnosis, design, rollout, or recovery under Russia-specific blocking behavior.

## Core Rules

- Work from the current date. Refresh live signals before prescribing a contour.
- When the user delegates the whole connectivity problem, switch into high-agency rollout mode: audit first, classify the host role, map failure domains, choose architecture, then implement and verify.
- Treat operator-provided field channels, such as Telegram exports or support chats, as an empirical layer when available. Use them to detect what is breaking now and what people are actually doing to survive it.
- Do not treat one protocol name as the answer. Evaluate transport, port, server ASN, DNS path, routing mode, client OS, and provider-specific behavior together.
- Prefer at least two independent paths: one primary contour and one backup in a different protocol family or transport.
- Separate three layers in your reasoning: local DPI bypass, VPN/proxy transport, and traffic-routing policy.
- Separate host connectivity from application egress. On infrastructure hosts, do not casually make Tailscale, updates, DNS, and admin access depend on the same brittle contour as blocked foreign APIs.
- Do not hardcode stale assumptions about Cloudflare, QUIC, port `443`, or one specific datacenter family staying usable.
- Never recommend a contour without first checking whether the breakage is primarily DNS, routing, transport, or provider-specific filtering.
- If a rollout or repair fails, search the skill's official, maintainer, and community sources before inventing a fresh architecture from scratch.
- Prefer ready-made, community-tested routing lists, rule corpora, utility scripts, and runbooks over bespoke one-off lists.
- No contour is "done" without runtime contract tests against the user's most important blocked services.
- Keep public-doc evidence, public empirical evidence, and private field evidence clearly separated in your reasoning.
- When the situation is ambiguous, give a confidence level and the fastest discriminating next test instead of pretending certainty.

## On Invocation

1. Capture the minimum intake facts from the task or infer them explicitly: user geography, ISP or mobile operator, device or router scope, client OS, protocol or stack already in use, target service, and what changed recently.
2. Read [references/current-sources.md](./references/current-sources.md).
3. If the task is diagnosis-first or the symptom pattern is still fuzzy, read [references/diagnostic-matrix.md](./references/diagnostic-matrix.md).
4. If the task is about choosing or changing a contour, read [references/protocol-matrix.md](./references/protocol-matrix.md).
5. If the task is about split tunneling or rulesets, read [references/routing-and-rules.md](./references/routing-and-rules.md).
6. If the task is actual rollout on a VPS, computer, router, or server, read [references/deployment-paths.md](./references/deployment-paths.md).
7. Read [references/runbooks.md](./references/runbooks.md) for the current runbook layer.
8. If the task needs the latest Russia-specific field intelligence, read [references/telegram-intel.md](./references/telegram-intel.md).
9. If the task is a high-agency rollout or repair, read [references/runtime-contracts.md](./references/runtime-contracts.md).
10. Read [references/runbooks.md](./references/runbooks.md) for the current runbook layer.
11. Run `python3 scripts/check_sources.py` when you need a quick freshness check of the curated repos and docs.
12. Run `python3 scripts/refresh_telegram_intel.py --days 7 --exporter /path/to/exporter.py` when you have access to private Telegram exports and need a fresh field pulse.
13. For structured first-pass diagnosis, prepare a small case JSON and run `python3 scripts/triage_case.py --input case.json`.
14. Classify the failure mode before choosing a protocol.
15. Before making a final recommendation, confirm it against at least one official or maintainer source and one empirical source that matches the suspected breakage pattern.
16. Before declaring a rollout complete, run or define runtime contract checks for the actual services the user cares about.

## High-Agency Build Mode

Use this mode when the user delegates the whole problem, not just one protocol choice.

1. Audit the environment before choosing tools:
   - host role
   - who depends on this host
   - current direct paths
   - existing timers, watchdogs, bootstrap hooks, and route mutators
   - current primary and backup paths
2. Map the failure domains:
   - DNS
   - transport
   - port profile
   - hoster or ASN
   - routing policy
   - automation or lifecycle bugs
3. Choose the architecture before choosing the specific commands:
   - which layer stays direct
   - which layer is proxied or tunneled
   - what the primary contour is
   - what the independent backup contour is
   - how rollback works
4. Prefer one managed source of truth for egress health and failover. Avoid multiple competing "smart" layers.
5. Define the runtime contract up front, then verify against it after rollout.

## Community-First Recovery

When something does not work:

1. Re-check official or maintainer docs for the exact fields or behavior involved.
2. Re-check live routing inputs and empirical issue trackers for the current failure pattern.
3. Re-check Telegram and community-tested utilities for known-good workarounds.
4. Only after that, propose a custom architecture change.

Use this skill to find existing working practice, not to reward novelty.

## Intake Checklist

Collect or state assumptions for:

- user city or region in Russia, plus home broadband vs mobile
- provider or operator if known
- one device vs many devices vs whole-network scope
- client OS, router model, or server role
- current protocol, transport, port, and client app
- exact failure symptom and when it started
- whether plain HTTPS to the camouflage destination works
- whether changing DNS, network, or port changes the behavior

If more than three of these are unknown, reduce confidence and avoid prescribing a brittle final contour as if it were proven.

## Decision Tree

### 1. Determine what kind of access is needed

- A few blocked sites on one machine: local DPI bypass may be enough; do not confuse that with a general VPN contour.
- Stable day-to-day access to foreign dev infrastructure from multiple devices: build a self-hosted contour plus routing policy.
- Router or whole-network coverage: prioritize maintainability, low-friction clients, and a backup server in a different ASN.
- A server in Russia that needs foreign APIs, registries, or control planes: use a server-grade client with health checks, external DNS, and explicit route policy.

### 2. Classify the breakage

Look for one of these patterns:

- DNS or NSDI tampering: the domain disappears only on Russian resolvers.
- TLS or TCP freezing after first data, often around `16 KB` or about `25` packets.
- Problems only on port `443`, especially with VLESS + REALITY or other TLS-looking tunnels.
- QUIC or UDP path instability that depends on port, provider, or long-lived sessions.
- Service-specific reachability problems, especially where Cloudflare-backed paths are degraded.

Then choose the live-intel lane:

- Router, `OpenWrt`, `Podkop`, `zapret`, `DNS`, `AmneziaWG` on home or edge gear: start with `ITDog Chat`.
- `443`, `XHTTP`, `REALITY`, `SelfSteal`, `Remnawave`, `Marzban`, hosters, Cloudflare/CDN, and server-side routing: start with `Обсуждение VPN-протоколов`.

### 3. Choose the contour for current conditions

Bias for May 2026:

1. `AmneziaWG 2.0` when UDP works and you want the most maintainable general contour across devices or routers.
2. `Xray VLESS + REALITY` when you need TCP or TLS-style camouflage or a richer client ecosystem, but validate it against the current provider and do not anchor everything on port `443`.
3. `Hysteria2` when QUIC works and you want a fast UDP alternative with real HTTP/3 masquerade and optional port hopping.
4. `Trojan`, `ShadowTLS`, `SS2022`, or `OpenVPN over Cloak` only as explicit compatibility or specialist options after current validation.

## Do Not Recommend Blindly

- one protocol name without transport, port, routing mode, and DNS posture
- a single server or a single ASN as the whole strategy
- `443` as the assumed safest default without current evidence
- `Cloudflare` reachability as a design assumption for all clients
- "blocked only" routing as the default for daily developer work
- WARP, one CDN path, or one hoster anecdote as the only recovery plan
- router-wide rollout before validating the contour on one client

## Evidence Discipline

Label the reasoning inputs mentally or explicitly as:

- config truth: official protocol, client, or maintainer docs
- empirical public evidence: `net4people`, issue trackers, monitoring, operator reports
- private field evidence: local Telegram exports, support chats, or operator notes

If Telegram and public sources disagree, do not hide it. Surface the disagreement and bias toward the explanation with the cleaner reproduction and narrower symptom match.

## Routing Guidance

- For daily work, prefer an "all except RU" style policy over "blocked only".
- Use the `runetfreedom` rulesets as living inputs, not static copies.
- Treat "blocked only" as a convenience mode with blind spots: TSPU throttling and heuristic filtering do not map cleanly to one domain list.
- Keep direct access to Russian banks, government services, and local infra where needed, but do not assume every Russian service should stay outside the tunnel.
- On infrastructure hosts, treat route policy as infrastructure design. Do not let a broken TUN, timer, or bootstrap hook silently replace a clean direct default route with a dead one.

## Optional Telegram Workflow

Use this when the task is "what works now", "what are people discussing this week", "which failures are showing up in Russia right now", or "what should we try first before doing more research", and the user has provided or configured a private Telegram exporter.

1. Run `python3 scripts/refresh_telegram_intel.py --days 7 --exporter /path/to/exporter.py`.
2. Read the generated summary markdown and manifest JSON.
3. Use the `Freshness` and `Symptom Heatmap` sections first so you do not overweight stale anecdotes.
4. If the task is diagnosis-heavy, compare the summary against [references/diagnostic-matrix.md](./references/diagnostic-matrix.md).
5. Start in the right chat:
   - `ITDog Chat` for edge-client and router reality
   - `Обсуждение VPN-протоколов` for server and transport reality
6. Search by symptom before protocol name.
7. Treat one anecdote as weak evidence; treat repeated patterns across multiple users as a live signal.

Do not let the Telegram layer replace protocol docs. Use it to steer where to look, what has started failing, which ports or transports are getting discussed, and which workarounds are recurring.

## Server Design Rules

- Keep at least two independent servers, ideally across two providers or ASNs.
- Avoid designing around one fashionable datacenter family.
- Keep at least one contour that does not depend on Cloudflare reachability.
- For REALITY or Cloak-style camouflage, choose a large ordinary foreign site that is reachable from Russia and does not rely on login gating.
- For self-hosted contours, prefer setups that can be rebuilt cleanly with regenerated client configs.
- Keep rollback simple: one way to disable the contour cleanly and one known-good backup profile ready to import.
- Include lifecycle truthfulness: a dead container or broken route must not still look "healthy" in `systemd`.
- For public VPS hosts in Russia, prefer a split-host design unless the contract explicitly requires host-wide capture:
  - keep `SSH`, `Tailscale`, package updates, admin access, and provider infra paths direct
  - send `docker` and application blocked egress through one transparent managed contour
  - keep one explicit local proxy surface for operator or host opt-in blocked calls
- If host-wide blocked egress is required on a Linux VPS, choose the capture layer empirically:
  - `TUN` is not automatically the best answer
  - on firewall-heavy hosts, `OUTPUT REDIRECT` or another transparent host capture layer may be more reliable than `TUN + auto_redirect`
  - evaluate the capture layer separately from the routing policy and the transport family
- If the backup path rides over tailnet infrastructure, bind that standby outbound to `tailscale0` or the equivalent tailnet interface instead of assuming the default NIC will work.
- Be careful with unconditional route-level `resolve` when the backup family uses `HTTP CONNECT`: pre-resolving can turn working hostname-based proxy flows into broken IP-literal flows.

## Runtime Contract

Every serious rollout should end with a concrete runtime contract:

- Tier 1: the exact blocked services the user relies on, such as `Telegram`, `OpenAI`, `OpenRouter`, `GitHub`, registries, and control planes.
- Tier 2: broader Russia-connectivity sanity, such as `YouTube`, major foreign HTTPS, DNS health, and remote-control reachability.
- Steady-state checks: primary contour works.
- Failover checks: backup contour really takes over.
- Post-reboot checks: the machine comes back in the intended state.
- Automation checks: timers, cron jobs, and watchdogs do not revert the machine into a broken contour.
- Local infra checks: LAN, Tailscale, and admin surfaces still work.

If the runtime contract is missing, the rollout is still in analysis mode.

## Anti-Patterns

Do not normalize any of these:

- a single fragile contour with no independent backup
- a hidden second VPN stack with its own routing logic
- `systemd` units that stay green while the contour is actually dead
- "blocked only" as the default policy for founder or developer work
- runtime claims without runtime contract tests
- hand-maintained domain lists when community-maintained routing corpora already exist
- trying random protocol swaps before checking the documented and empirical failure mode

## Diagnostics Checklist

When troubleshooting, collect:

- provider, region, and whether the access network is mobile or home
- client OS and client version
- protocol, transport, and port
- whether the camouflage destination itself works as plain HTTPS
- whether failure is immediate, after first data, after about `16 KB`, only on `443`, only on UDP, or only on one ASN
- whether switching DNS changes the behavior

## Verification Loop

Before declaring a recommendation complete:

1. Confirm the recommendation still matches the current date and latest refreshed sources.
2. Verify that the camouflage destination or cover site is itself reachable as plain HTTPS from Russia.
3. Verify that the proposed backup is genuinely independent: different protocol family, port posture, or provider path.
4. For routing advice, confirm whether the use case should be `all except RU`, `blocked only`, or full tunnel, and explain the tradeoff.
5. State what the user should test first after rollout: one endpoint, one device, one alternate DNS path, one alternate port, or one alternate network.
6. If the task was a live rollout, state whether the runtime contract actually passed or which part is still failing.

## Confidence Scale

- High: official docs plus recent empirical confirmation match the same symptom pattern.
- Medium: the contour fits the symptoms and current field signals, but one key variable such as ISP, port, or client stack is still inferred.
- Low: evidence is partial, contradictory, or too anecdotal; prefer a short test plan over a firm recommendation.

## Deliverable Shape

When using this skill, answer with:

- the date used for the recommendation
- the known facts and any explicit assumptions
- the confidence level
- the recommended primary contour
- why it fits the current censorship pattern
- one backup contour
- the routing mode
- which public sources and which Telegram-intel signals informed the recommendation
- the first verification steps after rollout
- operational caveats and what must be rechecked later
