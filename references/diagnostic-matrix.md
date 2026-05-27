# Diagnostic Matrix

Use this file when the task is diagnosis-first rather than protocol-first. The point is to map symptom shape to the next discriminating test, the likely contour family, and the right Telegram lane.

## How To Use It

1. Match the case to the closest failure mode.
2. Run the first discriminating test before swapping protocols at random.
3. Use the suggested Telegram lane to refresh current field reality.
4. Keep one backup contour in a different transport family.

If the intake is still sparse, run `python3 scripts/triage_case.py --input case.json` with a small JSON case file to get a structured first-pass recommendation.

## Failure Modes

### `dns-or-nsdi`

- Symptoms:
  - domains disappear only on Russian resolvers
  - apps fail inconsistently while raw connectivity still looks fine
  - `dnsmasq`, `AGH`, `fakeip`, or rebind warnings dominate the report
- First discriminating test:
  - switch to a known-clean external DNS path and retest the same contour
- Primary contour bias:
  - `AmneziaWG 2.0`
- Backup contour:
  - `Xray VLESS + REALITY`
- Telegram lane:
  - `ITDog Chat`

### `first-data-freeze`

- Symptoms:
  - handshake succeeds but traffic dies after first data
  - freezing appears around `16 KB` or about `25` packets
- First discriminating test:
  - retest the same contour from another provider or on another port
- Primary contour bias:
  - `Xray VLESS + REALITY`
- Backup contour:
  - `AmneziaWG 2.0`
- Telegram lane:
  - `Обсуждение VPN-протоколов`

### `443-tls-policing`

- Symptoms:
  - TLS-looking traffic dies only on `443`
  - `REALITY`, `XHTTP`, `SelfSteal`, `serverNames`, or SNI-like tuning dominates the discussion
- First discriminating test:
  - move the same contour to an alternate port before redesigning the whole stack
- Primary contour bias:
  - `Xray VLESS + REALITY`
- Backup contour:
  - `AmneziaWG 2.0`
- Telegram lane:
  - `Обсуждение VPN-протоколов`

### `udp-instability`

- Symptoms:
  - UDP or QUIC breaks, degrades, or behaves differently by port or operator
  - `Hysteria2`, `HTTP/3`, or long-lived UDP sessions are specifically involved
- First discriminating test:
  - retest with a TCP-family contour to confirm that the problem is really UDP-specific
- Primary contour bias:
  - `Xray VLESS + REALITY`
- Backup contour:
  - `Hysteria2`
- Telegram lane:
  - `ITDog Chat`

### `cloudflare-or-asn`

- Symptoms:
  - the server works only through another VPN
  - one provider can reach it and another cannot
  - Cloudflare-backed paths or one VPS subnet look selectively degraded
- First discriminating test:
  - verify that the target or camouflage site itself is reachable from Russia as plain HTTPS
- Primary contour bias:
  - `AmneziaWG 2.0`
- Backup contour:
  - `Xray VLESS + REALITY`
- Telegram lane:
  - `Обсуждение VPN-протоколов`

### `local-dpi-only`

- Symptoms:
  - only a few blocked sites matter
  - one desktop or laptop needs relief, not a general foreign infra contour
  - `zapret`, `GoodbyeDPI`, or `Podkop` are the real scope of the problem
- First discriminating test:
  - confirm the problem is limited to a few sites on one device before rolling out a full tunnel
- Primary contour bias:
  - local DPI bypass
- Backup contour:
  - `AmneziaWG 2.0`
- Telegram lane:
  - `ITDog Chat`
