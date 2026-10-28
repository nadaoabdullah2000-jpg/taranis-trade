# Taranis - trade

The 11 day-trader skills from
[Jakeschincariol/day-trader-skill](https://github.com/Jakeschincariol/day-trader-skill)
(MIT-licensed, see `LICENSE`), installed under `.claude/skills/` so they load
in every Claude Code session of this repo.

Skills: trader-scanner, trader-news, trader-entry, trader-exit,
trader-timemachine, trader-budget, trader-risk, trader-alerts, trader-broker,
trader-analyst, trader-pelosi.

- **Paper trading is the default.** `trader-broker` sends nothing to a broker
  without your explicit yes, and targets a paper account unless you change it.
- **No brokerage keys in this repo.** Keep them in environment variables only
  (e.g. `ALPACA_API_KEY`, `ALPACA_SECRET_KEY`).
- `trader/config.json` holds the SEC User-Agent. Everything else the skills
  write under `trader/` is runtime output and is git-ignored.
