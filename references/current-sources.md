# Current Sources

Use these sources in priority order. The point of this skill is to refresh reality before acting, not to replay frozen folklore.

## Priority Order

1. Official protocol and maintainer docs
2. Live routing and rules repositories
3. Empirical censorship tracking and issue threads
4. Private field intelligence, such as Telegram exports or support chats, when available
5. News or policy analysis for trend confirmation

For symptom-first diagnosis inside this skill package, also use [diagnostic-matrix.md](./diagnostic-matrix.md). It is not a primary source itself; it is a routing layer that maps observed failure patterns to the right sources and tests.

## Live Routing and Rules Inputs

### Primary routing sources

- `runetfreedom/russia-v2ray-rules-dat`
  - Repo: <https://github.com/runetfreedom/russia-v2ray-rules-dat>
  - This is the official Russian `geoip.dat` and `geosite.dat` source for `v2rayN`.
  - The README says it updates every 6 hours and exposes live `geoip.dat` and `geosite.dat` download URLs.
  - Use it for living geodata, not copied snapshots.

- `runetfreedom/russia-v2ray-custom-routing-list`
  - Repo: <https://github.com/runetfreedom/russia-v2ray-custom-routing-list>
  - Use when the task needs a ready-made routing mode such as all, all-except-ru, or blocked-only.

- `runetfreedom/geodat2srs`
  - Repo: <https://github.com/runetfreedom/geodat2srs>
  - Use when the target client needs sing-box `srs` files instead of `dat`.

## Community-Tested Utility Layer

Use this layer when the task is "what do people actually use to validate or route this today" or when the first attempt failed and you need existing working practice rather than a fresh invention.

- `itdoginfo/allow-domains`: <https://github.com/itdoginfo/allow-domains>
- `vernette/censorcheck`: <https://github.com/vernette/censorcheck>
- `tickcount/podkop-subscriptions`: <https://github.com/tickcount/podkop-subscriptions>
- `Shellgate/warp-endpoint`: <https://github.com/Shellgate/warp-endpoint>
- `medvedeff-true/ru-gaming-blocklist`: <https://github.com/medvedeff-true/ru-gaming-blocklist>
- `akiyamov/xray-online`: <https://github.com/akiyamov/xray-online>
- `XTLS/RealiTLScanner`: <https://github.com/XTLS/RealiTLScanner>

Do not treat these as canonical truth. Treat them as living evidence of what the community is validating and shipping right now.

### Upstream data feeds behind the routing repos

- `antifilter.download`: <https://antifilter.download/>
- `community.antifilter.download`: <https://community.antifilter.download/>
- `re:filter`: <https://github.com/1andrevich/Re-filter-lists>
- `russia-mobile-internet-whitelist`: <https://github.com/hxehex/russia-mobile-internet-whitelist>

## Protocol and Client Docs

### Amnezia

- Protocol overview: <https://docs.amnezia.org/documentation/protocols-info/>
- AmneziaWG: <https://docs.amnezia.org/documentation/amnezia-wg/>
- AmneziaWG 2.0 self-hosted: <https://docs.amnezia.org/documentation/instructions/new-amneziawg-selfhosted/>

Use these when the task touches AmneziaWG, OpenVPN over Cloak, or cross-platform self-hosted deployment.

### Xray / REALITY

- REALITY transport doc: <https://xtls.github.io/en/config/transports/reality.html>
- Xray user docs: <https://xtls.github.io/en/document/>

Use these for REALITY field behavior, target selection, fallback risk, and current configuration semantics.

### Hysteria2

- Protocol spec: <https://v2.hysteria.network/docs/developers/Protocol/>
- Port hopping: <https://v2.hysteria.network/docs/advanced/Port-Hopping/>
- Server docs: <https://v2.hysteria.network/docs/getting-started/Server/>

Use these when QUIC or UDP contours are being considered.

### sing-box

- Shared TLS config: <https://sing-box.sagernet.org/configuration/shared/tls/>
- Hysteria2: <https://sing-box.sagernet.org/configuration/outbound/hysteria2/>
- ShadowTLS: <https://sing-box.sagernet.org/configuration/outbound/shadowtls/>

Use these for client and transport-field reality, especially when someone suggests relying on `utls`, fragment tricks, or engine-specific TLS behavior.

### Local DPI bypass

- `zapret`: <https://github.com/bol-van/zapret>
- `GoodbyeDPI`: <https://github.com/ValdikSS/GoodbyeDPI>

Use these when the task is local DPI desync on a single device or router, not a general VPN contour.

## Empirical Censorship Tracking

### net4people issue tracker

These are high-value empirical sources because they capture breakage modes sooner than vendor docs do.

- 16 KB or 25-packet freezing and suspicious-ASN logic:
  <https://github.com/net4people/bbs/issues/490>
- Port-443 TLS policing affecting VLESS + REALITY:
  <https://github.com/net4people/bbs/issues/546>
- Cloudflare ECH blocking in Russia:
  <https://github.com/net4people/bbs/issues/417>

### Other monitoring and evidence

- Cloudflare on 16 KB throttling:
  <https://blog.cloudflare.com/russian-internet-users-are-unable-to-access-the-open-internet/>
- HRW report on censorship and TSPU expansion:
  <https://www.hrw.org/report/2025/07/30/disrupted-throttled-and-blocked/state-censorship-control-and-increasing-isolation>
- The Insider on NSDI-based DNS disappearance in February 2026:
  <https://theins.org/en/news/289338>

## Private Empirical Sources

When the user has access to relevant field channels, also use [telegram-intel.md](./telegram-intel.md). Those chats are not public canonical documentation, but they can provide high-value early warning and operational context for what is breaking in practice.

## How To Refresh Before Acting

1. Run `python3 scripts/check_sources.py`.
2. Check the current date and mention it in the answer.
3. Open the protocol docs relevant to the proposed contour.
4. Open at least one empirical source that matches the suspected failure pattern.
5. If a private Telegram layer is relevant and `telegram-mcp` is configured, use its read-only tools or run `python3 scripts/telegram_mcp_refresh.py --days 7 --command /path/to/telegram-mcp`.
6. If `telegram-mcp` is unavailable but a private exporter exists, run `python3 scripts/refresh_telegram_intel.py --days 7 --exporter /path/to/exporter.py`.
7. If routing is involved, confirm the live `runetfreedom` sources rather than quoting old copies.
8. If the first idea fails, consult the community-tested utility layer before designing a bespoke replacement.

## What These Sources Are Good For

- Official docs: configuration truth and protocol semantics
- `runetfreedom`: living route and split-tunnel inputs
- `net4people`: current breakage modes by provider, port, or transport
- Private field layer: current operational pain, workarounds, and pattern drift
- Cloudflare and policy reporting: confirmation that the blocking pattern is systemic, not a local glitch
