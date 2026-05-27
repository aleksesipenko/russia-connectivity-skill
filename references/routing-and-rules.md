# Routing and Rules

## Main Point

Routing in Russia should be driven by live rule sources, not by stale embedded domain lists.

## Preferred Inputs

### `runetfreedom/russia-v2ray-rules-dat`

<https://github.com/runetfreedom/russia-v2ray-rules-dat>

What it gives you:

- `geoip.dat`
- `geosite.dat`
- categories such as `geosite:ru-blocked`, `geosite:ru-blocked-all`, `geosite:ru-available-only-inside`, and `ru-whitelist`
- ASN-based helpers like `geoip:cloudflare`, `geoip:google`, `geoip:telegram`, and others

Why it matters:

- the repo is a living aggregation layer over `antifilter`, community data, `re:filter`, and whitelist sources
- the README says it updates every 6 hours
- it is the official Russian geodata source for `v2rayN`

### `runetfreedom/russia-v2ray-custom-routing-list`

<https://github.com/runetfreedom/russia-v2ray-custom-routing-list>

Use this when you need a ready routing posture instead of inventing one from scratch.

## Recommended Default Policy

For real work, prefer an "all except RU" routing mode.

Why:

- it keeps blocked foreign infrastructure inside the tunnel by default
- it avoids relying on a perfect registry of everything TSPU will throttle or break
- it preserves direct access to many Russian local services

## When "Blocked Only" Is Acceptable

Use "blocked only" only when:

- the user wants minimal tunneling
- they understand that it is incomplete
- the task is convenience browsing rather than resilient infrastructure access

The Habr write-up that adapts `v2rayN` for Russia makes the same point: with newer TSPU-style restrictions there is no single complete registry of everything that will misbehave, so blocked-only mode can miss cases.

## sing-box Note

If the client stack is sing-box, prefer converting the living sources rather than maintaining parallel handwritten lists. `runetfreedom/geodat2srs` exists exactly for that reason.

## Practical Rule Design

When building a contour for work:

1. start with all-except-ru
2. keep Russian banks, state services, and latency-sensitive local services direct if needed
3. keep DNS behavior consistent with the tunnel strategy
4. avoid making "blocked-only" the only line of defense

## Maintenance Habit

When a service fails from Russia, ask:

- is it missing from the route rules
- is DNS wrong
- is the transport broken even though routing is correct
- is the provider applying a new heuristic that no list can fully express
