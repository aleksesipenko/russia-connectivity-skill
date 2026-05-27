#!/usr/bin/env python3

from __future__ import annotations

import datetime as dt
import subprocess
import sys
import urllib.error
import urllib.request

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Codex Russia Connectivity Source Check/1.0)",
}


REPOS = [
    ("runetfreedom/russia-v2ray-rules-dat", "https://github.com/runetfreedom/russia-v2ray-rules-dat.git"),
    ("runetfreedom/russia-v2ray-custom-routing-list", "https://github.com/runetfreedom/russia-v2ray-custom-routing-list.git"),
    ("runetfreedom/geodat2srs", "https://github.com/runetfreedom/geodat2srs.git"),
    ("bol-van/zapret", "https://github.com/bol-van/zapret.git"),
]

DOCS = [
    ("Amnezia protocols", "https://docs.amnezia.org/documentation/protocols-info/"),
    ("AmneziaWG 2.0 self-hosted", "https://docs.amnezia.org/documentation/instructions/new-amneziawg-selfhosted/"),
    ("Xray REALITY", "https://xtls.github.io/en/config/transports/reality.html"),
    ("Hysteria2 protocol", "https://v2.hysteria.network/docs/developers/Protocol/"),
    ("sing-box TLS", "https://sing-box.sagernet.org/configuration/shared/tls/"),
    ("Cloudflare RU throttling post", "https://blog.cloudflare.com/russian-internet-users-are-unable-to-access-the-open-internet/"),
]


def repo_head(url: str) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["git", "ls-remote", url, "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)

    line = result.stdout.strip()
    if not line:
        return False, "empty response"
    sha = line.split()[0]
    return True, sha


def head_request(url: str) -> tuple[bool, str]:
    request = urllib.request.Request(url, headers=HEADERS, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            last_modified = response.headers.get("Last-Modified", "n/a")
            return True, f"{response.status} Last-Modified={last_modified}"
    except urllib.error.HTTPError as exc:
        if exc.code in {403, 405}:
            request = urllib.request.Request(url, headers=HEADERS, method="GET")
            with urllib.request.urlopen(request, timeout=20) as response:
                last_modified = response.headers.get("Last-Modified", "n/a")
                return True, f"{response.status} Last-Modified={last_modified}"
        return False, f"HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def main() -> int:
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    print(f"Russia connectivity source check at {now}")
    print()
    print("Repositories")
    for name, url in REPOS:
        ok, info = repo_head(url)
        status = "OK" if ok else "ERR"
        print(f"- [{status}] {name}: {info}")

    print()
    print("Docs and monitoring URLs")
    for name, url in DOCS:
        ok, info = head_request(url)
        status = "OK" if ok else "ERR"
        print(f"- [{status}] {name}: {info}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
