#!/usr/bin/env python3
"""Build macro JSON for AscensionFX WebRequest fallback.

Fetches daily close data for US10Y, WTI, Copper, SPX from Yahoo Finance
and writes a JSON file compatible with Macro.mqh WebRequest parser.

Output JSON format:
  {
    "updated": "2026-05-15T12:00:00Z",
    "US10Y": [{"d": "2026.05.13", "c": 4.45}, ...],
    "WTI":   [{"d": "2026.05.13", "c": 78.12}, ...],
    "Copper":[{"d": "2026.05.13", "c": 4.82}, ...],
    "SPX":   [{"d": "2026.05.13", "c": 5308.15}, ...]
  }

Designed to run in GitHub Actions (fx_calendar_public repo) on a daily cron.
Also usable locally for testing.

Usage:
    pip install yfinance
    python tools/build_macro_json.py --out-dir /path/to/output

    # Default output: macro/macro_data.json (relative to CWD)
    python tools/build_macro_json.py
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

# Yahoo Finance ticker → AscensionFX feed ID mapping
FEEDS = {
    "^TNX": "US10Y",     # CBOE 10-Year Treasury Note Yield
    "CL=F": "WTI",       # WTI Crude Oil Futures
    "HG=F": "Copper",    # Copper Futures
    "^GSPC": "SPX",      # S&P 500 Index
}

LOOKBACK_DAYS = 60  # enough for shift=1..2 with weekends/holidays


def fetch_feed(ticker: str, feed_id: str, days: int) -> list[dict]:
    """Fetch daily close data from Yahoo Finance."""
    import yfinance as yf

    tk = yf.Ticker(ticker)
    hist = tk.history(period=f"{days}d", interval="1d")

    if hist.empty:
        print(f"  WARN {feed_id} ({ticker}): no data returned", file=sys.stderr)
        return []

    rows = []
    for ts, row in hist.iterrows():
        close_val = float(row["Close"])
        if close_val <= 0:
            continue
        # Format date as YYYY.MM.DD (MT5 StringToTime compatible)
        date_str = ts.strftime("%Y.%m.%d")
        rows.append({"d": date_str, "c": round(close_val, 6)})

    print(f"  OK {feed_id} ({ticker}): {len(rows)} rows")
    return rows


def build_macro_json(out_dir: Path) -> int:
    """Fetch all feeds and write macro_data.json."""
    out_dir.mkdir(parents=True, exist_ok=True)

    data: dict = {
        "updated": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    total = 0
    for ticker, feed_id in FEEDS.items():
        rows = fetch_feed(ticker, feed_id, LOOKBACK_DAYS)
        data[feed_id] = rows
        total += len(rows)

    if total == 0:
        print("ERROR: No data fetched for any feed.", file=sys.stderr)
        return 1

    out_path = out_dir / "macro_data.json"
    with open(out_path, "w") as f:
        json.dump(data, f, separators=(",", ":"))

    print(f"\nDone. {total} total rows → {out_path}")
    print(f"Updated: {data['updated']}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--out-dir",
        default="macro",
        help="Output directory (default: macro/)",
    )
    args = p.parse_args()

    return build_macro_json(Path(args.out_dir))


if __name__ == "__main__":
    sys.exit(main())
