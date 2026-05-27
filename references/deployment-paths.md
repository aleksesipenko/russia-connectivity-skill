# Deployment Paths

This file answers "how do we actually roll this out" without freezing the skill around one brittle command sequence.

## Default Build Strategy

For most users and most VPS setups:

1. deploy a self-hosted server with Amnezia's official self-hosted flow
2. prefer `AmneziaWG 2.0` as the first contour if UDP is viable
3. add one backup contour in a different transport family
4. add routing rules from the `runetfreedom` sources instead of hand-maintained lists

## By Environment

### VPS or leased Linux server

Primary source:

- Amnezia self-hosted setup:
  <https://docs.amnezia.org/documentation/instructions/install-vpn-on-server>
- VPS requirements:
  <https://docs.amnezia.org/documentation/supported-linux-os-for-vps/>

Use this when:

- the task is "raise a working VPN contour on a new VPS"
- the user wants the lowest-friction path without hand-assembling Xray or sing-box from scratch

### Linux workstation or Linux jump host

Primary source:

- Install AmneziaVPN on Linux:
  <https://docs.amnezia.org/documentation/installing-app-on-linux>

Use this when:

- the endpoint is a Linux laptop, workstation, or server that needs a GUI or packaged client
- you need a quick reliable client rollout instead of a custom systemd stack

### OpenWrt router

Primary source:

- Install VPN on an OpenWrt router:
  <https://docs.amnezia.org/documentation/instructions/openwrt-os-awg/>

Use this when:

- the user wants whole-network coverage
- the router should terminate the tunnel for multiple devices

Notes:

- this is a good place for an AmneziaWG primary contour
- still keep a backup contour on at least one endpoint device
- when the rollout is blocked by package compatibility, router model quirks, `Podkop`, `DNS`, or route-policy oddities, refresh the Telegram layer and start with `ITDog Chat`

### Custom Xray rollout

Primary sources:

- Xray docs:
  <https://xtls.github.io/en/document/>
- REALITY transport details:
  <https://xtls.github.io/en/config/transports/reality.html>

Use this when:

- you explicitly need REALITY
- you need fine-grained control over inbounds, outbounds, mux, or transport settings
- the access network currently punishes the AmneziaWG path
- the issue smells like `443`, `SelfSteal`, `serverNames`, `XHTTP`, or panel/topology behavior rather than simple client setup

### Custom Hysteria2 rollout

Primary sources:

- Hysteria server docs:
  <https://v2.hysteria.network/docs/getting-started/Server/>
- Protocol spec:
  <https://v2.hysteria.network/docs/developers/Protocol/>
- Port hopping:
  <https://v2.hysteria.network/docs/advanced/Port-Hopping/>

Use this when:

- QUIC works on the target access network
- throughput or low latency is a priority
- you want a strong UDP-family backup contour

### sing-box-based client or server

Primary sources:

- sing-box TLS:
  <https://sing-box.sagernet.org/configuration/shared/tls/>
- sing-box Hysteria2:
  <https://sing-box.sagernet.org/configuration/outbound/hysteria2/>
- sing-box ShadowTLS:
  <https://sing-box.sagernet.org/configuration/outbound/shadowtls/>

Use this when:

- the target environment already standardizes on sing-box
- the task needs a headless client or service-style deployment

## Practical Rollout Rules

- Always mention the current date in rollout recommendations.
- Prefer the official vendor or maintainer instructions for the chosen contour, then layer Russian-specific routing and fallback logic on top.
- If the user needs the latest field reality, refresh the Telegram layer before finalizing the contour.
- Do not collapse setup and routing into one blob. First get a working tunnel, then apply split policy.
- Before declaring rollout complete, confirm:
  - the client connects
  - DNS behaves as intended
  - at least one blocked foreign service works
  - the backup contour is also documented or installed
