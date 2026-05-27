# Runtime Contracts

Calibration date: `21 May 2026`

This file describes how to close the loop after a Russia-connectivity rollout. The goal is not "it seems better", but "the services the user actually depends on still work, and the machine did not become fragile."

## Mindset

- Define the contract before or during the rollout, not after.
- Use community-tested service sets and utility packs where possible.
- Treat runtime acceptance as a product requirement, not a nice-to-have.
- Prefer evidence from the real host and real paths over abstract arguments.

## High-Value Sources For Contract Design

- `runetfreedom/russia-v2ray-rules-dat`
- `runetfreedom/russia-v2ray-custom-routing-list`
- `itdoginfo/allow-domains`
- `vernette/censorcheck`
- `tickcount/podkop-subscriptions`
- `Shellgate/warp-endpoint`
- `medvedeff-true/ru-gaming-blocklist`
- `akiyamov/xray-online`
- `XTLS/RealiTLScanner`
- private field channels for current service pain and workaround drift, when available

## Contract Structure

### Tier 1

Founder and developer critical services:

- `Telegram`
- `OpenAI`
- `OpenRouter`
- `GitHub`
- container and package registries
- model and control-plane endpoints the user currently relies on

### Tier 2

Broader Russia-connectivity sanity:

- `YouTube`
- major foreign HTTPS
- DNS behavior
- tailnet or remote-control reachability
- a small community-derived set of popular foreign platforms relevant this month

## Test Classes

### Steady State

The main contour is up and the Tier 1 set works from the intended scope:

- host-level if the contract is host-level
- service-level if the contract is service-level
- both if the design intentionally supports both

### Failover

Primary becomes unavailable and backup takes over without leaving a silent blackhole.

For host-level or router-level contours in Russia, do not treat a single immediate post-failover handshake miss as definitive proof that the contour is bad. A practical contract runner should allow one controlled retry for transient `connect`, `timeout`, or `transport` failures so that it measures contour reality instead of one unlucky packet race.

### Post-Reboot

The machine returns in the intended routing and service state after restart.

### Automation Safety

Timers, cron jobs, watchdogs, and boot hooks do not revert the host into a broken routing model.

### Local Infra Safety

LAN access, Tailscale, admin surfaces, and the host's own observability still work.

## Failure Interpretation

When a test fails, classify it before changing architecture:

- DNS failure
- transport failure
- routing failure
- provider or ASN failure
- lifecycle or automation failure

Then search the skill's official and community sources for the exact failure class before proposing a new design.

## Host-Level Linux Note

Observed in a Linux infrastructure-host rollout:

- a clean host-level design can be:
  - managed local proxy surface for primary and fallback selection
  - `sing-box` `TUN` only as the host capture layer
  - direct bypass for `LAN`, `Tailscale`, gateway, local subnets, and upstream contour IPs
- if failover swaps host-network listeners on the same local ports, the manager must wait for port release before starting the backup candidate
- runtime acceptance should be tested both through the host path and through the local proxy interfaces, because both can regress differently during recovery

## Split-Host VPS Note

Observed in a split-host VPS rollout:

- treat `container-transparent` as a first-class contract, not just a smoke test:
  - representative `docker` workloads should reach Tier 1 blocked services without explicit proxy environment variables
  - logs should confirm the proxy engine, not accidental direct egress, carried the traffic
- keep `sandbox-restricted` as a separate contract class:
  - public Internet works through the intended boundary
  - local host, tailnet, and private ranges stay blocked from sandbox scope
- if standby is a tailnet `HTTP CONNECT` proxy:
  - preserve hostname-based proxying where possible
  - avoid unconditional route-level `resolve` that forces IP-literal CONNECT attempts
  - bind the standby outbound to `tailscale0` or the real tailnet interface if the engine otherwise dials the wrong NIC
- failover acceptance for split-host designs should cover:
  - `host-proxy`
  - `container-transparent`
  - `sandbox-restricted`
  - post-failback return to the primary selector

## Host-Wide VPS Capture Note

Observed in a host-wide VPS capture rollout:

- if the user upgrades the contract from split-host to host-wide blocked egress, add a separate `host-transparent` contract class:
  - the blocked endpoints must pass from the host shell without proxy environment variables
  - `host-proxy` should still be tested as an explicit observability surface
- on a firewall-heavy Linux VPS, a route-correct `TUN` rollout can still fail the real contract if the capture layer is incompatible with the host's `nftables` or Docker stack
- if that happens, treat it as a capture-layer failure, not as proof that the contour family or routing policy is wrong
- a valid fallback implementation is:
  - transparent capture for container traffic
  - host TCP capture via `OUTPUT REDIRECT`
  - direct exceptions enforced by routing rules and selected source-port or process exceptions for inbound-facing services
