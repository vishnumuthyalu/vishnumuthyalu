"""Featured-projects strip -> README.md, rotated daily.

Writes one table row of project cards between the PROJECTS markers in
README.md. GitHub lets a wide table scroll sideways, so visitors can scroll
or swipe through the cards, and each card links to its own repo.

The order rotates by one card per day, so a different project leads each
day. The daily workflow runs this script; you can also run it locally:
    python scripts/rotate_projects.py
"""
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
START, END = "<!-- PROJECTS:START -->", "<!-- PROJECTS:END -->"

# (card file in projects/, link, alt text). Add a card here after adding it
# to make_project_cards.py.
CARDS = [
    ("relay-extension.svg", "https://github.com/vishnumuthyalu/relay-extension",
     "Relay: hosted GitHub App that turns each push into a plain-English client email, with a remote MCP server"),
    ("waypoint-api.svg", "https://github.com/vishnumuthyalu/waypoint-api",
     "Waypoint: URL shortener split into four TypeScript microservices on Kubernetes"),
    ("whisker.svg", "https://github.com/spengjohn/Whisker-WINNER_CODERED",
     "Whisker: smart crib monitor, Best Hardware track winner at CodeRED 2026"),
    ("credit-risk-scorecard-model-validation-framework.svg",
     "https://github.com/vishnumuthyalu/Credit-Risk-Scorecard-Model-Validation-Framework",
     "Credit Risk Scorecard and model validation framework"),
    ("cell-tower-optimizer.svg", "https://github.com/vishnumuthyalu/cell-tower-optimizer",
     "Cell Tower Optimizer: max-coverage placement with ILP"),
]


def strip(today: date) -> str:
    shift = today.toordinal() % len(CARDS)
    ordered = CARDS[shift:] + CARDS[:shift]
    cells = "\n".join(
        f'    <td valign="top"><a href="{href}"><img src="./projects/{svg}" width="425" alt="{alt}" /></a></td>'
        for svg, href, alt in ordered
    )
    return (
        f"{START}\n"
        "<sub>scroll or swipe sideways for more projects →</sub>\n"
        "<table>\n"
        "  <tr>\n"
        f"{cells}\n"
        "  </tr>\n"
        "</table>\n"
        f"{END}"
    )


def main() -> None:
    text = README.read_text(encoding="utf-8")
    a, b = text.index(START), text.index(END) + len(END)
    new = text[:a] + strip(date.today()) + text[b:]
    if new != text:
        README.write_text(new, encoding="utf-8", newline="\n")
        print(f"README.md: projects strip updated, {CARDS[date.today().toordinal() % len(CARDS)][0]} first")
    else:
        print("README.md: projects strip already current")


if __name__ == "__main__":
    main()
