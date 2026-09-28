"""Featured-project cards -> projects/<slug>.svg (terminal style, fades in).

Edit PROJECTS below, then:  python scripts/make_project_cards.py
Keep bullets under ~54 characters so they fit on one line.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "projects"

W, H = 425, 262
BG, FG, DIM, BORDER = "#0d1117", "#c9d1d9", "#6e7681", "#30363d"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

PROJECTS = [
    {
        "slug": "waypoint-api",
        "title": "Waypoint API",
        "accent": "#58a6ff",
        "tagline": "Spec-first URL shortener with click analytics",
        "bullets": [
            "OpenAPI 3.1 contract validates every req/response",
            "Custom aliases, link expiry, click analytics",
            "Runs on Kubernetes behind NGINX; CI/CD in Actions",
        ],
        "stack": ["TypeScript", "Express", "PostgreSQL", "Prisma", "Docker", "k8s", "NGINX"],
    },
    {
        "slug": "relay-extension",
        "title": "Relay",
        "accent": "#d2a8ff",
        "tagline": "git push → plain-English update emails for clients",
        "bullets": [
            "GitHub webhooks trigger Claude to summarize commits",
            "Non-technical summaries emailed on every push",
            "VS Code extension: one-click webhook + client setup",
        ],
        "stack": ["TypeScript", "Node.js", "Express", "Claude API", "SQLite", "Docker"],
    },
    {
        "slug": "Credit-Risk-Scorecard-Model-Validation-Framework",
        "title": "Credit Risk Scorecard",
        "path": "credit-risk-scorecard",  # display path; repo name is too long for the bar
        "accent": "#f0883e",
        "tagline": "Bank-grade scorecard + model validation framework",
        "bullets": [
            "1.27M Lending Club loans, $18.5B exposure (2007-18)",
            "WoE features → PDO-scaled logistic scorecard",
            "Discrimination, calibration, PSI, fair-lending checks",
        ],
        "stack": ["Python", "pandas", "scikit-learn", "statsmodels", "pytest"],
    },
    {
        "slug": "cell-tower-optimizer",
        "title": "Cell Tower Optimizer",
        "accent": "#39d353",
        "tagline": "Max-coverage tower placement on real Census data",
        "bullets": [
            "Exact ILP vs greedy over 962 candidate sites",
            "42.6% population coverage vs 39.0% greedy (8 towers)",
            "FastAPI service + Streamlit dashboard + Folium maps",
        ],
        "stack": ["Python", "PuLP", "spopt", "FastAPI", "Streamlit", "Folium"],
    },
]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def card(p: dict) -> str:
    a = p["accent"]
    parts, n = [], 0

    def step(svg: str) -> None:
        nonlocal n
        parts.append(f'<g class="ln" style="animation-delay:{0.15 + n * 0.09:.2f}s">{svg}</g>')
        n += 1

    step(f'<text x="22" y="68" class="t">{esc(p["title"])}</text>')
    step(f'<text x="22" y="92" class="tag">{esc(p["tagline"])}</text>')
    for i, b in enumerate(p["bullets"]):
        y = 124 + i * 23
        step(f'<text x="22" y="{y}" class="ar">▸</text><text x="38" y="{y}" class="b">{esc(b)}</text>')

    # stack chips, wrapped to the card width
    x, y, chips = 22, 198, []
    for s in p["stack"]:
        w = len(s) * 6.3 + 16
        if x + w > W - 22:
            x, y = 22, y + 24
        chips.append(
            f'<rect x="{x}" y="{y}" width="{w:.1f}" height="19" rx="9.5" fill="{a}" fill-opacity=".12" stroke="{a}" stroke-opacity=".45"/>'
            f'<text x="{x + w / 2:.1f}" y="{y + 13}" text-anchor="middle" class="chip">{esc(s)}</text>'
        )
        x += w + 6
    step("".join(chips))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(p["title"])}: {esc(p["tagline"])}">
<style>
  text {{ font-family: {FONT}; }}
  .t {{ fill: {a}; font-size: 19px; font-weight: 700; }}
  .tag {{ fill: {FG}; font-size: 12px; }}
  .b {{ fill: {FG}; font-size: 11.5px; }}
  .ar {{ fill: {a}; font-size: 11.5px; }}
  .chip {{ fill: {FG}; font-size: 10.5px; }}
  .bar {{ fill: {DIM}; font-size: 11px; }}
  .go {{ fill: {a}; font-size: 11px; }}
  .ln {{ opacity: 0; animation: in .4s ease-out forwards; }}
  @keyframes in {{ from {{ opacity: 0; transform: translateY(4px); }} to {{ opacity: 1; transform: none; }} }}
</style>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<rect x="1" y="1" width="3" height="{H - 2}" rx="1.5" fill="{a}"/>
<path d="M.5 30.5h{W - 1}" stroke="{BORDER}"/>
<circle cx="20" cy="15.5" r="5" fill="#ff5f57"/><circle cx="36" cy="15.5" r="5" fill="#febc2e"/><circle cx="52" cy="15.5" r="5" fill="#28c840"/>
<text x="72" y="19.5" class="bar">~/projects/{esc(p.get("path", p["slug"]).lower())}</text>
<text x="{W - 16}" y="19.5" text-anchor="end" class="go">view repo ↗</text>
{chr(10).join(parts)}
</svg>
'''


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    for p in PROJECTS:
        (OUT_DIR / f"{p['slug'].lower()}.svg").write_text(card(p))
    print(f"wrote {len(PROJECTS)} cards to {OUT_DIR.name}/")


if __name__ == "__main__":
    main()
