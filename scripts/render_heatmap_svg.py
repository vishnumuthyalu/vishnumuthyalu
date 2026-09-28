"""Render data/contributions.json -> contrib-heatmap.svg (animated, no JS)."""
import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BG, FG, DIM, ACCENT = "#0d1117", "#c9d1d9", "#6e7681", "#39d353"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

W = 860
CELL, GAP = 12, 3
STEP = CELL + GAP
PAD_X = 20
LABEL_W = 30
GRID_X = PAD_X + LABEL_W
GRID_Y = 58
STAGGER = 0.014  # seconds per diagonal step


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> None:
    data = json.loads(DATA.read_text())
    st = data["stats"]
    # exactly 53 week-columns: Sunday 52 weeks before the latest week, through today
    last = date.fromisoformat(data["days"][-1]["date"])
    cutoff = last - timedelta(days=(last.weekday() + 1) % 7) - timedelta(weeks=52)
    days = [d for d in data["days"] if date.fromisoformat(d["date"]) >= cutoff]

    # top 5% of active days get the neon level-5 colour
    active = sorted(d["count"] for d in days if d["count"] > 0)
    neon = active[int(len(active) * 0.95)] if len(active) >= 20 else float("inf")

    first = date.fromisoformat(days[0]["date"])
    start = first - timedelta(days=(first.weekday() + 1) % 7)  # back up to Sunday

    cells, months, last_month = [], [], None
    max_week = 0
    for d in days:
        dt = date.fromisoformat(d["date"])
        idx = (dt - start).days
        w, dow = divmod(idx, 7)
        max_week = max(max_week, w)
        level = 5 if d["count"] >= neon and d["count"] > 0 else min(d["level"], 4)
        x, y = GRID_X + w * STEP, GRID_Y + dow * STEP
        delay = (w + dow) * STAGGER
        tip = f"{d['count']} contribution{'s' if d['count'] != 1 else ''} on {dt:%b %-d, %Y}"
        cells.append(
            f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
            f'fill="{PALETTE[level]}" style="animation-delay:{delay:.3f}s"><title>{tip}</title></rect>'
        )
        if dow == 0 and dt.month != last_month and dt.day <= 7:
            months.append(f'<text x="{x}" y="{GRID_Y - 8}" class="m">{dt:%b}</text>')
            last_month = dt.month

    grid_bottom = GRID_Y + 7 * STEP
    total_delay = (max_week + 6) * STAGGER + 0.4

    dow_labels = "".join(
        f'<text x="{PAD_X}" y="{GRID_Y + i * STEP + 10}" class="m">{n}</text>'
        for i, n in ((1, "Mon"), (3, "Wed"), (5, "Fri"))
    )

    lx = W - PAD_X - 5 * STEP - 70
    legend = f'<text x="{lx - 34}" y="{grid_bottom + 22}" class="m">Less</text>' + "".join(
        f'<rect x="{lx + i * STEP}" y="{grid_bottom + 12}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>'
        for i, c in enumerate(PALETTE)
    ) + f'<text x="{lx + 6 * STEP + 4}" y="{grid_bottom + 22}" class="m">More</text>'

    footer = (
        f'<tspan class="hi">{st["total"]:,}</tspan> contributions in the last year'
        f'  ·  current streak <tspan class="hi">{st["current_streak"]}d</tspan>'
        f'  ·  longest <tspan class="hi">{st["longest_streak"]}d</tspan>'
    )
    H = grid_bottom + 62

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{st['total']} GitHub contributions in the last year">
<style>
  text {{ font-family: {FONT}; }}
  .m {{ fill: {DIM}; font-size: 10px; }}
  .t {{ fill: {FG}; font-size: 13px; }}
  .p {{ fill: {ACCENT}; font-size: 13px; }}
  .f {{ fill: {DIM}; font-size: 11.5px; }}
  .hi {{ fill: {FG}; font-weight: 600; }}
  .c {{ opacity: 0; transform-box: fill-box; transform-origin: center;
        animation: drop .45s cubic-bezier(.2,.8,.2,1) forwards; }}
  @keyframes drop {{ from {{ opacity: 0; transform: translateY(-7px) scale(.6); }}
                     to   {{ opacity: 1; transform: none; }} }}
  .fade {{ opacity: 0; animation: fade .6s ease forwards; animation-delay: {total_delay:.2f}s; }}
  @keyframes fade {{ to {{ opacity: 1; }} }}
</style>
<rect width="{W}" height="{H}" rx="10" fill="{BG}" stroke="#30363d"/>
<text x="{PAD_X}" y="26" class="p">$ <tspan class="t">git log --since="1 year ago" | heatmap</tspan></text>
{"".join(months)}
{dow_labels}
{"".join(cells)}
<g class="fade">{legend}
<text x="{PAD_X}" y="{grid_bottom + 22}" class="f">{footer}</text>
<text x="{PAD_X}" y="{grid_bottom + 44}" class="m">updated {esc(data.get("generated", ""))} · auto-refreshed daily by GitHub Actions</text></g>
</svg>
'''
    OUT.write_text(svg)
    print(f"wrote {OUT.name} ({len(cells)} days)")


if __name__ == "__main__":
    main()
