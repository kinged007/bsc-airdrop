# crypto-airdrop

## Description

This app can either simulate an airdrop (single transaction) of tokens to multiple receiving wallets, or multiple transactions of tokens to destination wallets. 

Random Senders are chosen to send a randomised amount to a random receiver. Limitations and maximum amounts may be applied through the `config.ini` file or the columns `send_max` and `receive_max` in the CSV files. 

## Installation
1. To install, just execute `install.bat` on Windows, or `run.bat` (Windows) or `run.sh` (Mac/Linux) for the first time.
2. Rename `config_sample.ini` to `config.ini`.
3. Open `config.ini` and set parameters.
4. Execute `run.bat` (Windows) or `run.sh` (Mac/Linux) to create directories and templates.

## Configuration options

`threads_count` is the number of multi-processes to run at the same time.

`delay_between_transfer_from`  is the min seconds to wait between transactions (per thread/process)

`delay_between_transfer_to`  is the max seconds to wait between transactions (per thread/process)

`min_send_amount`  is the minimum transaction volume (of token) to send.

`max_send_amount`  is the maximum transaction volume (of token) to send. A random number between min and max is issued.

`token_name`  (optional) just the name of the token you are executing.

`token_contract`  the contract address (Upper case) of ERC20 Token. Empty will resort to using the chains native currency (eg. BNB on BSC)

`node_http_url`  the RPC URL for the blockchain. See https://rpc.info/

`chain_id`  the chain ID for the blockchain in use. See https://rpc.info/

`use_auto_gas_price`  (boolean) Auto set the gas price based on default pricing strategy (easy option)

`gas_price`  set your own gas price to use. If value is too low, transactions will fail.

`gas_limit`  set your gas limit. Depends on blockchain, see last transactions on network to get an idea.

`timeout_find_wallet`  (seconds) timeout value to find suitable wallet to work with.

`timeout_transaction_receipt`  (seconds) timeout value to wait for transaction receipt. Assumed fail if no transaction receipt received.

`one_transaction_per_wallet` (boolean) If `True`, each destination wallet will only receive one transaction.


## Other information

If no `token_contract` is set, the app will send the native currency to the destination wallets, if that wallet has sufficient balance.

If `one_transaction_per_wallet` is `True`, each destination will receive only ONE transaction. 
If this is `False`, then the receivers will continue receiveing transactions up to the `receive_max` amount defined in the `destination_wallets.csv` file. If this value is empty or `0`, the receiver will continue receiving transactions until the sender runs out of funds.

See `Wallet Data` below to see how to apply other transaction limitations.

## Wallet data

The wallet data (for senders and receivers) are found in the `data` folder.

### Sender / Source

The columns for the `source_wallets.csv` (senders) are as follows:

`wallet_address , secret , send_total , send_max , last_balance`

Required columns: `wallet_address , secret`

`wallet_address` = wallet address of sender

`secret`   = wallet private key of sender

`send_total` = (leave empty) the total amount of tokens sent by this app.

`send_max` = (optional) if set, the app will not send more than this total amount to various receivers. If empty, the app will continue until there is no more available funds.

`last_balance` = (leave empty) The last balance is auto updated after each transaction.


### Receiver / Destination

The columns for the `destination_wallets.csv` (receivers) are as follows:

`wallet_address , receive_total , receive_max , last_balance`

Required columns: `wallet_address`

`wallet_address` = wallet address of receiver

`receive_total` = (leave empty) the total amount of tokens received by senders of this app.

`receive_max` = (optional) if set, the app will not receive more than this total amount from the various senders. If empty, the app will continue until the senders run out of money or the app is closed (or if `one_transaction_per_wallet` is true).

`last_balance` = (leave empty) The last balance is auto updated after each transaction.


