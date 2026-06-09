#!/usr/bin/env python3
"""Load, filter, and strip articles from a saved MCP result file.

Usage: process_articles.py <json_path> <cutoff_timestamp>

Outputs filtered articles as JSON to stdout. Survey info goes to stderr.
"""
import html
import json
import re
import sys
from collections import Counter
from datetime import datetime


def strip_html(s):
    s = re.sub(r"<[^>]+>", "", s or "")
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


json_path, cutoff_ts = sys.argv[1], int(sys.argv[2])

with open(json_path) as f:
    data = json.load(f)
all_articles = data["result"]

filtered = [a for a in all_articles if a.get("published", 0) >= cutoff_ts]

for a in filtered:
    a["summary"] = strip_html(a.get("summary", ""))

counts = Counter(a["feed_name"] for a in filtered)
if filtered:
    dates = [a["published"] for a in filtered]
    date_range = (
        f"{datetime.fromtimestamp(min(dates)).date()} – "
        f"{datetime.fromtimestamp(max(dates)).date()}"
    )
else:
    date_range = "no articles"

print(f"articles: {len(filtered)} (filtered from {len(all_articles)})", file=sys.stderr)
print(f"date range: {date_range}", file=sys.stderr)
for feed, count in counts.most_common(10):
    print(f"  {count:3d}  {feed}", file=sys.stderr)

json.dump(filtered, sys.stdout)
