# Time Machine: odds of target before stop, per position

37 positions replayed, 10,000 paths each, 20 trading days (~4 weeks) forward from the latest close. Stops and targets are taken unchanged from `trade_plan.csv`. Simulation, not prediction: it is built from each stock's own recent daily bars and cannot see an earnings report, a halt or a headline. Treat the odds as a reality check. Analysis only: paper, nothing placed.

Verdicts on the replayed positions: 8 favorable, 18 coin-flip, 11 unfavorable. 46 more were not replayed because the price is already through the stop (or the target): see the review list below.

**How the verdict reads:** it weighs the odds against the payoff, as the skill does. A target at 0.2R needs to come first in 83 % of the replays that hit a side just to break even, so 77 % target-first is still *unfavorable*; a 5R target breaks even at 17 %, so 20 % is a *coin-flip*. Avg R shows the same thing as a number.

Columns: **Target first / Stop first / Neither** = share of the 10,000 replays; **Avg R** = mean result in R, where R is the distance from today's price to the stop (+target R at the target, -1 at the stop, open move / R otherwise); **Target R** = target distance / stop distance from today's price; **History T / S / N** = past rolling 20-day windows that hit target first / stop first / neither with the same % distances.

## Longs (ranked by target-first odds)

| # | Ticker | Name | Target first | Stop first | Neither | Avg R | Target R | History T / S / N | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 1 | OHB GY | OHB SE | 87.2% | 12.8% | 0.0% | -0.01 | 0.14 | 199 / 29 / 2 | coin-flip |
| 2 | HO FP | Thales S.A. | 82.2% | 17.8% | 0.0% | -0.04 | 0.17 | 182 / 48 / 0 | coin-flip |
| 3 | 9468 JP | Kadokawa Corporation | 80.0% | 20.0% | 0.0% | -0.07 | 0.16 | 181 / 42 / 0 | unfavorable |
| 4 | NVDA | NVIDIA Corporation | 77.4% | 22.6% | 0.0% | -0.08 | 0.18 | 182 / 48 / 0 | unfavorable |
| 5 | SCW PW | Scanway S.A. | 69.5% | 30.6% | 0.0% | -0.16 | 0.21 | 159 / 71 / 0 | unfavorable |
| 6 | LITE | Lumentum Holdings Inc. | 65.2% | 34.8% | 0.0% | -0.20 | 0.23 | 150 / 80 / 0 | unfavorable |
| 7 | CRDO | Credo Technology Group Holding Ltd | 52.8% | 45.4% | 1.8% | +0.09 | 1.03 | 105 / 122 / 3 | coin-flip |
| 8 | BE | Bloom Energy Corporation | 51.3% | 48.7% | 0.0% | +0.10 | 1.15 | 118 / 112 / 0 | coin-flip |
| 9 | MU | Micron Technology, Inc. | 48.5% | 51.4% | 0.0% | +0.00 | 1.07 | 111 / 119 / 0 | coin-flip |
| 10 | GOOG | Alphabet Inc. | 46.8% | 53.2% | 0.0% | +0.01 | 1.16 | 108 / 122 / 0 | coin-flip |
| 11 | NBIS | Nebius Group N.V. | 42.3% | 42.6% | 15.1% | +0.16 | 1.36 | 90 / 99 / 41 | favorable |
| 12 | CRI PW | Creotech Instruments S.A. | 38.1% | 61.9% | 0.0% | +0.28 | 2.37 | 91 / 139 / 0 | favorable |
| 13 | AMD | Advanced Micro Devices, Inc. | 37.5% | 62.5% | 0.0% | -0.21 | 1.10 | 86 / 144 / 0 | unfavorable |
| 14 | 3081 TT | LandMark Optoelectronics Corporation | 35.2% | 64.8% | 0.0% | +1.04 | 4.79 | 85 / 138 / 0 | favorable |
| 15 | 3661 TT | Alchip Technologies, Limited | 32.9% | 67.1% | 0.0% | -0.01 | 2.02 | 73 / 150 / 0 | coin-flip |
| 16 | AVGO | Broadcom Inc. | 31.1% | 68.9% | 0.0% | +0.10 | 2.55 | 63 / 167 / 0 | coin-flip |
| 17 | GNS PW | Niewiadów Polska Grupa Militarna S.A. | 30.9% | 69.1% | 0.0% | +0.02 | 2.31 | 72 / 158 / 0 | coin-flip |
| 18 | 186A JP | Astroscale Holdings Inc. | 30.6% | 69.4% | 0.0% | +0.38 | 3.50 | 70 / 153 / 0 | favorable |
| 19 | AMZN | Amazon.com, Inc. | 27.2% | 72.8% | 0.0% | +0.24 | 3.55 | 61 / 169 / 0 | favorable |
| 20 | MSFT | Microsoft Corporation | 19.5% | 80.5% | 0.0% | +0.23 | 5.29 | 37 / 193 / 0 | coin-flip |
| 21 | HY9H GR | SK hynix Inc. (GDR) | 19.2% | 80.7% | 0.1% | +1.86 | 13.85 | 52 / 171 / 2 | favorable |
| 22 | CRQ PW | Creotech Quantum S.A. | 19.0% | 80.8% | 0.2% | -0.01 | 4.21 | 15 / 97 / 5 | coin-flip |

Not replayed (the level is already behind the price): AMAT (already through the stop); ENX FP (target already reached); ASML NA (already through the stop); 009150 KS (already through the stop); COIN (already through the stop); PNG CN (already through the stop); SHAZ (already through the stop); 347700 KS (already through the stop); ARM (already through the stop); MP1 AU (already through the stop); MAXQ CN (already through the stop); HPE (already through the stop); 9880 HK (already through the stop); 290A JP (already through the stop); CRWV (already through the stop); CBRS (already through the stop); GOMX SS (already through the stop); FLY (already through the stop); PRIUA CP (already through the stop); 464A JP (already through the stop); 462350 KS (already through the stop); LFR PW (already through the stop); KEBNIB SS (already through the stop); 100 HK (already through the stop).

## Shorts (ranked by target-first odds)

For a short, target first = the price falls to the target before it rises to the stop.

| # | Ticker | Name | Target first | Stop first | Neither | Avg R | Target R | History T / S / N | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 1 | MELI | MercadoLibre, Inc. | 94.8% | 5.1% | 0.0% | -0.02 | 0.03 | 219 / 10 / 1 | coin-flip |
| 2 | SOUN | SoundHound AI, Inc. | 93.4% | 6.6% | 0.0% | +0.01 | 0.08 | 217 / 13 / 0 | coin-flip |
| 3 | TMUS | T-Mobile US, Inc. | 93.0% | 6.9% | 0.0% | -0.05 | 0.02 | 216 / 14 / 0 | unfavorable |
| 4 | ADYEN NA | Adyen N.V. | 90.2% | 9.0% | 0.8% | +0.01 | 0.11 | 208 / 16 / 6 | coin-flip |
| 5 | CSGP | CoStar Group, Inc. | 86.2% | 12.0% | 1.8% | +0.09 | 0.25 | 211 / 15 / 4 | favorable |
| 6 | STX | Seagate Technology Holdings plc | 75.1% | 24.9% | 0.0% | -0.21 | 0.06 | 164 / 66 / 0 | unfavorable |
| 7 | COHR | Coherent Corp. | 73.9% | 26.2% | 0.0% | -0.07 | 0.26 | 171 / 59 / 0 | unfavorable |
| 8 | VRT | Vertiv Holdings Co | 72.6% | 27.4% | 0.0% | -0.09 | 0.25 | 165 / 65 / 0 | unfavorable |
| 9 | RKLB | Rocket Lab Corporation | 70.8% | 29.2% | 0.0% | -0.22 | 0.11 | 162 / 68 / 0 | unfavorable |
| 10 | TTWO | Take-Two Interactive Software, Inc. | 64.3% | 34.8% | 0.8% | +0.04 | 0.61 | 140 / 79 / 11 | coin-flip |
| 11 | DKNG | DraftKings Inc. | 58.4% | 18.8% | 22.8% | +0.06 | 0.50 | 131 / 47 / 52 | favorable |
| 12 | MBLY | Mobileye Global Inc. | 52.8% | 47.2% | 0.0% | -0.44 | 0.07 | 124 / 106 / 0 | unfavorable |
| 13 | DUOL | Duolingo, Inc. | 31.2% | 65.8% | 2.9% | +0.07 | 2.27 | 56 / 164 / 10 | coin-flip |
| 14 | OWL | Blue Owl Capital Inc. | 26.2% | 73.9% | 0.0% | +0.17 | 3.46 | 61 / 169 / 0 | coin-flip |
| 15 | HFG GY | HelloFresh SE | 9.6% | 90.4% | 0.0% | +0.83 | 18.00 | 28 / 202 / 0 | coin-flip |

Not replayed (the level is already behind the price): TEAM (already through the stop); VEEV (already through the stop); REY IM (already through the stop); SAP GY (already through the stop); SHOP (already through the stop); EDR SM (already through the stop); GWRE (already through the stop); FIG (already through the stop); NYT (already through the stop); AAPL (already through the stop); ABNB (already through the stop); REA AU (already through the stop); BSY (already through the stop); 9684 JP (already through the stop); WIX (already through the stop); GTLB (already through the stop); BSP (already through the stop); SECTB SS (already through the stop); PME AU (already through the stop); ASTS (target already reached); NFLX (target already reached); WULF (already through the stop).

## Flag (a): unfavorable odds

11 replayed positions lean toward the stop. Stop first at least twice as likely as target first (0): none.

Unfavorable on payoff rather than odds (the target is so close, or so far, that its hit rate does not cover the 1R lost at the stop): AMD (37.5% vs 62.5%, 1.1R), MBLY (52.8% vs 47.2%, 0.1R), LITE (65.2% vs 34.8%, 0.2R), SCW PW (69.5% vs 30.6%, 0.2R), RKLB (70.8% vs 29.2%, 0.1R), VRT (72.6% vs 27.4%, 0.3R), COHR (73.9% vs 26.2%, 0.3R), STX (75.1% vs 24.9%, 0.1R), NVDA (77.4% vs 22.6%, 0.2R), 9468 JP (80.0% vs 20.0%, 0.2R), TMUS (93.0% vs 6.9%, 0.0R).

## Flag (b): past stop in trade_plan.csv (43) - priority review

These closed through their stop before this run, so there is no forward replay: the stop has already been hit. Cut, or re-justify with a new thesis and a fresh stop.

| Ticker | Name | Side | Entry | Current | Stop |
|---|---|---|---|---|---|
| AMAT | Applied Materials, Inc. | LONG | 504.93 | 416.00 | 475.49 |
| ASML NA | ASML Holding N.V. | LONG | 1,623.76 | 1,489.60 | 1,547.12 |
| 009150 KS | Samsung Electro-Mechanics Co., Ltd. | LONG | 1,465,682.88 | 1,306,000.00 | 1,320,260.50 |
| COIN | Coinbase Global, Inc. | LONG | 177.44 | 162.32 | 162.95 |
| PNG CN | Kraken Robotics Inc. | LONG | 5.78 | 3.89 | 5.40 |
| SHAZ | SharonAI Holdings Inc. | LONG | 45.19 | 28.47 | 39.58 |
| 347700 KS | Life Semantics Corp | LONG | 30,926.53 | 20,750.00 | 28,005.10 |
| ARM | Arm Holdings plc | LONG | 303.18 | 235.90 | 281.51 |
| MP1 AU | Megaport Limited | LONG | 21.15 | 18.48 | 19.16 |
| MAXQ CN | Maritime Launch Services Inc. | LONG | 0.53 | 0.47 | 0.49 |
| HPE | Hewlett Packard Enterprise Company | LONG | 71.64 | 60.33 | 66.41 |
| 9880 HK | Ubtech Robotics Corp Ltd | LONG | 87.99 | 69.10 | 81.04 |
| 290A JP | Synspective Inc. | LONG | 1,355.89 | 1,230.00 | 1,253.87 |
| CRWV | CoreWeave, Inc. | LONG | 96.63 | 63.93 | 87.77 |
| CBRS | Cerebras Systems Inc. | LONG | 234.37 | 112.56 | 217.20 |
| GOMX SS | GomSpace Group AB (publ) | LONG | 21.78 | 12.51 | 20.44 |
| FLY | Firefly Aerospace Inc. | LONG | 34.67 | 19.85 | 32.61 |
| PRIUA CP | Primoco UAV SE | LONG | 824.47 | 640.00 | 794.29 |
| 464A JP | QPS Holdings Inc. | LONG | 2,448.66 | 1,441.00 | 2,334.26 |
| 462350 KS | Innospace Co Ltd | LONG | 13,311.03 | 5,020.00 | 12,599.55 |
| LFR PW | LFR C.XNCO PLN | LONG | 75.00 | 48.22 | 70.38 |
| KEBNIB SS | KebNi AB (publ) | LONG | 1.55 | 0.62 | 1.48 |
| 100 HK | MiniMax Group Inc. | LONG | 777.97 | 180.20 | 745.52 |
| TEAM | Atlassian Corporation | SHORT | 158.87 | 220.12 | 171.97 |
| VEEV | Veeva Systems Inc. | SHORT | 183.23 | 317.82 | 197.36 |
| REY IM | Reply S.p.A. | SHORT | 93.37 | 131.10 | 98.55 |
| SAP GY | SAP SE | SHORT | 158.96 | 211.20 | 167.38 |
| SHOP | Shopify Inc. | SHORT | 124.06 | 168.22 | 134.67 |
| EDR SM | eDreams ODIGEO S.A. | SHORT | 4.45 | 4.78 | 4.71 |
| GWRE | Guidewire Software, Inc. | SHORT | 129.56 | 166.92 | 141.93 |
| FIG | Figma, Inc. | SHORT | 21.17 | 23.21 | 22.94 |
| NYT | The New York Times Company | SHORT | 65.62 | 69.18 | 68.34 |
| AAPL | Apple Inc. | SHORT | 287.95 | 343.83 | 297.20 |
| ABNB | Airbnb, Inc. | SHORT | 132.50 | 166.04 | 139.30 |
| REA AU | REA Group Limited | SHORT | 142.12 | 158.16 | 149.63 |
| BSY | Bentley Systems, Incorporated | SHORT | 32.90 | 39.43 | 34.65 |
| 9684 JP | Square Enix Holdings Co., Ltd. | SHORT | 2,539.95 | 2,923.50 | 2,655.63 |
| WIX | Wix.com Ltd. | SHORT | 58.48 | 78.56 | 64.86 |
| GTLB | GitLab Inc. | SHORT | 40.47 | 57.97 | 44.10 |
| BSP | Bending Spoons S.p.A. | SHORT | 34.98 | 47.02 | 41.44 |
| SECTB SS | Sectra AB (publ) | SHORT | 183.11 | 338.80 | 195.39 |
| PME AU | Pro Medicus Limited | SHORT | 123.79 | 196.00 | 134.18 |
| WULF | TeraWulf Inc. | SHORT | 10.49 | 13.42 | 12.18 |

## Method

- **Engine:** the installed trader-timemachine skill's `simulate()` and verdict thresholds (`lean()`: the target's share of replays that hit one side vs the 1 / (1 + target R) break-even share; within 5 points = coin-flip, above = favorable, below = unfavorable). The stop is checked before the target inside every bar (a bar touching both counts as the stop).
- **Multi-day horizon:** `timemachine.py` has no multi-day mode (its CLI replays one session of 5-minute bars, and its history check is an opening-range-breakout rule). Here every one of the engine's pool slots holds the ticker's own daily bars, drawn at random (window 0) for 20 trading days, each scaled to the previous simulated close.
- **Lookback:** the last 250 daily bars, or every bar since listing when younger (range 84 to 250 bars; per row in `lookback_days`). Same daily data as trade_plan.csv.
- **Start:** today's close (the position is already open), so risk and R are measured from today's price, not from the original entry.
- **Seed:** crc32(ticker) mod 100,000, recorded per row; the same seed and data give the same numbers.
- **History:** from every past close in the lookback, the same stop and target distances (as a % of price) walked forward 20 days. Windows overlap, so they are not independent.
- **HY9H GR:** levels are in EUR (GDR); returns come from SK Hynix's Korean line 000660.KS.
- **Not replayed:** positions already through their stop (no forward odds: the stop is hit) and winners already through their target (2R reached, trailing-stop only). No-data rows are skipped.

Per-ticker detail (simulation, percentile bands, history, verdict line): `timemachine/<TICKER>.json`.
