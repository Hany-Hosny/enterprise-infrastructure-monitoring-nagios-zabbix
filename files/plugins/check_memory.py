#!/usr/bin/env python3
"""Nagios plugin reporting used Linux memory as MemTotal minus MemAvailable."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3


def parse_meminfo(text: str) -> tuple[int, int]:
    values: dict[str, int] = {}
    for line in text.splitlines():
        fields = line.split()
        if len(fields) >= 2 and fields[0].endswith(":"):
            try:
                values[fields[0][:-1]] = int(fields[1])
            except ValueError:
                continue
    total = values.get("MemTotal")
    available = values.get("MemAvailable")
    if total is None or available is None or total <= 0:
        raise ValueError("MemTotal or MemAvailable is missing")
    return total, max(0, min(available, total))


def evaluate(text: str, warning: float, critical: float) -> tuple[int, str]:
    if not 0 <= warning < critical <= 100:
        raise ValueError("thresholds must satisfy 0 <= warning < critical <= 100")
    total_kib, available_kib = parse_meminfo(text)
    used_percent = (total_kib - available_kib) * 100.0 / total_kib
    state = CRITICAL if used_percent >= critical else WARNING if used_percent >= warning else OK
    label = {OK: "OK", WARNING: "WARNING", CRITICAL: "CRITICAL"}[state]
    output = (
        f"{label} - memory used {used_percent:.1f}% "
        f"({total_kib - available_kib} KiB / {total_kib} KiB) "
        f"| used={used_percent:.1f}%;{warning:g};{critical:g};0;100"
    )
    return state, output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-w", "--warning", type=float, default=80)
    parser.add_argument("-c", "--critical", type=float, default=90)
    parser.add_argument("--meminfo", default="/proc/meminfo")
    args = parser.parse_args()
    try:
        text = Path(args.meminfo).read_text(encoding="ascii")
        state, output = evaluate(text, args.warning, args.critical)
    except (OSError, ValueError) as exc:
        print(f"UNKNOWN - {exc}")
        return UNKNOWN
    print(output)
    return state


if __name__ == "__main__":
    sys.exit(main())
