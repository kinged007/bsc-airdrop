# AGENTS.md — bsc-airdrop

## Purpose

Free BSC (EVM) token airdrop tool for project owners. Distributes ERC-20 or native currency (BNB) from a set of funded source wallets to many destination wallets listed in CSV files. Configurable amounts, per-wallet caps, gas, and concurrency. Python, web3.py, asyncio.

## How to run checks

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
ruff check .
mypy . --ignore-missing-imports
pytest -q
```

CI (`.github/workflows/ci.yml`) runs the same on push/PR to `master`.

## Skills / workflow

- Keep changes small and focused; do not add new dependencies without need.
- Do not commit `config.ini` or anything under `data/` — they hold private keys / funded wallets and are gitignored. Use `config_sample.ini` as the template.
- Keep this repo self-contained. Do not add network calls in tests; mock external services.

## Branch / PR workflow

- Default branch is `master`. Do not push directly to it.
- Create a feature branch, commit, push, and open a PR against `master` (`gh pr create`).
- Use commit identity `kinged007 <599286+kinged007@users.noreply.github.com>`.

## Permissions

- No secrets in commits. Do not copy `.env` or real wallet CSVs into docs or tests (tests use tmp paths).
