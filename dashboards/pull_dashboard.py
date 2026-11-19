#!/usr/bin/env python3
"""Pull the mtik_exporter dashboard from Grafana into dashboards/mtik_exporter.json.

Usage:
    GRAFANA_URL=http://grafana:3000 GRAFANA_TOKEN=glsa_... python3 dashboards/pull_dashboard.py

GRAFANA_URL, GRAFANA_TOKEN and GRAFANA_PUBLIC_UID can also be put in a
.env file in the repo root (gitignored); real environment variables win.

The token is a Grafana service account token (Viewer role is enough for pulling).
The dashboard UID is read from the existing JSON file unless --uid is given.

Instance-specific fields (id, version, and the saved selection of every
template variable) are stripped so that `git diff` shows only real changes
and no local hostnames/addresses end up in the repo.

Public copy (optional): with --public-uid (or $GRAFANA_PUBLIC_UID) the pulled
dashboard is also pushed over an existing "public" dashboard. The public
dashboard keeps its own uid, title, folder and the variables listed in
PUBLIC_KEEP_VARS (e.g. the filtered router list); everything else is
replaced. This needs Editor permission on the public dashboard's folder.
"""

import argparse
import copy
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_FILE = Path(__file__).resolve().parent / "mtik_exporter.json"
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

# Variables taken from the existing public dashboard instead of the private one
PUBLIC_KEEP_VARS = ("node",)


def load_env_file(path):
    """Read KEY=VALUE lines into os.environ; variables already set win."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.removeprefix("export ").split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def api(url, token, path, body=None):
    req = urllib.request.Request(
        f"{url.rstrip('/')}{path}",
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        method="POST" if body is not None else "GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f"Grafana returned HTTP {e.code} for {path}: {e.read().decode(errors='replace')}")
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


def push_public(url, token, private, public_uid):
    existing = api(url, token, f"/api/dashboards/uid/{public_uid}")
    old = existing["dashboard"]
    kept = {v["name"]: v for v in old.get("templating", {}).get("list", []) if v["name"] in PUBLIC_KEEP_VARS}
    missing = set(PUBLIC_KEEP_VARS) - kept.keys()
    if missing:
        sys.exit(f"Public dashboard {public_uid} has no variable(s) {', '.join(sorted(missing))}; not pushing")

    dash = copy.deepcopy(private)
    dash["uid"] = public_uid
    dash["id"] = old["id"]
    dash["title"] = old["title"]
    dash["templating"]["list"] = [kept.get(v["name"], v) for v in dash["templating"]["list"]]

    api(url, token, "/api/dashboards/db", {
        "dashboard": dash,
        "folderUid": existing["meta"].get("folderUid", ""),
        "overwrite": True,
        "message": f"Synced from {private['uid']} by pull_dashboard.py",
    })
    print(f"Pushed public copy to '{old['title']}' ({public_uid})")


def main():
    load_env_file(ENV_FILE)
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--url", default=os.environ.get("GRAFANA_URL"), help="Grafana base URL (default: $GRAFANA_URL)")
    p.add_argument("--uid", help="dashboard UID (default: read from the output file)")
    p.add_argument("--public-uid", default=os.environ.get("GRAFANA_PUBLIC_UID"),
                   help="also push to this public dashboard (default: $GRAFANA_PUBLIC_UID)")
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

    dash = normalize(api(args.url, token, f"/api/dashboards/uid/{uid}")["dashboard"])
    args.output.write_text(json.dumps(dash, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote '{dash.get('title')}' to {args.output}")

    if args.public_uid:
        push_public(args.url, token, dash, args.public_uid)


if __name__ == "__main__":
    main()
