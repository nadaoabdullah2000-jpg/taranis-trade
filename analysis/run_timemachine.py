"""Time Machine odds for every position in trade_plan.csv, on daily bars.

    python3 fetch_data.py CACHE_DIR        # the same daily bars build_plan.py used
    python3 run_timemachine.py CACHE_DIR

The engine is the installed trader-timemachine skill: its simulate() (random
draws, stop checked before target inside every bar, R maths) and its verdict
thresholds. timemachine.py itself has no multi-day mode (its CLI replays one
session of 5-minute bars), so this feeds simulate() a pool of each ticker's own
daily bars and walks HORIZON trading days. Stops and targets come from
trade_plan.csv unchanged. Writes timemachine.csv, timemachine.md and
timemachine/<TICKER>.json next to this file. Analysis only, nothing is placed.
"""
import csv
import importlib.util
import json
import os
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ENGINE = os.path.join(ROOT, ".claude", "skills", "trader-timemachine", "timemachine.py")

HORIZON = 20       # trading days (~4 weeks) per replay
LOOKBACK = 250     # daily bars in the pool (fewer when the listing is younger)
REPLAYS = 10000
LOCAL_LINE = {"HY9H GR": "000660.KS"}  # GDR levels, returns from the Korean line

spec = importlib.util.spec_from_file_location("timemachine", ENGINE)
tm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tm)


def daily_bars(cache, sym):
    res = json.load(open(os.path.join(cache, sym + ".json")))["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    return [(o, h, l, c) for o, h, l, c in zip(q["open"], q["high"], q["low"], q["close"])
            if None not in (o, h, l, c)]


def seed_for(ticker):
    return zlib.crc32(ticker.encode()) % 100000


def history(bars, start_px, stop, target, long):
    """The same stop / target distances (as % of price) from every past close, walked HORIZON days."""
    s_mult, t_mult = stop / start_px, target / start_px
    out = {"fires": 0, "target": 0, "stop": 0, "neither": 0}
    for t in range(len(bars) - HORIZON):
        base = bars[t][3]
        st, tg = base * s_mult, base * t_mult
        res = "neither"
        for o, h, l, c in bars[t + 1:t + 1 + HORIZON]:
            if (long and l <= st) or (not long and h >= st):
                res = "stop"
                break
            if (long and h >= tg) or (not long and l <= tg):
                res = "target"
                break
        out["fires"] += 1
        out[res] += 1
    return out


def tag(mc):
    lv = tm.lean(mc)
    if lv is None or abs(lv[0]) < tm.COIN_FLIP:
        return "coin-flip"
    return "favorable" if lv[0] > 0 else "unfavorable"


def main():
    cache = sys.argv[1]
    plan_path = os.path.join(HERE, "trade_plan.csv")
    if not os.path.exists(plan_path):
        sys.exit("analysis/trade_plan.csv is missing: run the trade-plan step (build_plan.py) first.")
    os.makedirs(os.path.join(HERE, "timemachine"), exist_ok=True)
    rows = []
    for p in csv.DictReader(open(plan_path)):
        if p["data_ok"] != "True":
            continue
        side, long = p["side"], p["side"] == "LONG"
        entry, cur = float(p["entry"]), float(p["current"])
        stop, target = float(p["stop"]), float(p["target"])
        sym = LOCAL_LINE.get(p["ticker"], p["data_symbol"])
        bars = daily_bars(cache, sym)[-LOOKBACK:]
        seed = seed_for(p["ticker"])
        row = dict(ticker=p["ticker"], name=p["name"], side=side, entry=entry, current=cur, stop=stop,
                   target=target, seed=seed, lookback_days=len(bars), plan_status=p["status"],
                   currency=p["currency"])
        past_stop = (cur <= stop) if long else (cur >= stop)
        past_target = (cur >= target) if long else (cur <= target)
        doc = {"ticker": p["ticker"], "data_symbol": sym, "plan": {k: row[k] for k in (
            "side", "entry", "current", "stop", "target", "currency")},
            "horizon_days": HORIZON, "lookback_days": len(bars), "seed": seed}
        if past_stop or past_target:
            # The level is already behind the price: there is nothing left to replay.
            row.update(sim_target_first_pct="", sim_stop_first_pct="", sim_neither_pct="", avg_result_R="",
                       median_end_price="", hist_fires="", hist_target="", hist_stop="", hist_neither="",
                       verdict="unfavorable" if past_stop else "favorable",
                       note="already through the stop" if past_stop else "target already reached")
            doc["result"] = row["note"]
        else:
            # Every slot of the engine's pool holds the same daily bars; window 0 = draw from all of them.
            ratios = [(o / pc, h / pc, l / pc, c / pc) for (_, _, _, pc), (o, h, l, c) in zip(bars, bars[1:])]
            pool = [ratios] * (HORIZON + 1)
            mc = tm.simulate(pool, cur, stop, target, 0, HORIZON, REPLAYS, seed, 0,
                             "buy" if long else "sell")
            hist = history(bars, cur, stop, target, long)
            row.update(sim_target_first_pct=round(100 * mc["p_target"], 1),
                       sim_stop_first_pct=round(100 * mc["p_stop"], 1),
                       sim_neither_pct=round(100 * mc["p_neither"], 1), avg_result_R=mc["avg_R"],
                       median_end_price=mc["median_close"], hist_fires=hist["fires"],
                       hist_target=hist["target"], hist_stop=hist["stop"], hist_neither=hist["neither"],
                       verdict=tag(mc), note="", r_at_target=mc["r_at_target"])
            mc.pop("sample_paths", None)
            doc.update(simulation=mc, history=hist, verdict=row["verdict"], verdict_line=tm.verdict(mc),
                       verdict_notes=tm.verdict_notes(mc))
        json.dump(doc, open(os.path.join(HERE, "timemachine", p["ticker"].replace(" ", "_") + ".json"), "w"),
                  indent=1)
        rows.append(row)
        print(f"{p['ticker']:11} {row['verdict']:11} {row['sim_target_first_pct']!s:>5} / "
              f"{row['sim_stop_first_pct']!s:>5}  {row['note']}", flush=True)
    write_csv(rows)
    write_md(rows)


COLS = ["ticker", "name", "side", "entry", "stop", "target", "seed", "lookback_days",
        "sim_target_first_pct", "sim_stop_first_pct", "sim_neither_pct", "avg_result_R",
        "median_end_price", "hist_fires", "hist_target", "hist_stop", "hist_neither", "verdict"]


def write_csv(rows):
    with open(os.path.join(HERE, "timemachine.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def write_md(rows):
    sim = [r for r in rows if r["note"] == ""]

    def table(rs):
        out = ["| # | Ticker | Name | Target first | Stop first | Neither | Avg R | Target R | "
               "History T / S / N | Verdict |", "|---|---|---|---|---|---|---|---|---|---|"]
        for i, r in enumerate(rs, 1):
            out.append(f"| {i} | {r['ticker']} | {r['name']} | {r['sim_target_first_pct']}% | "
                       f"{r['sim_stop_first_pct']}% | {r['sim_neither_pct']}% | {r['avg_result_R']:+.2f} | "
                       f"{r['r_at_target']:.2f} | {r['hist_target']} / {r['hist_stop']} / {r['hist_neither']} | "
                       f"{r['verdict']} |")
        return "\n".join(out)

    def ranked(side):
        return sorted((r for r in sim if r["side"] == side), key=lambda r: -r["sim_target_first_pct"])

    def side_sections(side):
        rs = [r for r in rows if r["side"] == side and r["note"]]
        out = [table(ranked(side))]
        if rs:
            out += ["", "Not replayed (the level is already behind the price): " +
                    "; ".join(f"{r['ticker']} ({r['note']})" for r in rs) + "."]
        return "\n".join(out)

    counts = {v: sum(1 for r in sim if r["verdict"] == v) for v in ("favorable", "coin-flip", "unfavorable")}
    unfav = sorted((r for r in sim if r["verdict"] == "unfavorable"),
                   key=lambda r: r["sim_target_first_pct"] - r["sim_stop_first_pct"])
    much = [r for r in unfav if r["sim_stop_first_pct"] >= 2 * max(r["sim_target_first_pct"], 0.1)]
    past = [r for r in rows if r["plan_status"].startswith("past stop")]
    skipped = len(rows)
    lb = sorted({r["lookback_days"] for r in rows})

    md = [
        "# Time Machine: odds of target before stop, per position",
        "",
        f"{len(sim)} positions replayed, {REPLAYS:,} paths each, {HORIZON} trading days (~4 weeks) "
        "forward from the latest close. Stops and targets are taken unchanged from `trade_plan.csv`. "
        "Simulation, not prediction: it is built from each stock's own recent daily bars and cannot see "
        "an earnings report, a halt or a headline. Treat the odds as a reality check. Analysis only: "
        "paper, nothing placed.",
        "",
        f"Verdicts on the replayed positions: {counts['favorable']} favorable, {counts['coin-flip']} "
        f"coin-flip, {counts['unfavorable']} unfavorable. {skipped - len(sim)} more were not replayed "
        "because the price is already through the stop (or the target): see the review list below.",
        "",
        "**How the verdict reads:** it weighs the odds against the payoff, as the skill does. A target "
        "at 0.2R needs to come first in 83 % of the replays that hit a side just to break even, so 77 % "
        "target-first is still *unfavorable*; a 5R target breaks even at 17 %, so 20 % is a *coin-flip*. "
        "Avg R shows the same thing as a number.",
        "",
        "Columns: **Target first / Stop first / Neither** = share of the 10,000 replays; **Avg R** = "
        "mean result in R, where R is the distance from today's price to the stop (+target R at the "
        "target, -1 at the stop, open move / R otherwise); **Target R** = target distance / stop "
        "distance from today's price; **History T / S / N** = past rolling 20-day windows that hit "
        "target first / stop first / neither with the same % distances.",
        "",
        "## Longs (ranked by target-first odds)",
        "",
        side_sections("LONG"),
        "",
        "## Shorts (ranked by target-first odds)",
        "",
        "For a short, target first = the price falls to the target before it rises to the stop.",
        "",
        side_sections("SHORT"),
        "",
        "## Flag (a): unfavorable odds",
        "",
        f"{len(unfav)} replayed positions lean toward the stop. Stop first at least twice as likely as "
        f"target first ({len(much)}): " + (", ".join(
            f"**{r['ticker']}** {r['side'].lower()} ({r['sim_target_first_pct']}% vs "
            f"{r['sim_stop_first_pct']}%)" for r in much) or "none") + ".",
        "",
        "Unfavorable on payoff rather than odds (the target is so close, or so far, that its hit rate "
        "does not cover the 1R lost at the stop): " + (", ".join(
            f"{r['ticker']} ({r['sim_target_first_pct']}% vs {r['sim_stop_first_pct']}%, "
            f"{r['r_at_target']:.1f}R)" for r in unfav if r not in much) or "none") + ".",
        "",
        f"## Flag (b): past stop in trade_plan.csv ({len(past)}) - priority review",
        "",
        "These closed through their stop before this run, so there is no forward replay: the stop "
        "has already been hit. Cut, or re-justify with a new thesis and a fresh stop.",
        "",
        "| Ticker | Name | Side | Entry | Current | Stop |",
        "|---|---|---|---|---|---|",
        *[f"| {r['ticker']} | {r['name']} | {r['side']} | {r['entry']:,.2f} | {r['current']:,.2f} | "
          f"{r['stop']:,.2f} |" for r in past],
        "",
        "## Method",
        "",
        "- **Engine:** the installed trader-timemachine skill's `simulate()` and verdict thresholds "
        "(`lean()`: the target's share of replays that hit one side vs the 1 / (1 + target R) break-even "
        "share; within 5 points = coin-flip, above = favorable, below = unfavorable). The stop is checked "
        "before the target inside every bar (a bar touching both counts as the stop).",
        "- **Multi-day horizon:** `timemachine.py` has no multi-day mode (its CLI replays one session of "
        "5-minute bars, and its history check is an opening-range-breakout rule). Here every one of the "
        f"engine's pool slots holds the ticker's own daily bars, drawn at random (window 0) for {HORIZON} "
        "trading days, each scaled to the previous simulated close.",
        f"- **Lookback:** the last {LOOKBACK} daily bars, or every bar since listing when younger "
        f"(range {lb[0]} to {lb[-1]} bars; per row in `lookback_days`). Same daily data as trade_plan.csv.",
        "- **Start:** today's close (the position is already open), so risk and R are measured from "
        "today's price, not from the original entry.",
        "- **Seed:** crc32(ticker) mod 100,000, recorded per row; the same seed and data give the same "
        "numbers.",
        "- **History:** from every past close in the lookback, the same stop and target distances (as a "
        f"% of price) walked forward {HORIZON} days. Windows overlap, so they are not independent.",
        "- **HY9H GR:** levels are in EUR (GDR); returns come from SK Hynix's Korean line 000660.KS.",
        "- **Not replayed:** positions already through their stop (no forward odds: the stop is hit) and "
        "winners already through their target (2R reached, trailing-stop only). No-data rows are skipped.",
        "",
        "Per-ticker detail (simulation, percentile bands, history, verdict line): `timemachine/<TICKER>.json`.",
        "",
    ]
    open(os.path.join(HERE, "timemachine.md"), "w").write("\n".join(md))


if __name__ == "__main__":
    main()
