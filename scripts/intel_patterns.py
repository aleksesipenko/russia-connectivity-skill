from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FailureMode:
    key: str
    summary: str
    preferred_chat: str
    keywords: tuple[str, ...]
    primary_contour: str
    backup_contour: str
    routing_mode: str
    next_tests: tuple[str, ...]


FAILURE_MODES = (
    FailureMode(
        key="dns-or-nsdi",
        summary="DNS or NSDI tampering, resolver-specific disappearance, fake protocol failures",
        preferred_chat="ITDog Chat",
        keywords=(
            "dns",
            "днс",
            "resolver",
            "resolvers",
            "nsdi",
            "fakeip",
            "dnsmasq",
            "agh",
            "adguard",
            "private dns",
            "domain disappears",
            "russian resolvers",
            "rebind",
        ),
        primary_contour="AmneziaWG 2.0",
        backup_contour="Xray VLESS + REALITY",
        routing_mode="all-except-ru",
        next_tests=(
            "Switch to a known-clean external DNS path and retest the same contour before changing protocol.",
            "Check whether plain HTTPS to the cover or target host works with the same DNS posture.",
        ),
    ),
    FailureMode(
        key="first-data-freeze",
        summary="Handshake works, then traffic freezes after first data or around 16 KB / 25 packets",
        preferred_chat="Обсуждение VPN-протоколов",
        keywords=(
            "16 kb",
            "25 packets",
            "after first data",
            "first data",
            "freezes",
            "freeze",
            "handshake works",
            "handshake ok",
            "connects then dies",
        ),
        primary_contour="Xray VLESS + REALITY",
        backup_contour="AmneziaWG 2.0",
        routing_mode="all-except-ru",
        next_tests=(
            "Retest on a different provider or ASN to separate protocol issues from suspicious-subnet filtering.",
            "Check whether the same contour survives beyond first data on a non-443 port.",
        ),
    ),
    FailureMode(
        key="443-tls-policing",
        summary="Port 443 or TLS-looking traffic is selectively punished",
        preferred_chat="Обсуждение VPN-протоколов",
        keywords=(
            "443",
            "tls",
            "reality",
            "xhttp",
            "selfsteal",
            "servername",
            "servernames",
            "vision",
            "flow",
            "sni",
            "only on 443",
        ),
        primary_contour="Xray VLESS + REALITY",
        backup_contour="AmneziaWG 2.0",
        routing_mode="all-except-ru",
        next_tests=(
            "Move the same contour to an alternate port first before redesigning the full stack.",
            "Keep one non-443 or non-TLS-family backup profile ready for the same user and provider.",
        ),
    ),
    FailureMode(
        key="udp-instability",
        summary="UDP or QUIC path is unstable, blocked, or degrades over time",
        preferred_chat="ITDog Chat",
        keywords=(
            "udp",
            "quic",
            "http/3",
            "hysteria",
            "hysteria2",
            "mobile operator",
            "port hopping",
            "long-lived",
            "unstable",
            "packet loss",
        ),
        primary_contour="Xray VLESS + REALITY",
        backup_contour="Hysteria2",
        routing_mode="all-except-ru",
        next_tests=(
            "Retest with a TCP-family contour to confirm the problem is UDP-specific.",
            "If QUIC is in play, try one alternate UDP port and one different access network.",
        ),
    ),
    FailureMode(
        key="cloudflare-or-asn",
        summary="Cloudflare-backed reachability, hoster ASN, or subnet reputation looks suspect",
        preferred_chat="Обсуждение VPN-протоколов",
        keywords=(
            "cloudflare",
            "warp",
            "cdn",
            "asn",
            "subnet",
            "подсети",
            "hoster",
            "vps",
            "whitelist",
            "blacklist",
            "dirty ip",
            "only through vpn",
        ),
        primary_contour="AmneziaWG 2.0",
        backup_contour="Xray VLESS + REALITY",
        routing_mode="all-except-ru",
        next_tests=(
            "Check whether the camouflage or target site itself is reachable from Russia without the contour.",
            "Test the same contour from a different provider or move to a different hoster or ASN.",
        ),
    ),
    FailureMode(
        key="local-dpi-only",
        summary="A few blocked sites on one machine; local DPI desync may be enough",
        preferred_chat="ITDog Chat",
        keywords=(
            "zapret",
            "goodbyedpi",
            "podkop",
            "single device",
            "few blocked sites",
            "browser only",
            "desktop only",
        ),
        primary_contour="Local DPI bypass",
        backup_contour="AmneziaWG 2.0",
        routing_mode="targeted-local-bypass",
        next_tests=(
            "Confirm the issue is limited to a few blocked services on one device before rolling out a full tunnel.",
            "Keep a real VPN backup if the use case includes foreign dev infrastructure, not just browsing.",
        ),
    ),
)


EXPECTED_FIELDS = (
    "region",
    "provider_name",
    "provider_type",
    "scope",
    "client_os",
    "router_model",
    "target_service",
    "current_stack",
)


def normalize(text: str) -> str:
    return text.casefold()


def flatten_case_text(case: dict) -> str:
    chunks: list[str] = []
    for key in ("region", "provider_name", "provider_type", "scope", "client_os", "router_model", "target_service"):
        value = case.get(key)
        if value:
            chunks.append(str(value))

    for item in case.get("symptoms", []):
        chunks.append(str(item))
    for item in case.get("needs", []):
        chunks.append(str(item))

    current_stack = case.get("current_stack") or {}
    if isinstance(current_stack, dict):
        for value in current_stack.values():
            if value is not None:
                chunks.append(str(value))

    return normalize(" ".join(chunks))


def score_failure_modes(case: dict) -> dict[str, int]:
    text = flatten_case_text(case)
    scores: dict[str, int] = {}
    for mode in FAILURE_MODES:
        score = sum(1 for keyword in mode.keywords if keyword.casefold() in text)
        if mode.key == "443-tls-policing":
            current_stack = case.get("current_stack") or {}
            if current_stack.get("port") == 443:
                score += 2
        scores[mode.key] = score
    return scores


def mode_by_key(key: str) -> FailureMode:
    for mode in FAILURE_MODES:
        if mode.key == key:
            return mode
    raise KeyError(key)


def dominant_mode(case: dict) -> FailureMode:
    scores = score_failure_modes(case)
    top_key, top_score = max(scores.items(), key=lambda item: item[1])
    if top_score <= 0:
        return mode_by_key("cloudflare-or-asn")
    return mode_by_key(top_key)

