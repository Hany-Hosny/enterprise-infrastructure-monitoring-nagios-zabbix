#!/usr/bin/env python3
"""Unauthenticated Zabbix apiinfo.version check for the local Nagios host."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request


def read_version(url: str, timeout: float = 5.0) -> str:
    request_data = {
        "jsonrpc": "2.0",
        "method": "apiinfo.version",
        "params": {},
        "id": 1,
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(request_data).encode("utf-8"),
        headers={"Content-Type": "application/json-rpc"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        result = json.load(response)
    if "error" in result:
        raise ValueError(result["error"].get("message", "Zabbix API returned an error"))
    version = result.get("result")
    if not isinstance(version, str) or not version:
        raise ValueError("Zabbix API response has no version")
    return version


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--url",
        default="http://127.0.0.1/zabbix/api_jsonrpc.php",
        help="Zabbix JSON-RPC endpoint",
    )
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()
    try:
        version = read_version(args.url, args.timeout)
    except (OSError, ValueError, urllib.error.URLError) as exc:
        print(f"CRITICAL - Zabbix API unavailable: {exc}")
        return 2
    print(f"OK - Zabbix API responds; version {version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
