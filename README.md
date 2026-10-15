# bsc-airdrop

[![CI](https://github.com/kinged007/bsc-airdrop/actions/workflows/ci.yml/badge.svg)](https://github.com/kinged007/bsc-airdrop/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](requirements.txt)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Free BSC token airdrop tool for project owners to distribute ERC-20 or native BNB to many wallets from CSV files. Configure send limits, concurrency, and gas — free for any project owner.

![Demo](./docs/screenshot.png)
> Screenshot to be added — run `python main.py` to see the interactive airdrop flow (wallet balances, random amounts, transaction receipts).

## What it is

- Sends ERC-20 tokens or native currency (BNB) to many destination wallets from a funded set of source wallets.
- Random sender / receiver selection with configurable min/max amounts, per-wallet caps (`send_max` / `receive_max`), and multi-threaded execution.
- Designed for BSC but works with any EVM chain via `node_http_url` / `chain_id` in `config.ini`.

## Install

Prereqs: Python 3.10+.

```bash
# clone
git clone https://github.com/kinged007/bsc-airdrop.git
cd bsc-airdrop

# quick start (creates venv + installs deps)
./run.sh          # macOS / Linux
# or
run.bat           # Windows

# manual
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate.bat
pip install -r requirements.txt
```

## Configuration

```bash
cp config_sample.ini config.ini
# edit config.ini: set node_http_url, chain_id, token_contract, amounts, gas
```

Key options (see `config_sample.ini` for all):

| Option | Description |
|---|---|
| `threads_count` | Concurrent workers |
| `delay_between_transfer_from` / `delay_between_transfer_to` | Random wait between transfers (seconds) |
| `min_send_amount` / `max_send_amount` | Random amount per transfer |
| `token_contract` | ERC-20 address (empty = native currency) |
| `node_http_url` / `chain_id` | RPC URL and chain ID (e.g. BSC 56, BSC testnet 97) |
| `gas_price` / `gas_limit` | Gas settings (`use_auto_gas_price = true` to auto) |
| `one_transaction_per_wallet` | If true, each destination receives once |

## Usage

1. Populate `data/source_wallets.csv` (sender address + private key, optional `send_max`) and `data/destination_wallets.csv` (receiver addresses, optional `receive_max`). Templates are created on first run.
2. Fill `config.ini`.
3. Run:

```bash
./run.sh
# or
python main.py
```

The tool shows balances, planned send range, and streams transaction hashes. CSV files are updated with `send_total` / `receive_total` and `last_balance` after each transfer. Press Ctrl+C to stop gracefully.

> **Security:** `config.ini` and `data/` are gitignored. Never commit private keys or funded wallet files. The sample config points at BSC testnet.

## How it is tested

```bash
pip install -r requirements-dev.txt   # pytest, ruff, mypy
pytest -q
ruff check .
mypy .
# or via the check in CI
```

Tests cover config loading and CSV parsing / wallet selection logic. Lint and type checks run on every push/PR via GitHub Actions.

## Project structure

```
config_sample.ini      sample config (copy to config.ini)
main.py                airdrop orchestration, web3 transfers
utils.py               config / logging / helpers
requirements.txt       runtime deps
requirements-dev.txt   test + lint deps
data/                  source_wallets.csv, destination_wallets.csv (gitignored)
```

## License

MIT — see [LICENSE](LICENSE).
