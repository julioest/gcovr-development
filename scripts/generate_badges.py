#!/usr/bin/env python3
"""
Generate coverage badges from gcovr output.

This script parses gcovr HTML or JSON output and generates SVG badges
in shields.io flat style for lines, functions, and branches coverage.
"""

import json
import os
import re
import sys
from pathlib import Path


# Shields.io flat-style SVG badge template
BADGE_TEMPLATE = '''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="20" role="img" aria-label="{label}: {value}%">
  <title>{label}: {value}%</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="{width}" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="{label_width}" height="20" fill="#555"/>
    <rect x="{label_width}" width="{value_width}" height="20" fill="{color}"/>
    <rect width="{width}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="110">
    <text aria-hidden="true" x="{label_x}" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)">{label}</text>
    <text x="{label_x}" y="140" transform="scale(.1)" fill="#fff">{label}</text>
    <text aria-hidden="true" x="{value_x}" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)">{value}%</text>
    <text x="{value_x}" y="140" transform="scale(.1)" fill="#fff">{value}%</text>
  </g>
</svg>'''


# Standard shields.io colors
COLORS = {
    'brightgreen': '#4c1',
    'green': '#97ca00',
    'yellowgreen': '#a4a61d',
    'yellow': '#dfb317',
    'orange': '#fe7d37',
    'red': '#e05d44',
}


def get_color_for_coverage(percentage):
    """Return shields.io color based on coverage percentage."""
    try:
        pct = float(percentage)
        if pct >= 90:
            return COLORS['brightgreen']
        elif pct >= 75:
            return COLORS['yellow']
        else:
            return COLORS['red']
    except (ValueError, TypeError):
        return COLORS['red']


def estimate_text_width(text):
    """Estimate text width in pixels (approximate)."""
    # Average character width for Verdana 11px is about 6.5-7px
    return len(text) * 7 + 10


def generate_badge_svg(label, value):
    """Generate an SVG badge with the given label and value."""
    value_str = f"{value:.0f}" if isinstance(value, float) else str(value)

    label_width = estimate_text_width(label)
    value_width = estimate_text_width(f"{value_str}%")
    total_width = label_width + value_width

    color = get_color_for_coverage(value)

    # Calculate text positions (center of each section, scaled by 10 for transform)
    label_x = (label_width / 2) * 10
    value_x = (label_width + value_width / 2) * 10

    return BADGE_TEMPLATE.format(
        width=total_width,
        label_width=label_width,
        value_width=value_width,
        label=label,
        value=value_str,
        color=color,
        label_x=int(label_x),
        value_x=int(value_x)
    )


def parse_coverage_from_html(html_path):
    """Parse coverage data from gcovr HTML output using regex."""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        coverage_data = {
            'lines': None,
            'functions': None,
            'branches': None
        }

        # Find the summary-cards section
        summary_match = re.search(
            r'<div class="summary-cards">(.*?)</div>\s*</div>\s*</div>\s*</div>',
            content,
            re.DOTALL
        )

        if not summary_match:
            # Try alternative: find all summary-card blocks
            summary_match = re.search(
                r'<div class="summary-cards">(.*?)<div class="legend">',
                content,
                re.DOTALL
            )

        if summary_match:
            summary_html = summary_match.group(1)

            # Find each summary-card and extract type + percentage
            card_pattern = re.compile(
                r'<div class="summary-card">\s*'
                r'<div class="summary-card-header">\s*<h3>(\w+)</h3>\s*</div>\s*'
                r'<div class="summary-card-body">.*?'
                r'<span class="ring-text">([^<]+)</span>',
                re.DOTALL
            )

            for match in card_pattern.finditer(summary_html):
                stat_type = match.group(1).lower()
                percentage_text = match.group(2).strip()

                # Extract numeric percentage (skip "-%" which means no data)
                pct_match = re.search(r'([\d.]+)\s*%', percentage_text)
                if pct_match:
                    percentage = float(pct_match.group(1))
                    if stat_type == 'lines':
                        coverage_data['lines'] = percentage
                    elif stat_type == 'functions':
                        coverage_data['functions'] = percentage
                    elif stat_type == 'branches':
                        coverage_data['branches'] = percentage

        return coverage_data
    except Exception as e:
        print(f"Error parsing HTML: {e}", file=sys.stderr)
        return None


def parse_coverage_from_json(json_path):
    """Parse coverage data from gcovr JSON summary output."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # gcovr JSON summary format
        root = data.get('root', data)

        coverage_data = {
            'lines': None,
            'functions': None,
            'branches': None
        }

        if 'line_percent' in root:
            coverage_data['lines'] = root['line_percent']
        elif 'lines_percent' in root:
            coverage_data['lines'] = root['lines_percent']

        if 'function_percent' in root:
            coverage_data['functions'] = root['function_percent']
        elif 'functions_percent' in root:
            coverage_data['functions'] = root['functions_percent']

        if 'branch_percent' in root:
            coverage_data['branches'] = root['branch_percent']
        elif 'branches_percent' in root:
            coverage_data['branches'] = root['branches_percent']

        return coverage_data
    except Exception as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        return None


def generate_badges(output_dir, coverage_data):
    """Generate badge SVG files in the output directory."""
    badges_dir = Path(output_dir) / 'badges'
    badges_dir.mkdir(exist_ok=True)

    badge_configs = [
        ('coverage-lines.svg', 'coverage', coverage_data.get('lines')),
        ('coverage-functions.svg', 'functions', coverage_data.get('functions')),
        ('coverage-branches.svg', 'branches', coverage_data.get('branches')),
    ]

    generated = []
    for filename, label, value in badge_configs:
        if value is not None:
            svg = generate_badge_svg(label, value)
            badge_path = badges_dir / filename
            with open(badge_path, 'w', encoding='utf-8') as f:
                f.write(svg)
            generated.append(filename)
            print(f"Generated {badge_path} ({label}: {value:.1f}%)")
        else:
            print(f"Skipping {filename}: no data available")

    # Also write a JSON summary for potential dynamic badge use
    summary_path = badges_dir / 'coverage.json'
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump({
            'lines': coverage_data.get('lines'),
            'functions': coverage_data.get('functions'),
            'branches': coverage_data.get('branches')
        }, f, indent=2)
    print(f"Generated {summary_path}")

    return generated


def main():
    if len(sys.argv) < 2:
        print("Usage: generate_badges.py <gcovr_output_dir> [--json <summary.json>]", file=sys.stderr)
        print("  Parses index.html or JSON summary to generate coverage badges.", file=sys.stderr)
        sys.exit(1)

    output_dir = sys.argv[1]
    json_path = None

    # Check for --json argument
    if '--json' in sys.argv:
        json_idx = sys.argv.index('--json')
        if json_idx + 1 < len(sys.argv):
            json_path = sys.argv[json_idx + 1]

    if not os.path.isdir(output_dir):
        print(f"Error: {output_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    coverage_data = None

    # Try JSON first if specified
    if json_path and os.path.isfile(json_path):
        print(f"Parsing coverage from JSON: {json_path}")
        coverage_data = parse_coverage_from_json(json_path)

    # Fall back to HTML parsing
    if not coverage_data or all(v is None for v in coverage_data.values()):
        html_path = os.path.join(output_dir, 'index.html')
        if os.path.isfile(html_path):
            print(f"Parsing coverage from HTML: {html_path}")
            coverage_data = parse_coverage_from_html(html_path)

    if not coverage_data or all(v is None for v in coverage_data.values()):
        print("Error: Could not extract coverage data", file=sys.stderr)
        sys.exit(1)

    print(f"Coverage data: lines={coverage_data.get('lines')}, "
          f"functions={coverage_data.get('functions')}, "
          f"branches={coverage_data.get('branches')}")

    generated = generate_badges(output_dir, coverage_data)
    print(f"Successfully generated {len(generated)} badges in {output_dir}/badges/")


if __name__ == '__main__':
    main()
