"""Hand-authored neofetch-style info card -> info-card.svg.

Edit the ROWS / HIGHLIGHTS below when your details change, then re-run.
STATIC=1 python scripts/make_info_card.py  -> frozen frame (handy for previews)
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

W, H = 490, 380
BG, FG, DIM, BORDER = "#0d1117", "#c9d1d9", "#6e7681", "#30363d"
KEY = "#58a6ff"
ACCENT = "#39d353"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

USER, HOST = "vishnu", "github"

ROWS = [
    ("OS", "Rice University · MS Computer Science"),
    ("Uptime", "Fall 2026 → May 2028"),
    ("Now", "Seeking Summer 2027 SWE internships"),
    ("Focus", "Backend · Full-stack · Infra · Data"),
    ("Langs", "TypeScript, Python, Java, Kotlin, SQL"),
    ("Stack", "Node/Express, React, PostgreSQL, Prisma"),
    ("Infra", "Docker, Kubernetes, NGINX, GH Actions"),
]
HIGHLIGHTS = [
    "Waypoint API: spec-first URL shortener on k8s",
    "Relay: git push → AI-written client updates",
    "Credit risk scorecard on 1.27M loans",
]
CONTACT = ("Mail", "vm17college@gmail.com")

SWATCHES = ["#484f58", "#ff7b72", "#3fb950", "#d29922", "#58a6ff", "#bc8cff", "#39c5cf", "#c9d1d9"]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> None:
    lines, y, i = [], 72, 0
    LH = 20

    def line(content: str, extra_gap: int = 0):
        nonlocal y, i
        y += extra_gap
        cls = "" if STATIC else f' class="ln" style="animation-delay:{0.35 + i * 0.11:.2f}s"'
        lines.append(f"<g{cls}>{content.format(y=y)}</g>")
        y += LH
        i += 1

    title = f"{USER}@{HOST}"
    line(f'<text x="24" y="{{y}}"><tspan class="u">{USER}</tspan><tspan class="d">@</tspan><tspan class="u">{HOST}</tspan></text>')
    line(f'<text x="24" y="{{y}}" class="d">{"-" * len(title)}</text>', -6)
    for k, v in ROWS:
        line(f'<text x="24" y="{{y}}"><tspan class="k">{k}</tspan><tspan class="d">:</tspan><tspan x="104" class="v">{esc(v)}</tspan></text>')
    line('<text x="24" y="{y}"><tspan class="k">Highlights</tspan><tspan class="d">:</tspan></text>', 4)
    for h in HIGHLIGHTS:
        line(f'<text x="34" y="{{y}}"><tspan class="a">›</tspan><tspan x="50" class="v">{esc(h)}</tspan></text>', -2)
    k, v = CONTACT
    line(f'<text x="24" y="{{y}}"><tspan class="k">{k}</tspan><tspan class="d">:</tspan><tspan x="104" class="v">{esc(v)}</tspan></text>', 4)
    sw = "".join(
        f'<rect x="{24 + n * 24}" y="{{y}}" width="22" height="12" rx="2" fill="{c}"/>'
        for n, c in enumerate(SWATCHES)
    )
    line(sw.replace("{y}", "{y}"), 2)

    anim = "" if STATIC else """
  .ln { opacity: 0; animation: in .35s ease-out forwards; }
  @keyframes in { from { opacity: 0; transform: translateX(-6px); } to { opacity: 1; transform: none; } }
  .cur { animation: blink 1s steps(1) infinite; }
  @keyframes blink { 50% { opacity: 0; } }"""

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{USER} - {esc(ROWS[0][1])}">
<style>
  text {{ font-family: {FONT}; font-size: 12.5px; fill: {FG}; }}
  .u {{ fill: {ACCENT}; font-weight: 700; }}
  .k {{ fill: {KEY}; font-weight: 700; }}
  .v {{ fill: {FG}; }}
  .d {{ fill: {DIM}; }}
  .a {{ fill: {ACCENT}; }}
  .bar {{ fill: {DIM}; font-size: 11px; }}{anim}
</style>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<path d="M.5 30.5h{W - 1}" stroke="{BORDER}"/>
<circle cx="18" cy="15.5" r="5.5" fill="#ff5f57"/><circle cx="36" cy="15.5" r="5.5" fill="#febc2e"/><circle cx="54" cy="15.5" r="5.5" fill="#28c840"/>
<text x="{W / 2}" y="19.5" text-anchor="middle" class="bar">{title} — neofetch</text>
<text x="24" y="54" class="d"><tspan class="a">$</tspan> neofetch</text>
{chr(10).join(lines)}
</svg>
'''
    OUT.write_text(svg)
    print(f"wrote {OUT.name} (last baseline y={y - LH}, height {H})")


if __name__ == "__main__":
    main()
