#!/usr/bin/env python3
"""Generate retro-CRT pastel-plum GitHub contribution trail SVGs."""

from __future__ import annotations

import argparse
from datetime import date
import html
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


GRAPHQL_QUERY = """query($login:String!) {
  user(login:$login) {
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      contributionCalendar {
        totalContributions
        weeks {
          firstDay
          contributionDays {
            date
            weekday
            contributionCount
            contributionLevel
          }
        }
      }
    }
  }
}"""

LEVEL_ORDER = (
    "FIRST_QUARTILE",
    "SECOND_QUARTILE",
    "THIRD_QUARTILE",
    "FOURTH_QUARTILE",
)

PINK_TIERS = {
    "NONE": ("#3b3444", "#4a4056"),
    "FIRST_QUARTILE": ("#7d4f65", "#9b6680"),
    "SECOND_QUARTILE": ("#b46f8b", "#d18aa6"),
    "THIRD_QUARTILE": ("#e09ab4", "#f0b6cb"),
    "FOURTH_QUARTILE": ("#f7c2d3", "#ffe1eb"),
}

SAGE_TIERS = (
    ("FIRST_QUARTILE", "L1 Light", "#446b5a"),
    ("SECOND_QUARTILE", "L2 Steady", "#689777"),
    ("THIRD_QUARTILE", "L3 High", "#96c99b"),
    ("FOURTH_QUARTILE", "L4 Peak", "#c6ecb8"),
)

MONO_FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SANS_FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif"


def fetch_activity(owner: str) -> dict[str, Any]:
    """Fetch contribution collection data for `owner` via GitHub CLI."""
    raw = subprocess.check_output(
        [
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={GRAPHQL_QUERY}",
            "-f",
            f"login={owner}",
        ],
        text=True,
    )
    return extract_collection(json.loads(raw))


def extract_collection(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize either a raw GraphQL response or a contributionsCollection dict."""
    if "data" in payload:
        user = payload["data"].get("user")
        if not user:
            raise ValueError("GraphQL response returned no user object")
        return user["contributionsCollection"]
    if "contributionCalendar" in payload:
        return payload
    raise ValueError("Unrecognized contribution payload structure")


def render_stats_svg(activity: dict[str, Any]) -> str:
    """Render the 4-column past-year contribution stats card."""
    calendar = activity["contributionCalendar"]
    all_days = [
        day
        for week in calendar.get("weeks", [])
        for day in week.get("contributionDays", [])
    ]
    metrics = [
        ("Contributions", int(calendar.get("totalContributions", 0))),
        ("Active days", sum(1 for day in all_days if day.get("contributionCount", 0) > 0)),
        ("Commits", int(activity.get("totalCommitContributions", 0))),
        ("Pull requests", int(activity.get("totalPullRequestContributions", 0))),
    ]
    summary = ", ".join(f"{value:,} {label.lower()}" for label, value in metrics)

    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="104" viewBox="0 0 640 104" role="img" aria-labelledby="stats-title">',
        f'  <title id="stats-title">Past year on GitHub — {html.escape(summary)}</title>',
        '  <rect x="1" y="1" width="638" height="102" rx="11" fill="#251f2d" stroke="#5b4760" stroke-width="1.5"/>',
        '  <path d="M10 20V10h10M620 10h10v10M10 84v10h10M630 84v10h-10" fill="none" stroke="#987285" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>',
    ]
    for idx, (label, value) in enumerate(metrics):
        x = 22 + idx * 160
        if idx:
            lines.append(f'  <path d="M{x - 22} 20v64" stroke="#514353" stroke-width="1.2"/>')
        lines.append(
            f'  <text x="{x}" y="52" font-family="{MONO_FONT}" font-size="34" font-weight="bold" fill="#f7c2d3">{value:,}</text>'
        )
        lines.append(
            f'  <text x="{x}" y="80" font-family="{SANS_FONT}" font-size="15" fill="#f4e2d9">{html.escape(label)}</text>'
        )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def format_window_range(window_weeks: list[dict[str, Any]]) -> str:
    """Format the header date range string across the rolling week window."""
    if not window_weeks:
        return "NO ACTIVITY DATA"
    first_days = window_weeks[0].get("contributionDays", [])
    last_days = window_weeks[-1].get("contributionDays", [])
    start_str = window_weeks[0].get("firstDay") or (first_days[0]["date"] if first_days else "")
    end_str = last_days[-1]["date"] if last_days else window_weeks[-1].get("firstDay", start_str)
    if not start_str or not end_str:
        return ""
    start_dt = date.fromisoformat(start_str)
    end_dt = date.fromisoformat(end_str)
    if start_dt.year == end_dt.year:
        return f"{start_dt:%b %d}–{end_dt:%b %d, %Y}".upper()
    return f"{start_dt:%b %d, %Y}–{end_dt:%b %d, %Y}".upper()


def compute_month_labels(
    window_weeks: list[dict[str, Any]],
    grid_x: int,
    pitch: int,
) -> list[tuple[int, str]]:
    """Place collision-free month labels above month-start columns."""
    candidates: list[tuple[int, str]] = []
    prev_ym: tuple[int, int] | None = None

    for col, week in enumerate(window_weeks):
        ref_date_str = week.get("firstDay")
        if not ref_date_str and week.get("contributionDays"):
            ref_date_str = week["contributionDays"][0]["date"]
        if not ref_date_str:
            continue
        dt = date.fromisoformat(ref_date_str)
        ym = (dt.year, dt.month)
        if ym != prev_ym:
            # Drop column 0 label if the next month starts immediately at column 1.
            if candidates and col == 1 and candidates[-1][0] == grid_x:
                candidates.pop()
            x = grid_x + col * pitch
            candidates.append((x, dt.strftime("%b")))
            prev_ym = ym

    placed: list[tuple[int, str]] = []
    for x, label in candidates:
        if x > 596:
            continue
        if placed and x - placed[-1][0] < 44:
            continue
        placed.append((x, label))
    return placed


def compute_bar_segments(
    tier_counts: dict[str, int],
    bar_x: int,
    bar_width: int,
    gap: int = 2,
) -> list[tuple[int, int, str]]:
    """Compute pixel-exact rounded segment widths summing cleanly to `bar_width`."""
    nonzero = [(color, tier_counts[level]) for level, _label, color in SAGE_TIERS if tier_counts[level] > 0]
    if not nonzero:
        return []

    total = sum(count for _color, count in nonzero)
    usable = bar_width - gap * (len(nonzero) - 1)
    raw_widths = [max(4, round(usable * count / total)) for _color, count in nonzero]

    # Adjust largest segment so total used width matches `usable` to the pixel.
    diff = usable - sum(raw_widths)
    if diff != 0:
        largest_idx = max(range(len(nonzero)), key=lambda idx: nonzero[idx][1])
        raw_widths[largest_idx] = max(4, raw_widths[largest_idx] + diff)

    segments: list[tuple[int, int, str]] = []
    cursor = bar_x
    for (color, _count), width in zip(nonzero, raw_widths):
        segments.append((cursor, width, color))
        cursor += width + gap
    return segments


def render_heatmap_svg(activity: dict[str, Any], weeks_count: int = 16) -> str:
    """Render the rolling N-week contribution heatmap + sage-green intensity bar."""
    weeks = activity["contributionCalendar"].get("weeks", [])
    window_weeks = weeks[-weeks_count:] if weeks_count > 0 else list(weeks)
    num_cols = max(len(window_weeks), 1)

    grid_x = 64
    grid_y = 68
    tile_size = 27
    tile_gap = 8
    pitch = tile_size + tile_gap
    if num_cols != 16 and num_cols > 0:
        pitch = max(14, (616 - grid_x + tile_gap) // num_cols)
        tile_size = max(10, pitch - tile_gap)

    window_days = [
        day
        for week in window_weeks
        for day in week.get("contributionDays", [])
    ]
    tier_counts = {level: 0 for level in LEVEL_ORDER}
    window_total = 0
    for day in window_days:
        count = int(day.get("contributionCount", 0))
        level = day.get("contributionLevel", "NONE")
        window_total += count
        if count > 0 and level in tier_counts:
            tier_counts[level] += 1
        elif count > 0:
            tier_counts["FIRST_QUARTILE"] += 1
    active_days = sum(tier_counts.values())

    range_label = format_window_range(window_weeks)
    header_left = f"LAST {len(window_weeks)} WEEKS · {range_label}" if range_label else f"LAST {len(window_weeks)} WEEKS"
    summary_title = (
        f"Last {len(window_weeks)} weeks on GitHub: {window_total:,} contributions across {active_days} active days"
    )

    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="386" viewBox="0 0 640 386" role="img" aria-labelledby="hm-title hm-desc">',
        f'  <title id="hm-title">{html.escape(summary_title)}</title>',
        '  <desc id="hm-desc">Rolling 16-week contribution heatmap in retro pastel pink alongside a segmented sage-green activity intensity breakdown.</desc>',
        '  <defs>',
        '    <linearGradient id="hm-bg" x1="0" y1="0" x2="1" y2="1">',
        '      <stop offset="0" stop-color="#241d30"/>',
        '      <stop offset="1" stop-color="#312438"/>',
        '    </linearGradient>',
        '    <clipPath id="bar-clip"><rect x="24" y="345" width="592" height="10" rx="5"/></clipPath>',
        '    <style>',
        '      .active-tile { animation: tile-breathe 4.8s ease-in-out infinite; }',
        '      .peak-halo { animation: halo-breathe 4.8s ease-in-out infinite; }',
        '      @keyframes tile-breathe { 0%, 100% { opacity: .86; } 50% { opacity: 1; } }',
        '      @keyframes halo-breathe { 0%, 100% { opacity: .18; } 50% { opacity: .62; } }',
        '      @media (prefers-reduced-motion: reduce) { * { animation: none !important; } }',
        '    </style>',
        '  </defs>',
        '',
        '  <rect x="1" y="1" width="638" height="384" rx="12" fill="url(#hm-bg)" stroke="#5b4760" stroke-width="1.5"/>',
        '  <path d="M12 24V12h12M616 12h12v12M12 362v12h12M628 362v12h-12" fill="none" stroke="#987285" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>',
        '',
        f'  <text x="24" y="29" font-family="{MONO_FONT}" font-size="11.5" fill="#d9bec9">{html.escape(header_left)}</text>',
        f'  <text x="515" y="28.5" text-anchor="end" font-family="{MONO_FONT}" font-size="10.5" fill="#b89fb2">Less</text>',
    ]

    # Mini pastel-pink legend swatches in top-right header
    for idx, level in enumerate(("NONE", *LEVEL_ORDER)):
        fill, stroke = PINK_TIERS[level]
        sx = 523 + idx * 13
        lines.append(f'  <rect x="{sx}" y="20" width="9" height="9" rx="2.5" fill="{fill}" stroke="{stroke}" stroke-width=".8"/>')
    lines.append(f'  <text x="590" y="28.5" font-family="{MONO_FONT}" font-size="10.5" fill="#b89fb2">More</text>')

    # Month labels above grid
    for mx, month_label in compute_month_labels(window_weeks, grid_x, pitch):
        lines.append(f'  <text x="{mx}" y="56" font-family="{MONO_FONT}" font-size="11" fill="#b89fb2">{html.escape(month_label)}</text>')

    # Weekday labels aligned to Mon (row 1), Wed (row 3), Fri (row 5)
    for row_idx, day_name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        ly = grid_y + row_idx * pitch + tile_size // 2 + 4
        lines.append(f'  <text x="24" y="{ly}" font-family="{MONO_FONT}" font-size="10.5" fill="#b89fb2">{day_name}</text>')

    # Contribution tiles
    for col, week in enumerate(window_weeks):
        x = grid_x + col * pitch
        for day in week.get("contributionDays", []):
            row = int(day.get("weekday", 0))
            y = grid_y + row * pitch
            count = int(day.get("contributionCount", 0))
            level = day.get("contributionLevel", "NONE")
            if count <= 0:
                level = "NONE"
            elif level not in PINK_TIERS:
                level = "FIRST_QUARTILE"

            fill, stroke = PINK_TIERS[level]
            stroke_w = "1.2" if level == "FOURTH_QUARTILE" else "1"
            day_date = html.escape(str(day.get("date", "")))
            unit = "contribution" if count == 1 else "contributions"
            tooltip = f"{day_date}: {count} {unit}"

            if count > 0:
                delay = (col * 0.29 + row * 0.43) % 4.6
                if level == "FOURTH_QUARTILE":
                    lines.append(
                        f'  <rect class="peak-halo" x="{x - 1.5:.1f}" y="{y - 1.5:.1f}" width="{tile_size + 3}" height="{tile_size + 3}" rx="7.5" fill="none" stroke="#f7b5ca" stroke-width="2" style="animation-delay:{delay:.2f}s"/>'
                    )
                lines.append(
                    f'  <rect class="active-tile" x="{x}" y="{y}" width="{tile_size}" height="{tile_size}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w}" style="animation-delay:{delay:.2f}s"><title>{tooltip}</title></rect>'
                )
            else:
                lines.append(
                    f'  <rect x="{x}" y="{y}" width="{tile_size}" height="{tile_size}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1"><title>{tooltip}</title></rect>'
                )

    # Bottom segmented sage-green progress bar & monospace legend
    lines.extend([
        '',
        '  <path d="M24 318h592" stroke="#514353" stroke-width="1.2"/>',
        f'  <text x="24" y="336" font-family="{MONO_FONT}" font-size="10.5" fill="#b89fb2">ACTIVITY INTENSITY MIX ({len(window_weeks)}W)</text>',
        f'  <text x="616" y="336" text-anchor="end" font-family="{MONO_FONT}" font-size="10.5" fill="#c5eecb">{active_days} active days · {window_total:,} contributions</text>',
        '  <rect x="24" y="345" width="592" height="10" rx="5" fill="#3b3444"/>',
    ])

    segments = compute_bar_segments(tier_counts, bar_x=24, bar_width=592)
    if segments:
        lines.append('  <g clip-path="url(#bar-clip)">')
        for sx, sw, color in segments:
            lines.append(f'    <rect x="{sx}" y="345" width="{sw}" height="10" fill="{color}"/>')
        lines.append('  </g>')

    legend_xs = (24, 174, 324, 474)
    for lx, (level, label, color) in zip(legend_xs, SAGE_TIERS):
        cnt = tier_counts[level]
        lines.append(
            f'  <rect x="{lx}" y="363" width="9" height="9" rx="2.5" fill="{color}" stroke="#577467" stroke-width=".6"/>'
        )
        lines.append(
            f'  <text x="{lx + 15}" y="372" font-family="{MONO_FONT}" font-size="11" fill="#f4e2d9">{html.escape(label)} <tspan fill="#c5eecb">({cnt}d)</tspan></text>'
        )

    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate retro-CRT GitHub contribution SVGs.")
    parser.add_argument("--owner", default="BlushRins", help="GitHub username to query")
    parser.add_argument("--out", default="assets/contribution", help="Output directory for stats.svg and heatmap.svg")
    parser.add_argument("--weeks", type=int, default=16, help="Rolling number of recent weeks for the heatmap")
    parser.add_argument("--input", help="Optional local JSON file instead of querying GitHub GraphQL")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.input:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        activity = extract_collection(payload)
    else:
        activity = fetch_activity(args.owner)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "stats.svg").write_text(render_stats_svg(activity), encoding="utf-8")
    (out_dir / "heatmap.svg").write_text(render_heatmap_svg(activity, weeks_count=args.weeks), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
