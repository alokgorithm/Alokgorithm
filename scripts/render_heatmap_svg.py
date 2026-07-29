"""
render_heatmap_svg.py — Render data/contributions.json as an animated
53-week × 7-day contribution heatmap SVG.

Uses CSS @keyframes for a diagonal slide-in. Plays once, freezes.
"""
import json
from datetime import datetime
from pathlib import Path

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
CELL = 11
GAP = 3
MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]


def render():
    root = Path(__file__).resolve().parent.parent
    in_file = root / "data" / "contributions.json"
    out_file = root / "contrib-heatmap.svg"

    if not in_file.exists():
        print(f"Error: {in_file} not found. Run fetch_contributions.py first.")
        return

    data = json.loads(in_file.read_text(encoding="utf-8"))
    days = data.get("days", [])
    total = data.get("total", 0)
    longest = data.get("longest_streak", 0)
    current = data.get("current_streak", 0)

    # Build week columns
    weeks = []
    cur_week = []
    for d in days:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        if not cur_week and dt.weekday() != 6:
            # Pad to start on Sunday
            for _ in range((dt.weekday() + 1) % 7):
                cur_week.append(None)
        cur_week.append(d)
        if len(cur_week) == 7:
            weeks.append(cur_week)
            cur_week = []
    if cur_week:
        while len(cur_week) < 7:
            cur_week.append(None)
        weeks.append(cur_week)
    weeks = weeks[-53:]

    grid_w = len(weeks) * (CELL + GAP)
    grid_h = 7 * (CELL + GAP)
    svg_w = grid_w + 80
    svg_h = grid_h + 100

    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">')
    lines.append("""  <style>
    .t { font-family: Consolas, 'Courier New', monospace; font-size: 12px; fill: #c9d1d9; }
    .lbl { font-family: Consolas, 'Courier New', monospace; font-size: 10px; fill: #8b949e; }
    .mo { font-family: Consolas, 'Courier New', monospace; font-size: 11px; fill: #8b949e; }
    .stat { font-family: Consolas, 'Courier New', monospace; font-size: 11px; fill: #58a6ff; }
    .col { opacity: 0; animation: slideIn 0.5s ease-out forwards; }
    @keyframes slideIn { to { opacity: 1; } }
  </style>""")

    # Background
    lines.append(f'  <rect width="{svg_w}" height="{svg_h}" rx="8" fill="#0d1117" stroke="#30363d" stroke-width="1"/>')

    # Chrome dots
    lines.append('  <circle cx="20" cy="20" r="6" fill="#ff5f56"/>')
    lines.append('  <circle cx="40" cy="20" r="6" fill="#ffbd2e"/>')
    lines.append('  <circle cx="60" cy="20" r="6" fill="#27c93f"/>')
    lines.append(f'  <text x="{svg_w // 2}" y="24" class="t" text-anchor="middle" font-weight="bold">alok@github: ~$ ./contributions.sh</text>')

    # Grid
    ox, oy = 50, 55
    lines.append(f'  <g transform="translate({ox}, {oy})">')

    # Month labels
    last_month = None
    for c, week in enumerate(weeks):
        for d in week:
            if d:
                dt = datetime.strptime(d["date"], "%Y-%m-%d")
                if dt.month != last_month:
                    if last_month is not None or dt.day <= 15:
                        mx = c * (CELL + GAP)
                        lines.append(f'    <text x="{mx}" y="-5" class="mo">{MONTH_NAMES[dt.month - 1]}</text>')
                    last_month = dt.month
                break

    # Day labels
    lines.append(f'    <text x="-30" y="{1 * (CELL + GAP) + 9}" class="lbl">Mon</text>')
    lines.append(f'    <text x="-30" y="{3 * (CELL + GAP) + 9}" class="lbl">Wed</text>')
    lines.append(f'    <text x="-30" y="{5 * (CELL + GAP) + 9}" class="lbl">Fri</text>')

    # Cells, grouped by column with staggered animation
    for c, week in enumerate(weeks):
        delay = c * 0.03
        lines.append(f'    <g class="col" style="animation-delay:{delay:.2f}s">')
        for r, day in enumerate(week):
            if day:
                x = c * (CELL + GAP)
                y = r * (CELL + GAP)
                lvl = min(day.get("level", 0), len(PALETTE) - 1)
                color = PALETTE[lvl]
                cnt = day.get("count", 0)
                ds = day.get("date", "")
                lines.append(f'      <rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"><title>{cnt} contributions on {ds}</title></rect>')
        lines.append('    </g>')

    # Legend
    ly = grid_h + 15
    lines.append(f'    <text x="0" y="{ly + 10}" class="t">{total} contributions in the last year</text>')

    lx = grid_w - 110
    lines.append(f'    <text x="{lx - 30}" y="{ly + 10}" class="lbl">Less</text>')
    for i in range(5):
        lines.append(f'    <rect x="{lx + i * 15}" y="{ly}" width="{CELL}" height="{CELL}" rx="2" fill="{PALETTE[i]}"/>')
    lines.append(f'    <text x="{lx + 5 * 15 + 5}" y="{ly + 10}" class="lbl">More</text>')

    lines.append('  </g>')

    # Stats footer
    fy = oy + grid_h + 50
    lines.append(f'  <text x="{ox}" y="{fy}" class="stat">Current streak: {current} days  ·  Longest: {longest} days  ·  Best day: {data.get("best_day", 0)}</text>')

    lines.append('</svg>')

    out_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"Heatmap -> {out_file} ({svg_w}x{svg_h})")


if __name__ == "__main__":
    render()
