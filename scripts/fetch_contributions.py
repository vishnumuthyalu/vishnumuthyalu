"""Scrape the public contribution calendar (no token) -> data/contributions.json.

GitHub serves the same HTML fragment the profile page uses at
https://github.com/users/<username>/contributions
"""
import json
import os
import re
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_USERNAME", "vishnumuthyalu")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "contributions.json"


def fetch_html() -> str:
    r = requests.get(
        f"https://github.com/users/{USERNAME}/contributions",
        headers={"User-Agent": "profile-readme-heatmap"},
        timeout=30,
    )
    r.raise_for_status()
    return r.text


def parse(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")

    # Counts live in <tool-tip for="<cell id>">N contributions on ...</tool-tip>
    counts = {}
    for tip in soup.find_all("tool-tip"):
        target = tip.get("for")
        text = tip.get_text(" ", strip=True)
        m = re.match(r"([\d,]+) contributions?", text)
        counts[target] = int(m.group(1).replace(",", "")) if m else 0

    days = []
    for cell in soup.select("td.ContributionCalendar-day[data-date]"):
        cid = cell.get("id")
        count = counts.get(cid)
        if count is None:  # older markup kept the count on the cell
            count = int(cell.get("data-count", 0) or 0)
        days.append(
            {
                "date": cell["data-date"],
                "count": count,
                "level": int(cell.get("data-level", 0) or 0),
            }
        )
    days.sort(key=lambda d: d["date"])
    if not days:
        raise SystemExit("No contribution cells found - GitHub markup may have changed.")
    return days


def stats(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        longest = max(longest, run)

    # current streak: today may still be empty, so allow starting from yesterday
    current = 0
    rev = list(reversed(days))
    if rev and rev[0]["count"] == 0:
        rev = rev[1:]
    for d in rev:
        if d["count"] == 0:
            break
        current += 1

    best = max(days, key=lambda d: d["count"])
    monthly = defaultdict(int)
    for d in days:
        monthly[d["date"][:7]] += d["count"]

    return {
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "active_days": sum(1 for d in days if d["count"] > 0),
        "monthly": dict(sorted(monthly.items())),
    }


def main() -> None:
    days = parse(fetch_html())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(
            {"username": USERNAME, "generated": date.today().isoformat(),
             "stats": stats(days), "days": days},
            indent=1,
        )
    )
    s = stats(days)
    print(f"{len(days)} days, {s['total']} contributions, streak {s['current_streak']}")


if __name__ == "__main__":
    main()
