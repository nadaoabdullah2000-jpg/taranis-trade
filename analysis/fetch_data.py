"""Resolve Bloomberg tickers to Yahoo symbols and download ~1 year of daily bars.

    python3 fetch_data.py CACHE_DIR

Reads positions.csv next to this file. Writes CACHE_DIR/<yahoo symbol>.json
(the raw Yahoo v8 chart response) and resolved.json (bbg ticker -> symbol or
the reason it has no data). Free, unofficial Yahoo endpoints; nothing invented.
"""
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "Mozilla/5.0 (taranis-trade analysis)"}

# Instruments known to have no public market data.
NO_DATA = {"SPCX": "private company (SpaceX), no listed market data"}
OVERRIDE = {"HY9H GR": ["000660.KS"]}  # SK Hynix GDR -> Korean line

SUFFIX = {
    "PW": [".WA"], "JP": [".T"], "GY": [".DE"], "GR": [".DE"], "FP": [".PA"],
    "NA": [".AS"], "TT": [".TW", ".TWO"], "KS": [".KS", ".KQ"], "KQ": [".KQ", ".KS"],
    "CN": [".TO", ".V", ".CN", ".NE"], "CP": [".PR"], "AU": [".AX"], "IM": [".MI"],
    "SM": [".MC"], "SS": [".ST"], "SE": [".ST"],
}


def candidates(bbg):
    if bbg in OVERRIDE:
        return OVERRIDE[bbg]
    parts = bbg.split()
    if len(parts) == 1:
        return [parts[0]]
    code, exch = parts
    if exch == "HK":
        return [code.zfill(4) + ".HK"]
    out = []
    for sfx in SUFFIX.get(exch, []):
        out.append(code + sfx)
        if exch in ("SS", "SE") and code[-1] in "AB" and len(code) > 3:
            out.append(code[:-1] + "-" + code[-1] + sfx)  # KEBNIB -> KEBNI-B.ST
    return out


def fetch(symbol):
    for host in ("query2", "query1"):
        url = (f"https://{host}.finance.yahoo.com/v8/finance/chart/"
               f"{urllib.request.quote(symbol)}?range=1y&interval=1d&includePrePost=false")
        for attempt in range(2):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                    return json.load(r)
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return None
                if e.code == 429 and attempt == 0:
                    time.sleep(5)
                    continue
                break
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
                break
    return None


def usable(doc):
    try:
        res = doc["chart"]["result"][0]
        closes = [c for c in res["indicators"]["quote"][0]["close"] if c is not None]
    except (TypeError, KeyError, IndexError):
        return 0
    return len(closes)


def main():
    cache = sys.argv[1]
    os.makedirs(cache, exist_ok=True)
    resolved = {}
    with open(os.path.join(HERE, "positions.csv")) as fh:
        tickers = [r["bbg_ticker"] for r in csv.DictReader(fh)]
    for bbg in tickers:
        if bbg in NO_DATA:
            resolved[bbg] = {"symbol": None, "reason": NO_DATA[bbg], "tried": []}
            continue
        tried, hit = [], None
        for sym in candidates(bbg):
            tried.append(sym)
            path = os.path.join(cache, sym + ".json")
            doc = json.load(open(path)) if os.path.exists(path) else fetch(sym)
            time.sleep(0.3)
            n = usable(doc) if doc else 0
            if n:
                json.dump(doc, open(path, "w"))
            if n >= 60:
                hit = sym
                break
        resolved[bbg] = {"symbol": hit, "tried": tried,
                         "reason": None if hit else "no usable Yahoo daily data for " + ", ".join(tried)}
        print(f"{bbg:12} -> {hit or 'NO DATA'}  (tried {', '.join(tried)})", flush=True)
    json.dump(resolved, open(os.path.join(cache, "resolved.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
