# /// script
# requires-python = ">=3.12"
# ///
"""
Collect today's YouTube statistics for the channels in channels-list.csv.

A run appends one row per returned channel to data/stats/YYYY-MM.csv for the current UTC month,
refreshes data/channels.jsonl, and rewrites the table between the stats markers in README.md. It
does nothing when that month's file already holds a run from the current UTC date. On GitHub
Actions, it also sets the step output `missing` to the listed channels that returned no data.
"""

import csv
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from itertools import batched
from pathlib import Path

CHANNEL_LIST = Path("channels-list.csv")
STATS_DIR = Path("data/stats")
CHANNELS = Path("data/channels.jsonl")
README = Path("README.md")
STATS_FIELDS = ["retrieved_at", "channel_id", "title", "views", "subscribers", "videos"]
TABLE_START = "<!-- stats:start -->"
TABLE_END = "<!-- stats:end -->"
# https://developers.google.com/youtube/v3/docs/channels/list (checked 2026-11-11): a call costs
# one quota unit and takes a comma-separated list of channel ids. The page states no limit on that
# list, but a call with more than 50 ids fails.
API_URL = "https://www.googleapis.com/youtube/v3/channels"
IDS_PER_CALL = 50


def fetch(ids: list[str], key: str) -> list[dict]:
    """
    Return the channel resources for ids, or exit on an HTTP error.

    A terminated or deleted channel is absent from the result.
    """
    items = []
    for batch in batched(ids, IDS_PER_CALL):
        query = urllib.parse.urlencode(
            {"part": "snippet,statistics", "id": ",".join(batch), "key": key}
        )
        try:
            with urllib.request.urlopen(f"{API_URL}?{query}", timeout=30) as response:
                items += json.load(response).get("items", [])
        except urllib.error.HTTPError as error:
            sys.exit(f"YouTube Data API returned HTTP {error.code}: {error.read().decode()}")
    return items


def render_table(items: list[dict], retrieved_at: str) -> str:
    """Return a Markdown table of the run, with the most subscribed channel first."""
    lines = [
        f"Latest run: {retrieved_at}, {len(items)} channels.",
        "",
        "| Channel | Subscribers | Views | Videos |",
        "|:---|---:|---:|---:|",
    ]
    by_subscribers = sorted(
        items, key=lambda item: -int(item["statistics"].get("subscriberCount", 0))
    )
    for item in by_subscribers:
        stats = item["statistics"]
        subscribers = stats.get("subscriberCount")
        title = re.sub(r"([\\|\[\]])", r"\\\1", item["snippet"]["title"])
        cells = [
            f"[{title}](https://www.youtube.com/channel/{item['id']})",
            f"{int(subscribers):,}" if subscribers else "hidden",
            f"{int(stats['viewCount']):,}",
            f"{int(stats['videoCount']):,}",
        ]
        lines.append(f"| {' | '.join(cells)} |")
    return "\n".join(lines)


def main() -> None:
    key = os.environ.get("YOUTUBE_DATA_API_V3_KEY")
    if not key:
        sys.exit("Set YOUTUBE_DATA_API_V3_KEY to a YouTube Data API v3 key.")
    readme = README.read_text(encoding="utf-8")
    if not 0 <= readme.find(TABLE_START) < readme.find(TABLE_END):
        sys.exit(f"{README} needs a {TABLE_START} marker followed by a {TABLE_END} marker.")
    retrieved_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    today = retrieved_at[:10]
    stats_file = STATS_DIR / f"{retrieved_at[:7]}.csv"
    month_lines = stats_file.read_text(encoding="utf-8").splitlines() if stats_file.exists() else []
    # Rows are in time order, so the last line holds the latest run.
    if month_lines and month_lines[-1].startswith(today):
        print(f"{stats_file} already holds a run from {today}.")
        return

    with CHANNEL_LIST.open(newline="", encoding="utf-8") as f:
        ids = [row["channel_id"] for row in csv.DictReader(f)]
    items = sorted(fetch(ids, key), key=lambda item: item["id"])
    missing = sorted(set(ids) - {item["id"] for item in items})
    if missing:
        print(f"Listed channels with no data: {', '.join(missing)}", file=sys.stderr)

    STATS_DIR.mkdir(parents=True, exist_ok=True)
    with stats_file.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        if not month_lines:
            writer.writerow(STATS_FIELDS)
        for item in items:
            stats = item["statistics"]
            # https://developers.google.com/youtube/v3/docs/channels (checked 2026-11-11): a
            # channel can hide its subscriber count (hiddenSubscriberCount), and the page does
            # not say whether subscriberCount is then present, so a missing count stays empty.
            writer.writerow(
                [
                    retrieved_at,
                    item["id"],
                    item["snippet"]["title"],
                    stats["viewCount"],
                    stats.get("subscriberCount"),
                    stats["videoCount"],
                ]
            )

    # Upsert by id, so channels the API no longer returns keep their last details.
    channels = {}
    if CHANNELS.exists():
        lines = CHANNELS.read_text(encoding="utf-8").splitlines()
        channels = {channel["channel_id"]: channel for channel in map(json.loads, lines)}
    for item in items:
        snippet = item["snippet"]
        channels[item["id"]] = {
            "channel_id": item["id"],
            "handle": snippet.get("customUrl"),
            "title": snippet["title"],
            "published_at": snippet["publishedAt"],
            "country": snippet.get("country"),
            "description": snippet["description"],
        }
    CHANNELS.write_text(
        "".join(json.dumps(channels[c], ensure_ascii=False) + "\n" for c in sorted(channels)),
        encoding="utf-8",
    )

    before, _, rest = readme.partition(TABLE_START)
    after = rest.partition(TABLE_END)[2]
    table = render_table(items, retrieved_at)
    README.write_text(f"{before}{TABLE_START}\n\n{table}\n\n{TABLE_END}{after}", encoding="utf-8")
    print(f"Saved {len(items)} of {len(ids)} channels at {retrieved_at}.")

    if missing and "GITHUB_OUTPUT" in os.environ:
        missing_channels = [channels.get(c, {"channel_id": c}) for c in missing]
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
            f.write(f"missing={json.dumps(missing_channels, ensure_ascii=False)}\n")


if __name__ == "__main__":
    main()
