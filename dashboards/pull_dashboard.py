#!/usr/bin/env python3
"""Pull the mtik_exporter dashboard from Grafana into dashboards/mtik_exporter.json.

Usage:
    GRAFANA_URL=http://grafana:3000 GRAFANA_TOKEN=glsa_... python3 dashboards/pull_dashboard.py

The token is a Grafana service account token (Viewer role is enough).
The dashboard UID is read from the existing JSON file unless --uid is given.

Instance-specific fields (id, version, and the saved selection of every
template variable) are stripped so that `git diff` shows only real changes
and no local hostnames/addresses end up in the repo.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_FILE = Path(__file__).resolve().parent / "mtik_exporter.json"


def fetch(url, token, uid):
    req = urllib.request.Request(
        f"{url.rstrip('/')}/api/dashboards/uid/{uid}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.load(resp)["dashboard"]
    except urllib.error.HTTPError as e:
        sys.exit(f"Grafana returned HTTP {e.code} for dashboard {uid}: {e.read().decode(errors='replace')}")
    except urllib.error.URLError as e:
        sys.exit(f"Could not reach Grafana at {url}: {e.reason}")


def normalize(dash):
    dash.pop("id", None)
    dash.pop("version", None)
    for var in dash.get("templating", {}).get("list", []):
        # Saved selections are instance-specific (datasource UIDs, router
        # names, scrape target addresses); Grafana picks defaults on load
        var.pop("current", None)
    return dash


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--url", default=os.environ.get("GRAFANA_URL"), help="Grafana base URL (default: $GRAFANA_URL)")
    p.add_argument("--uid", help="dashboard UID (default: read from the output file)")
    p.add_argument("-o", "--output", type=Path, default=DEFAULT_FILE, help=f"output file (default: {DEFAULT_FILE.name})")
    args = p.parse_args()

    token = os.environ.get("GRAFANA_TOKEN")
    if not args.url or not token:
        sys.exit("Set GRAFANA_URL (or --url) and GRAFANA_TOKEN")

    uid = args.uid
    if not uid:
        try:
            uid = json.loads(args.output.read_text(encoding="utf-8"))["uid"]
        except (OSError, ValueError, KeyError):
            sys.exit(f"Could not read a dashboard UID from {args.output}; pass --uid")

    dash = normalize(fetch(args.url, token, uid))
    args.output.write_text(json.dumps(dash, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote '{dash.get('title')}' to {args.output}")


if __name__ == "__main__":
    main()
