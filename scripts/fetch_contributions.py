"""
fetch_contributions.py — Scrape public GitHub contributions.
No API token needed. Uses the public HTML endpoint.
"""
import os
import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path

USERNAME = "alokgorithm"
URL = f"https://github.com/users/{USERNAME}/contributions"

def fetch_contributions():
    root = Path(__file__).resolve().parent.parent
    out_file = root / "data" / "contributions.json"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml"
    }
    print(f"Fetching {URL}...")
    response = requests.get(URL, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find contribution cells (td elements with data-date and data-level)
    days = soup.find_all(lambda tag: tag.has_attr('data-date') and tag.has_attr('data-level'))

    if not days:
        print("Could not find contribution cells. HTML snippet:")
        print(response.text[:1000])
        return

    parsed_days = []
    for day in days:
        date_str = day.get('data-date')
        if not date_str:
            continue
        level = int(day.get('data-level', 0))

        # Try to extract count from tooltip or sr-only span
        count = 0
        tooltip_id = day.get('id')
        tooltip = soup.find('tool-tip', {'for': tooltip_id}) if tooltip_id else None

        if tooltip:
            text = tooltip.text.strip().split()[0]
            count = int(text) if text.isdigit() else 0
        else:
            text_span = day.find('span', class_='sr-only')
            if text_span:
                text = text_span.text.strip().split()[0]
                count = int(text) if text.isdigit() else 0

        parsed_days.append({
            'date': date_str,
            'level': level,
            'count': count
        })

    parsed_days.sort(key=lambda x: x['date'])

    # Compute stats
    total = sum(d['count'] for d in parsed_days)
    best_day = max((d['count'] for d in parsed_days), default=0)
    current_streak = 0
    longest_streak = 0
    temp_streak = 0

    for d in parsed_days:
        if d['count'] > 0:
            temp_streak += 1
        else:
            longest_streak = max(longest_streak, temp_streak)
            temp_streak = 0
    current_streak = temp_streak
    longest_streak = max(longest_streak, temp_streak)

    data = {
        'username': USERNAME,
        'total': total,
        'longest_streak': longest_streak,
        'current_streak': current_streak,
        'best_day': best_day,
        'days': parsed_days
    }

    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"Saved {len(parsed_days)} days -> {out_file}")
    print(f"Total: {total}, Longest streak: {longest_streak}, Current: {current_streak}, Best day: {best_day}")

if __name__ == "__main__":
    fetch_contributions()
