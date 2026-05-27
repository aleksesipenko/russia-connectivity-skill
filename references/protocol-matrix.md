# Protocol Matrix

This matrix is opinionated for Russia as of May 2026. It should be refreshed against live sources before prescribing a final contour.

## First Principle

Do not frame the decision as "which protocol is best" in isolation. In Russia, the outcome often depends more on:

- whether the path is UDP or TCP
- whether the server sits on a suspicious foreign ASN
- whether the flow depends on port `443`
- whether the destination or camouflage path depends on Cloudflare
- whether the client is mobile, desktop, router, or server

Also separate these questions:

- what should be the default contour for a new self-hosted build
- what is already empirically working on the user's current provider and path

If a contour is already working for the user on the current date, do not recommend replacing it only because another option is your abstract default.

## Recommended Order

### 1. AmneziaWG 2.0

Use when:

- you want the default self-hosted contour for daily work
- UDP is allowed on the access network
- you need cross-platform support with low operational drag

Why it is strong now:

- Amnezia's docs recommend it as the default anti-blocking choice in heavily censored environments
- version 2.0 adds dynamic headers, packet-length randomization, and protocol mimicry
- it is easier to maintain than many Xray stacks

Caveats:

- it is still UDP, so some providers or ports may behave badly
- keep a second contour ready in case the access network starts degrading UDP
- if high random ports misbehave, Amnezia explicitly recommends moving the port below `9999`

### 2. Xray VLESS + REALITY

Use when:

- you need a TCP-first contour
- you need a large ecosystem of clients
- UDP is poor or unavailable

Why it still matters:

- REALITY remains one of the strongest camouflage-oriented transports
- it can look like ordinary web browsing and forward unauthenticated traffic to a real target
- current field reality still includes many users and commercial services for whom `VLESS + REALITY` works on 21 May 2026

Caveats:

- Russia's 2025-2026 breakage patterns show that TLS-looking traffic alone is not enough
- issue `#490` shows freezing after about `16 KB` or `25` packets on suspicious foreign ASNs
- issue `#546` shows provider-side TLS policing on port `443`, especially affecting VLESS + REALITY variants
- do not treat `443` as sacred; validate alternate ports and transport changes
- avoid Cloudflare-backed or otherwise risky REALITY targets, because the official docs warn about abuse and port-forward behavior

Operational note:

- if the user already has a working `VLESS + REALITY` contour, preserve it as an empirical success case unless there is a concrete failure pattern that forces a change

### 3. Hysteria2

Use when:

- QUIC works on the access path
- throughput matters
- you want an alternate UDP family distinct from AmneziaWG

Why it can work:

- the protocol spec says it behaves like a normal HTTP/3 web server to outsiders
- it supports masquerade and port hopping

Caveats:

- Russia has a history of QUIC and UDP restrictions, so current provider behavior matters more than theory
- port hopping helps only if the provider blocks specific UDP ports rather than UDP itself
- keep a TCP-family backup

### 4. Trojan

Use when:

- a specific client or environment requires it
- you already know the target access network currently tolerates it
- the user is on a managed VPN service whose `Trojan` contour is already working for them

Why it is not the default:

- "looks like TLS" is not enough under current Russian filtering
- if the censor is classifying flows by packet budget, port, ASN, or behavior, Trojan does not automatically solve that

What this does not mean:

- it does not mean `Trojan` is dead or unusable
- it means `Trojan` should be treated as an empirical contour, not as the universal first pick for new self-hosted infrastructure

### 5. ShadowTLS / SS2022 / OpenVPN over Cloak

Use when:

- there is a clear compatibility requirement
- you need a specialist fallback
- current testing shows it survives better than the primary contour on a specific provider

Caveats:

- these are secondary tools, not the foundation of the playbook
- do not recommend them from memory; validate with current docs and current breakage reports

### 6. Plain WireGuard / OpenVPN / IKEv2

Do not lead with them for Russia unless they are masked or wrapped in a stronger anti-censorship layer.

## Local DPI Bypass Versus VPN

`zapret` or `GoodbyeDPI` can still be the right answer when the task is:

- one desktop or laptop
- a handful of blocked services
- short-term local bypass

They are not a substitute for a robust self-hosted contour that must carry foreign IT infrastructure access across devices.

## Good Operational Pattern

For serious use, design the system as:

1. primary contour: `AmneziaWG 2.0` or `REALITY`
2. backup contour: a different transport family
3. local emergency bypass: `zapret`-style desync where appropriate
4. routing policy: usually all-except-ru
5. two servers in different providers or ASNs

For existing working setups:

1. keep the currently working contour
2. identify why it works: provider, port, transport, DNS, ASN, service tuning
3. add a backup in a different family before replacing anything
