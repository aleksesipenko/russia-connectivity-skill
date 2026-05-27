# Runbooks

Calibration date: `21 May 2026`

These runbooks combine:

- official protocol and vendor docs
- `runetfreedom` routing inputs
- public empirical blocking reports
- private field intelligence, with Telegram/support-chat exports treated as an operational signal and public docs as the verification layer

## How To Use This File

1. Pick the scenario that matches the user's actual environment.
2. Apply the runbook in order.
3. If it fails, jump to the matching symptom runbook rather than swapping protocols at random.
4. Always end with a backup contour and a routing mode.

Before changing a working setup, ask:

- is the current contour actually failing
- or is it merely not the abstract default you would choose from scratch

Do not migrate a stable working contour without a concrete reason.

## Runbook 0: "Set It Up Properly For Me"

Use when:

- the user delegates the whole contour problem
- the user wants you to choose architecture, fallbacks, and validation
- the machine is a server, NAS, router, or other infra host where bad routing choices can create silent outages

Approach:

1. Audit the host:
   - role
   - direct dependencies
   - current VPN, proxy, DNS, and route layers
   - timers, watchdogs, cron jobs, and bootstrap hooks
2. Identify anti-patterns:
   - multiple competing smart layers
   - stale restore units
   - broken lifecycle semantics
   - hidden SSH tunnels pretending to be the source of truth
3. Choose the architecture:
   - what stays direct
   - what is proxied
   - what is tunneled
   - which contour is primary
   - which backup is independent
4. Prefer one managed source of truth for health and failover.
5. Implement only after the host role and failure domains are explicit.
6. End with runtime contract tests, not just service status.

Success checks:

- no silent blackhole
- primary and backup are explicit
- local infra still works
- the contract services the user cares about are tested from the intended scope

Operational note from a Linux infrastructure-host rollout:

- on Linux infra hosts, a stable pattern is:
  - direct for `LAN`, `Tailscale`, gateway, and local infra
  - one managed local proxy surface as the source of truth for blocked foreign egress
  - host-level `TUN` layered on top only to capture host traffic, not as a second independent routing brain
- prefer `sing-box` for Linux host-level `TUN` capture when fed by a local managed proxy surface
- keep `Xray` or another proxy engine as the upstream egress engine if it is already the working primary contour
- when failover swaps two host-network listeners on the same local ports, wait for port release before starting the backup candidate
- do not trust a one-shot green `curl` after failover; verify the runtime contract from the real host scope

Operational note from a split-host VPS rollout:

- for a public VPS in Russia, the clean default is usually `split-host`, not host-wide full-tunnel:
  - keep `SSH`, `Tailscale`, provider reachability, and host lifecycle direct
  - make `docker` and sandbox workloads inherit blocked egress through one transparent `sing-box` contour
  - keep a local `127.0.0.1` proxy only as an operator surface, not as the main app contract
- if the standby contour is a tailnet `HTTP CONNECT` proxy, the standby outbound may need `bind_interface=tailscale0` or equivalent; direct host `curl` success does not prove the proxy engine will choose the right interface on its own
- do not use a global route `resolve` action in front of `HTTP CONNECT` standby unless you have verified that preserving hostnames is not required
- a clean failover for split-host should prove two things separately:
  - host direct infra still works
  - blocked `docker` traffic still passes transparently through the standby path
- if host-wide blocked egress is required on a public VPS, do not assume `TUN` is the right capture layer just because the route policy is sound:
  - on a host that already runs `ufw`, Docker bridges, and `iptables-nft`, `sing-box` `TUN + auto_redirect` may collide with the live firewall stack
  - `TUN` without a working redirect layer may look half-alive by resolving DNS yet fail to carry real host TCP
  - in that case, a cleaner production fix can be:
    - keep container capture on the working transparent path
    - add host TCP capture with `OUTPUT REDIRECT` into one `sing-box` inbound
    - preserve direct exceptions in the routing policy instead of forcing a brittle full host tunnel

## Runbook 1: Daily Foreign IT Access From a Laptop or Desktop in Russia

Use when:

- the user needs stable access to blocked foreign services
- the environment is one computer, not a whole home router
- the user needs reliability more than experimentation

Primary contour:

- `AmneziaWG 2.0`

Why:

- official Amnezia docs explicitly recommend using only `AmneziaWG` in high-censorship countries
- current Telegram reality says the edge-client path is dominated by `DNS`, client, and route-policy failures more than by pure protocol theory

Steps:

1. Refresh Telegram intel for the last 7 days.
2. If the complaint smells like client-side or DNS-side breakage, search `ITDog Chat` first.
3. Deploy or connect with `AmneziaWG 2.0`.
4. Change the UDP port to a value below `9999` rather than keeping a random high port.
5. Use an all-except-RU route policy unless the user has a strong reason to do blocked-only.
6. Verify at least one blocked dev service and one plain HTTPS foreign site.

Success checks:

- tunnel comes up cleanly
- foreign blocked services open
- Russian local services that should stay direct still work
- switching DNS does not flip the result unexpectedly

Fallback:

- if UDP is unstable or blocked, move to Runbook 4

## Runbook 1A: Existing Managed VPN Service Already Works

Use when:

- the user already has a commercial or third-party VPN service that works on the current date
- examples include working `VLESS + REALITY` or working `Trojan` profiles
- the task is to reason about current viability, not to rebuild from zero immediately

Primary rule:

- preserve the working contour

Why:

- empirical success on the user's actual provider and path is stronger than generic ranking
- the service operator may have already tuned ports, domains, CDN choices, ASN placement, and fallback logic

Steps:

1. Treat the current working contour as valid.
2. Identify what family it belongs to:
   - `VLESS + REALITY`
   - `Trojan`
   - another service-managed contour
3. Document the current working facts:
   - provider
   - device type
   - whether it is mobile/home/router/server
   - transport family
   - whether it depends on `443`
4. Add a backup contour instead of replacing the working one immediately.
5. Only migrate away if:
   - it starts failing
   - it is too opaque to operate safely
   - the user needs self-hosted control

What to say in answers:

- "`VLESS + REALITY` is still current for you because it is working on your actual path."
- "`Trojan` is also still viable for you as an empirical service contour."
- "The self-hosted default and the currently working managed-service contour are different questions."

## Runbook 2: Whole-Home Or Router-Based Access

Use when:

- the user wants several devices covered
- the device is `OpenWrt`, router firmware, or similar edge gear

Primary contour:

- `AmneziaWG 2.0` on the router

First research lane:

- `ITDog Chat`

Why:

- this is the strongest source for `OpenWrt`, `Podkop`, `DNS`, package compatibility, and router-model quirks
- Telegram signals say many "VPN failures" on routers are actually `dnsmasq`, `AGH`, `fakeip`, `marking`, or package-version problems

Steps:

1. Refresh Telegram intel.
2. Check `ITDog Chat` for the exact router model and firmware line.
3. Prefer `AmneziaWG 2.0` if the package and app versions are aligned.
4. Validate `DNS` before blaming the tunnel:
   - `dnsmasq`
   - `AGH`
   - `127.0.0.42`
   - `127.0.0.10`
   - rebind behavior
5. Only then apply split policy and service rules.

Success checks:

- router clients resolve DNS correctly
- major blocked services work
- traffic does not leak around the intended tunnel

Fallback:

- if router-side complexity dominates, keep the router on simpler routing and shift the backup contour to endpoint devices

## Runbook 3: Self-Hosted VPS For Stable Work

Use when:

- the user needs a foreign VPS or server-side contour
- they want a maintainable personal infrastructure path

Primary contour:

- `AmneziaWG 2.0`

Backup contour:

- `Xray VLESS + REALITY`

Why:

- Amnezia is the most maintainable default if UDP works
- Telegram and public evidence both say one protocol is not enough; keep a transport-family backup

Steps:

1. Use the official Amnezia self-hosted flow first.
2. Keep at least one backup node on a different provider or ASN.
3. Keep one contour that does not rely on Cloudflare.
4. Apply `runetfreedom`-based routing after the tunnel works.

Success checks:

- server reachable from Russia without weird provider dependence
- blocked foreign infra reachable through the contour
- backup contour documented and tested

Fallback:

- if the access path punishes UDP, go to Runbook 4
- if the hoster or subnet appears suspect, go to Runbook 7

## Runbook 4: UDP Is Bad, Broken, Or Inconsistent

Use when:

- `AmneziaWG` fails or is unstable
- the provider or path punishes UDP
- long-lived UDP flows degrade

Primary contour:

- `Xray VLESS + REALITY`

Steps:

1. Refresh Telegram intel.
2. Search `Обсуждение VPN-протоколов` for:
   - `xhttp`
   - `reality`
   - `selfsteal`
   - `443`
   - `serverNames`
3. Build a TCP-family contour instead of trying random UDP ports forever.
4. Do not assume port `443` is automatically best; validate alternate ports if needed.

Success checks:

- connection survives beyond handshake and first data
- the contour works without depending on one lucky provider quirk

Fallback:

- if `443` itself is the issue, go to Runbook 5
- if a managed `Trojan` contour already works for the user, keep it as a live backup rather than discarding it

## Runbook 5: Port 443 Or TLS-Looking Traffic Is Being Punished

Use when:

- TLS-looking tunnels die only on `443`
- `VLESS + REALITY` breaks selectively on some home ISPs
- the path shows the newer policing discussed in net4people `#546`

Primary response:

- treat `443` as suspect, not sacred

Steps:

1. Refresh Telegram intel and search `Обсуждение VPN-протоколов` first.
2. Re-check current public empirical sources on the `443` issue.
3. For `VLESS-TCP-Reality`, test without anchoring everything to one `443` setup.
4. Reduce dependence on large numbers of simultaneous unknown TLS connections.
5. Keep a non-`443` or non-TLS-family backup contour.

What not to do:

- do not keep tweaking one `443` topology endlessly without a second transport-family fallback

Fallback:

- `AmneziaWG 2.0` if UDP works
- `Hysteria2` if QUIC works and the provider allows it

## Runbook 6: DNS Or NSDI Tampering Suspected

Use when:

- domains disappear only on Russian resolvers
- apps fail inconsistently while raw connectivity looks fine
- users report that one resolver works and another does not

First research lane:

- `ITDog Chat`

Why:

- current Telegram evidence says DNS is one of the biggest sources of fake "protocol failures"

Steps:

1. Search `ITDog Chat` by symptom:
   - `dns`
   - `днс`
   - `fakeip`
   - `AGH`
   - `dnsmasq`
   - `global_check`
2. Validate whether the problem is resolver-specific before rotating protocols.
3. Fix DNS behavior first, then retest the same contour.

Fallback:

- if DNS is clean but traffic still fails, classify again under `443`, UDP, or Cloudflare/CDN cases

## Runbook 7: Hoster, ASN, Or Subnet Looks Suspect

Use when:

- the server works only through another VPN
- one provider reaches it and another does not
- Cloudflare-backed or certain VPS paths look selectively degraded

First research lane:

- `Обсуждение VPN-протоколов`

Why:

- the chat is much stronger on hosters, ASNs, dirty IPs, whitelist/blacklist folklore, and Cloudflare-side path risk

Steps:

1. Search by symptom, not by protocol:
   - `handshake`
   - `не работает в рф`
   - `только через впн`
   - `подсети в бане`
   - `вайтлист`
   - `asn`
2. Do not keep investing in one suspicious subnet if repeated field reports point the same way.
3. Move the server or add an intermediate node if the CIDR itself appears to be the problem.

Fallback:

- move provider or ASN
- insert an intermediate node from a cleaner path if needed

## Runbook 8: Need A Fast UDP Backup Distinct From AWG

Use when:

- UDP works
- you want a backup family different from `AmneziaWG`
- throughput matters

Primary backup contour:

- `Hysteria2`

Why:

- official docs say it looks like a normal HTTP/3 web server to outsiders
- it is a strong alternate UDP family when QUIC works

Caveats:

- do not assume QUIC is healthy on every Russian access path
- keep a TCP-family backup too

## Runbook 9: Need The Cleanest User-Facing Answer

When answering a user, produce:

1. the primary contour
2. the backup contour
3. the routing mode
4. the dominant failure pattern you are optimizing for
5. which Telegram lane and which public source lane informed the answer
6. what the user should test next if it fails

If the user already has a working contour, explicitly say whether you recommend:

7. keeping the existing contour as-is
8. adding a backup only
9. or replacing it, and why
