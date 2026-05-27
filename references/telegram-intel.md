# Telegram Intel

This is optional private field intelligence. Use it when the task needs current, practical, Russia-based signals rather than only public docs and GitHub repos, and the user has provided access to relevant Telegram exports or support-chat data.

## The Two Chats

### `ITDog Chat`

Treat this as:

- early warning radar
- router and edge-client lab
- `Podkop` / `zapret` / `OpenWrt` / `DNS` / `sing-box` / `AmneziaWG` support layer

Best for:

- "what is breaking right now on home internet"
- "what are people doing on routers and clients"
- `DNS`, `fakeip`, `DoH/DoT`, `Private DNS`, `AGH`, `dnsmasq`
- `OpenWrt`, router models, package compatibility, edge symptoms

Important caveat:

- search is noisy because `PodkopAI_bot` and `itrobodogbot` contribute many generic replies
- prefer exact errors, versions, models, and code-like strings over broad words

### `Обсуждение VPN-протоколов`

Treat this as:

- server and transport playbook
- hoster, ASN, Cloudflare, `443`, `XHTTP`, `REALITY`, `SelfSteal`, panel-routing layer

Best for:

- "what breaks on server-side topologies"
- `Remnawave`, `Marzban`, `3x-ui`, inbound layouts, `NGINX stream`
- `443`, multiple domains, `SelfSteal`, `serverNames`
- hosters, dirty IPs, ASN/whitelist/blacklist-like patterns, `Cloudflare`

Important caveat:

- it has more self-promotion and anecdotal claims around VPS and hosters than `ITDog`
- treat repeated independent complaints as a real signal; treat one hoster post as weak evidence

## Role Split

- `ITDog Chat` = radar + router playbook
- `Обсуждение VPN-протоколов` = server and protocol playbook

## Search Strategy

### Start by symptom, not by favorite protocol

Good first-pass symptom searches:

- `отвал`
- `не работает`
- `только через vpn`
- `443`
- `dns`
- `cloudflare`
- `sni`
- `тспу`
- `global_check`

### Then branch by layer

#### Edge/router layer

Start in `ITDog Chat` with:

- `podkop` / `подкоп`
- `zapret`
- `openwrt`
- `dns` / `днс`
- `global_check`
- `show_sing_box_config`
- `view_logs`
- router model names

#### Server/transport layer

Start in `Обсуждение VPN-протоколов` with:

- `xhttp`
- `reality`
- `selfsteal`
- `443`
- `cloudflare`
- `remnawave`
- `marzban`
- `hoster`
- `asn`
- `подсети`

## High-Value Query Bundles

### For `ITDog Chat`

- `0.7.17 key n/a`
- `global_check`
- `[fatal] Sing-box configuration`
- `Additional marking rules found`
- `dnsmasq rebind`
- `127.0.0.42`
- `127.0.0.10 AGH`
- `amneziawg 25.12.4`
- `zapret2 blockcheck2.sh`
- `routing_mark 0x10000000`
- `AX3000T Qualcomm`

### For `Обсуждение VPN-протоколов`

- `handshake`
- `только через впн`
- `не работает в рф`
- `тспу`
- `каскад`
- `через мост`
- `xhttp reality`
- `reality serverNames`
- `xhttp 443`
- `cloudflare в рф`
- `подсети в бане`
- `вайтлист асн`

## What The Chats Added To This Skill

The public sources explain protocol behavior. The chats added operational reality:

- `AmneziaWG` is a strong default, but actual viability on routers is gated by package and platform compatibility.
- `XHTTP/REALITY` discussions cluster around `443`, multiple domains, `SelfSteal`, `serverNames`, and real panel behavior rather than theory.
- DNS mistakes cause a surprising share of "protocol" failures on routers and clients.
- `Cloudflare` is both a tool and a risk surface: CDN, WARP, blocked or suspicious subnets, and route-list interactions all matter.
- Router and edge symptoms often surface in `ITDog` before they show up in cleaner public writeups.
- Server-side breakage patterns, hoster selection, and whitelist/subnet folklore show up earlier in `Обсуждение VPN-протоколов` than in protocol docs.

They also surfaced a practical utility layer worth checking before inventing new diagnostics or routing corpora:

- `itdoginfo/allow-domains`
- `vernette/censorcheck`
- `tickcount/podkop-subscriptions`
- `Shellgate/warp-endpoint`
- `medvedeff-true/ru-gaming-blocklist`
- `akiyamov/xray-online`
- `XTLS/RealiTLScanner`

## How To Use This Layer Safely

- Prefer repeated observations over one loud anecdote.
- Use Telegram to generate hypotheses and operational priorities.
- Confirm protocol semantics against official docs.
- Keep public-source-backed findings and Telegram-backed findings clearly distinguished in final reasoning.
