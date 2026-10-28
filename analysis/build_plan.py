"""Swing / position-level trade plan for the long/short book.

    python3 fetch_data.py CACHE_DIR      # downloads daily bars first
    python3 build_plan.py CACHE_DIR

Daily bars only (no intraday or opening-range logic). Per position:
20/50-day MA, 14-day ATR (Wilder), latest swing high / low (5-bar pivots),
a structural stop, a target, the R-multiple of the open move and a status.
Writes charts/<TICKER>.png, trade_plan.csv and summary.md next to this file.
Analysis only: nothing here places or sizes an order.
"""
import csv
import datetime as dt
import json
import os
import sys
import time
import urllib.request

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.ticker  # noqa: E402,F401
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PIVOT = 5          # bars each side for a confirmed swing point
BUFFER = 0.25      # ATRs beyond the structural level for the stop
ATR_STOP = 1.5     # entry -/+ 1.5 ATR risk stop
NEAR = 0.5         # ATRs: "near stop" / "near target"
CHART_BARS = 126   # ~6 months of daily bars
GDR = {"HY9H GR": "HY9H.F"}  # GDR quoted line, for converting levels back to the entry's currency

COLORS = {"LONG": "#1a7f37", "SHORT": "#cf222e"}


def load(cache, sym):
    res = json.load(open(os.path.join(cache, sym + ".json")))["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    bars = [(dt.datetime.fromtimestamp(t, dt.UTC).date(), o, h, l, c)
            for t, o, h, l, c in zip(res["timestamp"], q["open"], q["high"], q["low"], q["close"])
            if None not in (o, h, l, c)]
    meta = res["meta"]
    return bars, meta.get("currency"), meta.get("longName") or meta.get("shortName") or sym


def sma(xs, n):
    return [None if i + 1 < n else sum(xs[i + 1 - n:i + 1]) / n for i in range(len(xs))]


def atr(highs, lows, closes, n=14):
    tr = [highs[0] - lows[0]] + [max(h - l, abs(h - pc), abs(l - pc))
                                 for h, l, pc in zip(highs[1:], lows[1:], closes[:-1])]
    a = sum(tr[:n]) / n
    for x in tr[n:]:
        a = (a * (n - 1) + x) / n
    return a


def pivots(xs, kind):
    """Indices of confirmed pivot highs / lows (k bars lower / higher on each side)."""
    k, out = PIVOT, []
    for i in range(k, len(xs) - k):
        win = xs[i - k:i + k + 1]
        if (kind == "high" and xs[i] == max(win)) or (kind == "low" and xs[i] == min(win)):
            out.append(i)
    return out


def plan(side, entry, bars):
    closes = [b[4] for b in bars]
    highs = [b[2] for b in bars]
    lows = [b[3] for b in bars]
    cur = closes[-1]
    ma20, ma50 = sma(closes, 20)[-1], sma(closes, 50)[-1]
    a = atr(highs, lows, closes)
    ph, pl = pivots(highs, "high"), pivots(lows, "low")
    swing_hi = highs[ph[-1]] if ph else max(highs[-60:])
    swing_lo = lows[pl[-1]] if pl else min(lows[-60:])
    long = side == "LONG"

    # Stop: tightest of the structural level (latest swing low / 20DMA, beyond a
    # 0.25 ATR buffer, on the right side of price) and entry -/+ 1.5 ATR.
    if long:
        struct = [x - BUFFER * a for x in (swing_lo, ma20) if x is not None and x - BUFFER * a < cur]
        atr_stop = entry - ATR_STOP * a
        stop = max(struct + [atr_stop])
        basis = "atr" if stop == atr_stop else ("swing" if stop == swing_lo - BUFFER * a else "ma20")
    else:
        struct = [x + BUFFER * a for x in (swing_hi, ma20) if x is not None and x + BUFFER * a > cur]
        atr_stop = entry + ATR_STOP * a
        stop = min(struct + [atr_stop])
        basis = "atr" if stop == atr_stop else ("swing" if stop == swing_hi + BUFFER * a else "ma20")

    # R = entry-to-stop distance while the stop is on the risk side of entry by at
    # least 0.5 ATR; once it has trailed to break-even or past it, R is the 1.5 ATR
    # risk unit (a stop just under entry would otherwise make R tiny).
    risk = (entry - stop) if long else (stop - entry)
    R = risk if risk >= NEAR * a else ATR_STOP * a
    sign = 1 if long else -1
    r_mult = sign * (cur - entry) / R

    # Target: nearest prior swing high (low) beyond both entry and price, else entry +/- 2R.
    if long:
        above = sorted(highs[i] for i in ph if highs[i] > max(entry, cur))
        target, tbasis = (above[0], "swing") if above else (entry + 2 * R, "2R")
    else:
        below = sorted((lows[i] for i in pl if lows[i] < min(entry, cur)), reverse=True)
        target, tbasis = (below[0], "swing") if below else (entry - 2 * R, "2R")
    beyond_target = (cur >= target) if long else (cur <= target)
    if beyond_target:  # no swing level left beyond price and 2R already reached
        tbasis = "2R-hit"

    if (long and cur <= stop) or (not long and cur >= stop):
        status = "past stop - cut or re-justify"
    elif abs(cur - stop) <= NEAR * a:
        status = "near stop"
    elif not beyond_target and abs(target - cur) <= NEAR * a:
        status = "near target"
    elif r_mult >= 1 or beyond_target:
        status = "winner / trail"
    else:
        status = "flat"

    return dict(current=cur, ma20=ma20, ma50=ma50, atr14=a, swing_hi=swing_hi, swing_lo=swing_lo,
                stop=stop, stop_basis=basis, target=target, target_basis=tbasis, R=R,
                r_multiple=r_mult, status=status, pct_move=(cur / entry - 1) * 100)


def exit_rule(side, p, cur_code, fmt):
    s, t = fmt(p["stop"]), fmt(p["target"])
    basis = {"atr": "entry %s 1.5 ATR" % ("-" if side == "LONG" else "+"),
             "swing": "beyond the latest swing %s" % ("low" if side == "LONG" else "high"),
             "ma20": "beyond the 20-day MA"}[p["stop_basis"]]
    word = "below" if side == "LONG" else "above"
    if p["status"].startswith("past stop"):
        return (f"Daily close is already {word} the {s} {cur_code} stop ({basis}): cut, or re-justify "
                f"with a new thesis and a fresh structural stop.")
    tgt = ("prior swing %s" % ("high" if side == "LONG" else "low")) if p["target_basis"] == "swing" else "2R"
    if p["target_basis"] == "2R-hit":
        return (f"2R target {t} already reached, no prior swing level left beyond price: manage by the "
                f"trailing stop only. Exit on a daily close {word} {s} {cur_code} ({basis}).")
    trail = ("max(20DMA, latest higher low) - 0.25 ATR" if side == "LONG"
             else "min(20DMA, latest lower high) + 0.25 ATR")
    return (f"Exit on a daily close {word} {s} {cur_code} ({basis}). Target {t} ({tgt}): trim there. "
            f"Trail the stop to {trail} as the trade works; never loosen it.")


def chart(path, title, bars, side, entry, p, ccy):
    closes = [b[4] for b in bars]
    ma20, ma50 = sma(closes, 20), sma(closes, 50)
    d = [b[0] for b in bars][-CHART_BARS:]
    col = COLORS[side]
    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=110)
    ax.plot(d, closes[-CHART_BARS:], color="#24292f", lw=1.4, label="Close")
    ax.plot(d, ma20[-CHART_BARS:], color="#0969da", lw=1, label="20-day MA")
    ax.plot(d, ma50[-CHART_BARS:], color="#8250df", lw=1, label="50-day MA")
    dec = 4 if abs(entry) < 2 else (0 if abs(entry) >= 10000 else 2)
    for y, name, style in ((entry, "Entry", "-"), (p["stop"], "Stop", "--"), (p["target"], "Target", ":")):
        ax.axhline(y, color=col, ls=style, lw=1.3, alpha=0.9, label=f"{name} {y:,.{dec}f}")
    ax.set_title(title, fontsize=11, color=col, loc="left")
    ax.set_ylabel(ccy or "")
    ax.grid(alpha=0.25)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.{min(dec, 2)}f}"))
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def fx_to_usd(cache, ccys):
    rates = {"USD": 1.0}
    for c in sorted(ccys - {"USD", None}):
        path = os.path.join(cache, f"FX_{c}USD.json")
        if not os.path.exists(path):
            url = f"https://query2.finance.yahoo.com/v8/finance/chart/{c}USD=X?range=5d&interval=1d"
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}),
                                        timeout=30) as r:
                json.dump(json.load(r), open(path, "w"))
            time.sleep(0.3)
        res = json.load(open(path))["chart"]["result"][0]
        rates[c] = [x for x in res["indicators"]["quote"][0]["close"] if x][-1]
    return rates


def main():
    cache = sys.argv[1]
    resolved = json.load(open(os.path.join(cache, "resolved.json")))
    os.makedirs(os.path.join(HERE, "charts"), exist_ok=True)
    rows = []
    for pos in csv.DictReader(open(os.path.join(HERE, "positions.csv"))):
        bbg, side = pos["bbg_ticker"], pos["side"]
        shares, entry = float(pos["shares"]), float(pos["entry"])
        sym = resolved[bbg]["symbol"]
        row = dict(ticker=bbg, side=side, shares=int(shares), entry=entry, data_symbol=sym or "")
        if not sym:
            row.update(name=bbg, data_ok=False, status="no market data", currency="",
                       exit_rule=f"No market data ({resolved[bbg]['reason']}). Carried at entry; "
                                 "set a manual stop / target off the broker or private-market mark.")
            rows.append(row)
            continue
        bars, ccy, name = load(cache, sym)
        factor = 1.0
        if bbg in GDR:  # levels from the local line, re-expressed in the GDR's currency
            gbars, gccy, _ = load(cache, GDR[bbg])
            factor = gbars[-1][4] / bars[-1][4]
            ccy, name = gccy, name + " (GDR)"
        p = plan(side, entry / factor, bars)
        conv = {k: (v * factor if k in ("current", "ma20", "ma50", "atr14", "stop", "target",
                                        "swing_hi", "swing_lo", "R") else v) for k, v in p.items()}
        dec = 4 if conv["current"] < 2 else 2
        fmt = lambda x: f"{x:,.{dec}f}"  # noqa: E731
        row.update(name=name, currency=ccy, data_ok=True, as_of=str(bars[-1][0]),
                   exit_rule=exit_rule(side, conv, ccy, fmt), **conv)
        fname = bbg.replace(" ", "_") + ".png"
        chart(os.path.join(HERE, "charts", fname), f"{name} ({bbg}) — {side} — {p['status']}",
              bars, side, entry / factor, p, ccy if factor == 1 else f"KRW ({sym}); entry converted from {ccy}")
        rows.append(row)

    rates = fx_to_usd(cache, {r.get("currency") or None for r in rows})
    write_csv(rows)
    write_summary(rows, rates)


COLS = ["ticker", "name", "side", "shares", "entry", "current", "pct_move", "ma20", "ma50", "atr14",
        "stop", "target", "r_multiple", "status", "exit_rule", "data_ok", "currency", "data_symbol"]


def write_csv(rows):
    with open(os.path.join(HERE, "trade_plan.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(COLS)
        for r in rows:
            out = []
            for c in COLS:
                v = r.get(c, "")
                if isinstance(v, float) and c not in ("shares",):
                    v = round(v, 2) if c in ("pct_move", "r_multiple") else (
                        round(v, 4) if abs(v) < 2 else round(v, 2))
                out.append(v)
            w.writerow(out)


def write_summary(rows, rates):
    for r in rows:
        fx = rates.get(r.get("currency") or "USD", 1.0)
        px = r.get("current", r["entry"])
        sign = 1 if r["side"] == "LONG" else -1
        r["mv_usd"] = sign * r["shares"] * px * fx if r["data_ok"] else sign * r["shares"] * r["entry"] * fx
        r["pnl_usd"] = sign * r["shares"] * (px - r["entry"]) * fx if r["data_ok"] else 0.0
        r["ret"] = sign * r["pct_move"] if r["data_ok"] else None  # return to the position, short-adjusted

    # A no-data position has no currency from the feed; value it at entry in USD
    # only when it is US-listed (SPCX). Others are reported but left out of exposure.
    def in_exposure(r):
        return r["data_ok"] or " " not in r["ticker"]

    longs = [r for r in rows if r["side"] == "LONG"]
    shorts = [r for r in rows if r["side"] == "SHORT"]
    lv = sum(r["mv_usd"] for r in longs if in_exposure(r))
    sv = sum(r["mv_usd"] for r in shorts if in_exposure(r))
    excluded = [r["ticker"] for r in rows if not in_exposure(r)]
    pnl = sum(r["pnl_usd"] for r in rows)

    def avg(xs):
        xs = [x for x in xs if x is not None]
        return sum(xs) / len(xs) if xs else float("nan")

    def side_line(name, rs):
        ok = [r for r in rs if r["data_ok"]]
        wins = sum(1 for r in ok if r["ret"] > 0)
        return (f"| {name} | {len(rs)} | {len(ok)} | {avg(r['ret'] for r in ok):+.1f}% | "
                f"{wins} / {len(ok) - wins} | ${sum(r['pnl_usd'] for r in rs) / 1e6:+,.2f}m |")

    ok = sorted((r for r in rows if r["data_ok"]), key=lambda r: r["ret"])
    as_of = max(r["as_of"] for r in ok)
    status_counts = {}
    for r in rows:
        status_counts[r["status"]] = status_counts.get(r["status"], 0) + 1

    def tbl(rs):
        out = ["| Ticker | Name | Side | Return | R | P&L (USD) | Status |", "|---|---|---|---|---|---|---|"]
        for r in rs:
            out.append(f"| {r['ticker']} | {r['name']} | {r['side']} | {r['ret']:+.1f}% | {r['r_multiple']:+.1f} "
                       f"| ${r['pnl_usd'] / 1e6:+,.2f}m | {r['status']} |")
        return "\n".join(out)

    past = sorted((r for r in rows if r["status"].startswith("past stop")), key=lambda r: r["pnl_usd"])
    near = [r for r in rows if r["status"] == "near stop"]
    md = [
        "# Book review: swing / position trade plan",
        "",
        f"Data as of the last daily bar ({as_of}), free Yahoo daily OHLC (~1 year), local currency per "
        "position. Analysis only: paper, nothing sized, placed or executed. Not investment advice.",
        "",
        "## Exposure (USD, converted at today's FX)",
        "",
        "| | USD |",
        "|---|---|",
        f"| Long market value | ${lv / 1e6:,.1f}m |",
        f"| Short market value | ${-sv / 1e6:,.1f}m |",
        f"| Gross exposure | ${(lv - sv) / 1e6:,.1f}m |",
        f"| Net exposure | ${(lv + sv) / 1e6:+,.1f}m ({(lv + sv) / (lv - sv) * 100:+.0f}% of gross) |",
        f"| Unrealized P&L vs entry | ${pnl / 1e6:+,.1f}m |",
        "",
        "P&L is price-only: local-currency move x shares, converted at today's FX (no FX P&L, "
        "no fees, borrow or dividends). No-data positions are carried at entry with zero P&L"
        + (f"; {', '.join(excluded)} has no currency from the feed and is left out of exposure." if excluded else "."),
        "",
        "## Longs vs shorts",
        "",
        "Return is to the position (a short that fell shows a positive return).",
        "",
        "| Side | Positions | With data | Avg return | Winners / losers | P&L (USD) |",
        "|---|---|---|---|---|---|",
        side_line("Long", longs),
        side_line("Short", shorts),
        "",
        "## Status vs plan",
        "",
        "| Status | Positions |",
        "|---|---|",
        *[f"| {k} | {v} |" for k, v in sorted(status_counts.items(), key=lambda kv: -kv[1])],
        "",
        "## Biggest winners (by return)",
        "",
        tbl(list(reversed(ok[-8:]))),
        "",
        "## Biggest losers (by return)",
        "",
        tbl(ok[:8]),
        "",
        "## Biggest by USD P&L",
        "",
        tbl(sorted(ok, key=lambda r: -r["pnl_usd"])[:5] + sorted(ok, key=lambda r: r["pnl_usd"])[:5]),
        "",
        f"## Priority review: past stop ({len(past)})",
        "",
        "Price has already closed through the plan's stop. Cut, or re-justify with a new thesis and a "
        "fresh structural stop. Sorted by USD loss.",
        "",
        tbl(past),
        "",
        f"## Near stop ({len(near)})",
        "",
        (tbl(near) if near else "None."),
        "",
        "## No market data",
        "",
        *[f"- **{r['ticker']}**: {r['exit_rule']}" for r in rows if not r["data_ok"]],
        "",
        "## Method",
        "",
        "- Daily bars only; no intraday or opening-range logic. 20/50-day simple MAs, 14-day ATR "
        "(Wilder), swing points = 5-bar pivots (a high / low with 5 lower / higher bars each side).",
        "- **Stop (long):** the tighter of (a) the higher of the latest swing low and the 20-day MA, "
        "minus 0.25 ATR, taken only if it is still below price, and (b) entry - 1.5 ATR. Shorts mirror "
        "it above. A winner's stop therefore trails above entry; a loser more than 1.5 ATR through "
        "entry is past stop.",
        "- **R:** entry-to-stop distance while the stop is at least 0.5 ATR on the risk side of entry; "
        "once it has trailed to break-even or through entry, R is the 1.5 ATR risk unit. "
        "R-multiple = open move / R.",
        "- **Target (long):** nearest prior swing high above both entry and price, else entry + 2R "
        "(shorts: nearest prior swing low below both, else entry - 2R). When price is already through "
        "2R with no swing level left beyond it, the 2R level stays on the chart as reached and the "
        "position is managed by its trailing stop.",
        "- **Stops are evaluated as of today.** Entry dates are not in the book, so the stop is today's "
        "structure and today's ATR, not the stop that applied on the day each position was opened.",
        "- **Status** (first that applies): past stop; near stop (within 0.5 ATR); near target "
        "(within 0.5 ATR); winner / trail (R >= 1 or through target); flat.",
        "- **Ticker mapping:** Bloomberg suffix -> Yahoo suffix; 3081 TT trades on TPEx (3081.TWO); "
        "PNG CN on the TSX-V; MAXQ CN on Cboe Canada (.NE); Swedish B shares use a dash "
        "(KEBNI-B.ST, SECT-B.ST). HY9H GR: levels are computed on SK Hynix's Korean line 000660.KS and "
        "converted to the GDR's EUR price (HY9H.F) at the latest close ratio, so entry, current, stop "
        "and target are all in EUR; its chart is in KRW with the entry converted the same way.",
        "",
        "Per-position detail: `trade_plan.csv`; charts: `charts/<TICKER>.png`.",
        "",
    ]
    open(os.path.join(HERE, "summary.md"), "w").write("\n".join(md))


if __name__ == "__main__":
    main()
