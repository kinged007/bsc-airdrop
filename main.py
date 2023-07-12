# import pandas as pd
# import numpy
from utils import load_config, printHeading, printTitle, async_wait
import os, time, random, json
from loguru import logger as log
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.rpc import rpc_gas_price_strategy
import csv
import asyncio
# from pprint import pprint
from decimal import Decimal
import math

# debug
NOWAIT = True
log.remove(0)

# pd.set_option("chained_assignment", None)
 
config = load_config()

# print_config(config)

os.makedirs('data',exist_ok=True)


def get_native_currency():

	# TODO https://chainid.network/chains.json

	chain_id = config.getint('Common','chain_id')
	node = config.get('Common','node_http_url').strip("/")

	name = "?"
	symbol = "(Native Currency)"
	decimals = 18

	return name, symbol, decimals

def send_tokens(source_wallet, secret, qty, destination_wallet):

	# return 123

	from_wallet = w3.to_checksum_address(source_wallet)
	private_key = secret
	to_wallet = w3.to_checksum_address(destination_wallet)
	nonce= w3.eth.get_transaction_count(from_wallet)

	if contract_address:
		token_tx = contract.functions.transfer(to_wallet, w3.to_wei(Decimal(qty),'ether') ).build_transaction({
			'chainId' : config.getint('Common','chain_id'),
			# 'to': to_wallet,
			# 'value' : w3.to_wei(Decimal(qty),'ether'),
			'nonce' : w3.eth.get_transaction_count(from_wallet),
			'gas': config.getint('Common','gas_limit'),
			'gasPrice': w3.to_wei(Decimal(config.getfloat('Common','gas_price')), 'gwei'),
			# 'maxFeePerGas': w3.to_wei(50, 'gwei'),
			# 'maxPriorityFeePerGas': w3.to_wei(2, 'gwei'),
		})
	else:
		token_tx = {
			'chainId' : config.getint('Common','chain_id'),
			'to': to_wallet,
			'value' : w3.to_wei(Decimal(qty),'ether'),
			'nonce' : w3.eth.get_transaction_count(from_wallet),
			'gas': config.getint('Common','gas_limit'),
			'gasPrice': w3.to_wei(Decimal(config.getfloat('Common','gas_price')), 'gwei'),
			# 'maxFeePerGas': w3.to_wei(5, 'gwei'),
			# 'maxPriorityFeePerGas': w3.to_wei(2, 'gwei'),
		}	

	try:
		sign_tx = w3.eth.account.sign_transaction(token_tx, private_key=private_key)
		hash_tx = w3.eth.send_raw_transaction(sign_tx.rawTransaction)
		tx_receipt = w3.eth.wait_for_transaction_receipt(w3.to_hex(hash_tx), timeout=config.getint("Common","timeout_transaction_receipt",fallback=120))

		# print(tx_receipt)
		# print(tx_receipt['status'])

		if int(tx_receipt['status']) == 1:
			return w3.to_hex(hash_tx)

		# print(f"Transaction to '{to_wallet}' successful.")
		# print(" [Success] TX Hash: " + w3.to_hex(hash_tx))

	except Exception as e:
		print(f" [!!] " + str(e))

	return False

async def start():

	# get wallets again...
	source_rows = []
	s_r = []
	destination_rows = []
	d_r = []

	print("\nSorting Wallet data...")

	if os.path.isfile(os.path.join('data','source_wallets.csv')):
		with open(os.path.join('data','source_wallets.csv'), 'r', encoding='utf8') as f:
			csvreader = csv.reader(f, delimiter=',')
			next(csvreader) # skip header
			for row in csvreader:
				if not row or row[0] in s_r: continue
				source_rows.append(row)
				s_r.append(row[0])
			print("Rows found for 'source_wallets': %d" % (len(source_rows)))
			# print(source_rows)
	else:
		with open(os.path.join('data','source_wallets.csv'), 'w', encoding='utf-8') as f:
			csvwriter = csv.writer(f, delimiter=',')
			csvwriter.writerow(source_cols)

	if os.path.isfile(os.path.join('data','destination_wallets.csv')):
		with open(os.path.join('data','destination_wallets.csv'), 'r', encoding='utf8') as f:
			csvreader = csv.reader(f, delimiter=',')
			next(csvreader) # skip header
			for row in csvreader:
				if not row or row[0] in d_r: continue
				destination_rows.append(row)
				d_r.append(row[0])
			print("Rows found for 'destination_wallets': %d" % (len(destination_rows)))
			# print(destination_rows)
	else:
		with open(os.path.join('data','destination_wallets.csv'), 'w', encoding='utf-8') as f:
			csvwriter = csv.writer(f, delimiter=',')
			csvwriter.writerow(destination_cols)

	print("")

	if any(len(x)==0 for x in [source_rows,destination_rows]):
		exit("Please populate the data sheets with wallet information.")

	# show balances
	print("\nCurrent Balances:\n")
	for x in source_rows:
		if contract_address:
			b = contract.functions.balanceOf(w3.to_checksum_address(x[0])).call() / decimals
		else:
			b = w3.from_wei(w3.eth.get_balance(w3.to_checksum_address(x[0])), 'ether')
		print(f" [{x[0]}] = {b:,.{precision}f} {symbol}")

	print("")

	input("Press Enter to Start Airdrop... (Ctrl+C to exit) ")

	threads = config.getint("Common","threads_count",fallback=1)
	printHeading("Starting Airdrop...")
	await asyncio.gather(*[task(x) for x in range(threads)])
	printHeading("Airdrop completed")
	# pprint(source_rows)
	# pprint(destination_rows)

async def task(thread):
	while True:
		await async_wait(random.randrange(0,10))

		# print("Globals")
		# print(global_using_source)
		# print(global_using_destination)
		# pprint([x[0] for x in source_rows])
		# pprint([x[0] for x in destination_rows])
		# pprint(destination_rows)


		using_source = []	
		using_destination = []

		source = []
		destination = [] 	

		for x in source_rows:
			if x[2] == '': x[2] = 0.0
			if x[3] == '': x[3] = 0.0
			if float(x[2]) < float(x[3]) or any([math.isclose(float(x[c]),0) for c in [2,3]]):
				using_source.append(x)

		for x in destination_rows:
			if x[1] == '': x[1] = 0.0
			if x[2] == '': x[2] = 0.0
			if float(x[1]) < float(x[2]) or any([math.isclose(float(x[c]),0) for c in [1,2]]):
				using_destination.append(x)
		
		# print(f" [{thread}] Working...")

		# print("-=-=-=-=-")
		# print(using_source)
		# print(using_destination)
		# print("-=-=-=-=-")

		if len(using_source) == 0 or len(using_destination) == 0:
			print(f" [{thread}] No wallets to work with...")
			break

		# print(f" [{thread}] Choosing wallets...")
		timeout = time.time() + config.getint("Common","timeout_find_wallet",fallback=120)

		while True:
			t = random.choice(using_source)
			if t[0] not in global_using_source: 
				global_using_source.append(t[0])
				source = t
				break
			if time.time() > timeout: break
			await async_wait(3)
		
		
		while True:
			t = random.choice(using_destination)
			if t[0] not in global_using_destination: 
				global_using_destination.append(t[0])
				destination = t
				break
			if time.time() > timeout: break
			await async_wait(3)
		
		if not source or not destination:
			print(f" [{thread}] Could not determine wallet/s to work with.")
			await sleep(thread)
			continue

			
		# print(source)
		# print(destination)
		# print(global_using_source)
		# print(global_using_destination)

		# check source balance
		if contract_address:
			source_balance = contract.functions.balanceOf(w3.to_checksum_address(source[0])).call() / decimals
			source[4] = source_balance
			destination[3] = contract.functions.balanceOf(w3.to_checksum_address(destination[0])).call() / decimals
		else:
			source_balance = w3.from_wei(w3.eth.get_balance(w3.to_checksum_address(source[0])), 'ether') 
			source[4] = source_balance
			destination[3] =  w3.from_wei(w3.eth.get_balance(w3.to_checksum_address(destination[0])), 'ether') 

		#### Process send
		# print(source)
		# print(destination)

		source_wallet = source[0]
		secret			= source[1]
		q =  float(destination[2])-float(destination[1])		
		qty				= q if q < config.getfloat("Common","max_send_amount") else config.getfloat("Common","max_send_amount")
		if math.isclose(qty,0) or qty < 0: qty = config.getfloat("Common","max_send_amount")
		# decimals = 10000000
		minn = config.getfloat("Common","min_send_amount",fallback=0.0) * decimals if config.getfloat("Common","min_send_amount",fallback=0.0) > 0 else 0
		maxx = qty * decimals
		# print("{:.18f}".format(minn))
		# print("{:.18f}".format(maxx))
		qty = random.randrange(int(minn),int(maxx)) / decimals
		# qty = w3.to_wei(Decimal(qty),'ether')
		# print("{:.18f}".format(decimals))
		# print("{:.18f}".format(qty))
		

		destination_wallet = destination[0]

		print(f" [{thread}] [Balance] [{source_wallet}]  = {source_balance:,.{precision}f} {symbol}")

		if source_balance < qty:
			print(f" [{thread}] Trying to send more than available balance.")
			break

		
		print(f" [{thread}] Sending '{qty:,.{precision}f}' from '{source[0]}' to '{destination[0]}'... ")

		# exit()

		tx_id = send_tokens(source_wallet, secret, qty, destination_wallet)
		if not tx_id:
			print(f" [{thread}] Transaction Failed. ")
			await sleep(thread)
			break #continue # or break?

		#### update variables
		# indexes
		s_i = source_rows.index([x for x in source_rows if x[0] == source_wallet][0])
		d_i = destination_rows.index([x for x in destination_rows if x[0] == destination_wallet][0])

		source[2] 		= float(source[2]) + qty
		destination[1] 	= float(destination[1]) + qty
		source[4] 		= float(source[4]) - qty
		destination[3] 	= float(destination[3]) + qty

		print(f" [{thread}] Transaction completed: {tx_id} ; [Balance] [{destination[0]}] {destination[3]:,.{precision}f} {symbol}")

		if config.getboolean("Common","one_transaction_per_wallet",fallback=True):
			# source[3] = soruce[2]
			destination[2] = destination[1]

		# adjust max send
		if float(source[4]) < float(source[3]): source[4] = source[3]

		# print("new values")
		# print(source)
		# print(destination)
		for idx, item in enumerate(source_rows):
			if item[0] == source_wallet:
				source_rows[idx] = source
		for idx, item in enumerate(destination_rows):
			if item[0] == destination_wallet:
				destination_rows[idx] = destination


		# source_rows[s_i] = source
		# destination_rows[s_i] = destination
		# print(d_i)
		# pprint(destination_rows)

		# set values as text for csv
		source[2] 		= f"{source[2]:.{precision}f}"
		source[3] 		= f"{float(source[3]):.{precision}f}"
		source[4] 		= f"{source[4]:.{precision}f}"
		destination[1] 	= f"{destination[1]:.{precision}f}"
		destination[2] 	= f"{float(destination[2]):.{precision}f}"
		destination[3] 	= f"{destination[3]:.{precision}f}"		

		#### update csv
		with open(os.path.join('data','source_wallets.csv'), 'w', encoding='utf-8',newline='') as f:
			csvwriter = csv.writer(f, delimiter=',')
			csvwriter.writerow(source_cols)
			csvwriter.writerows(source_rows)

		with open(os.path.join('data','destination_wallets.csv'), 'w', encoding='utf-8', newline='') as f:
			csvwriter = csv.writer(f, delimiter=',')
			csvwriter.writerow(destination_cols)
			csvwriter.writerows(destination_rows)


		await async_wait(5)
		del global_using_destination[global_using_destination.index(destination[0])]
		del global_using_source[global_using_source.index(source[0])]

		# print(f" [{thread}] Completed sending from '{source[0]}' to '{destination[0]}'... ")

		# print(global_using_source)
		# print(global_using_destination)

		# break

		await sleep(thread)

async def sleep(thread):
	_t = random.randrange(config.getint("Common","delay_between_transfer_from",fallback=3200),config.getint("Common","delay_between_transfer_to",fallback=6200))
	print(f" [{thread}] Resting for {_t} seconds...Press Ctrl+C to abort...")
	await async_wait(_t)

if __name__ == "__main__":


	printTitle("Crypto Airdrop")

	print("")

	print("Loading wallets...")

	### get wallet files
	source_cols = ["wallet_address","secret","send_total","send_max","last_balance"]
	destination_cols = ["wallet_address","receive_total","receive_max","last_balance"]
	source_rows = []
	s_r = []
	destination_rows = []
	d_r = []

	if os.path.isfile(os.path.join('data','source_wallets.csv')):
		with open(os.path.join('data','source_wallets.csv'), 'r', encoding='utf8') as f:
			csvreader = csv.reader(f, delimiter=',')
			next(csvreader) # skip header
			for row in csvreader:
				if not row or row[0] in s_r: continue
				source_rows.append(row)
				s_r.append(row[0])
			print("Rows found for 'source_wallets': %d" % (len(source_rows)))
			# print(source_rows)
	else:
		with open(os.path.join('data','source_wallets.csv'), 'w', encoding='utf-8') as f:
			csvwriter = csv.writer(f, delimiter=',')
			csvwriter.writerow(source_cols)

	if os.path.isfile(os.path.join('data','destination_wallets.csv')):
		with open(os.path.join('data','destination_wallets.csv'), 'r', encoding='utf8') as f:
			csvreader = csv.reader(f, delimiter=',')
			next(csvreader) # skip header
			for row in csvreader:
				if not row or row[0] in d_r: continue
				destination_rows.append(row)
				d_r.append(row[0])
			print("Rows found for 'destination_wallets': %d" % (len(destination_rows)))
			# print(destination_rows)
	else:
		with open(os.path.join('data','destination_wallets.csv'), 'w', encoding='utf-8') as f:
			csvwriter = csv.writer(f, delimiter=',')
			csvwriter.writerow(destination_cols)

	### print pandas dataframes 
	print("")

	async_wait(3)

	try:
		node = config.get('Common','node_http_url')
		print("Connecting to blockchain node: " + node)
		# node = "https://data-seed-prebsc-1-s1.binance.org:8545"
		# node = 'https://young-old-meadow.bsc-testnet.discover.quiknode.pro/7b687e8927ce5e0dea922c34a0a25827c1147ead/'
		w3 = Web3(Web3.HTTPProvider(node))
		w3.middleware_onion.inject(geth_poa_middleware, layer=0) # for testnet only
		if not w3.is_connected():
			exit("Cannot connect to blockchain.")
		print("Connected...")

		contract_address = config.get('Common','token_contract')

		tokenNameABI = json.loads('[ { "anonymous": false, "inputs": [ { "indexed": true, "internalType": "address", "name": "owner", "type": "address" }, { "indexed": true, "internalType": "address", "name": "spender", "type": "address" }, { "indexed": false, "internalType": "uint256", "name": "value", "type": "uint256" } ], "name": "Approval", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": true, "internalType": "address", "name": "from", "type": "address" }, { "indexed": true, "internalType": "address", "name": "to", "type": "address" }, { "indexed": false, "internalType": "uint256", "name": "value", "type": "uint256" } ], "name": "Transfer", "type": "event" }, { "constant": true, "inputs": [ { "internalType": "address", "name": "_owner", "type": "address" }, { "internalType": "address", "name": "spender", "type": "address" } ], "name": "allowance", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "address", "name": "spender", "type": "address" }, { "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "approve", "outputs": [ { "internalType": "bool", "name": "", "type": "bool" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "address", "name": "account", "type": "address" } ], "name": "balanceOf", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "decimals", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "getOwner", "outputs": [ { "internalType": "address", "name": "", "type": "address" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "name", "outputs": [ { "internalType": "string", "name": "", "type": "string" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "symbol", "outputs": [ { "internalType": "string", "name": "", "type": "string" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "totalSupply", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "address", "name": "recipient", "type": "address" }, { "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "transfer", "outputs": [ { "internalType": "bool", "name": "", "type": "bool" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "address", "name": "sender", "type": "address" }, { "internalType": "address", "name": "recipient", "type": "address" }, { "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "transferFrom", "outputs": [ { "internalType": "bool", "name": "", "type": "bool" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" } ]')

		if contract_address:
			# w3.eth.accounts.wallet.add('0xff11a717c09d7100cfa6a59f51261a5b85e316d47292bfcfe8ca5f40bcb463fc') # 0x0db36ecdc28b22d75708d0d5e1a26913c5da1598 : 0xff11a717c09d7100cfa6a59f51261a5b85e316d47292bfcfe8ca5f40bcb463fc
			# w3.eth.default_account = w3.to_checksum_address('0x0db36ecdc28b22d75708d0d5e1a26913c5da1598')
			contract = w3.eth.contract(address=contract_address, abi=tokenNameABI)
		else:
			pass
			# https://chainid.network/chains.json
			# match node_url or chain_id to known list of networks to get native currency information


	except Exception as e:
		print("ERROR: " + str(e))
		input("Press Enter to exit... ")	
		exit()

	try:
		if contract_address:
			print("Found contract...")
			print("")
			print("[Name] = " + contract.functions.name().call())
			symbol = contract.functions.symbol().call()
			print("[Symbol] = " + symbol)
			precision = contract.functions.decimals().call()
			decimals = float(10 ** precision)
			print("[Decimals] = " + str(contract.functions.decimals().call()))
			print("[Total Supply] = " + "{:,}".format(int(contract.functions.totalSupply().call() / decimals)))
		else:
			print("\nUsing Native Currency...")
			# TODO https://chainid.network/chains.json
			name, symbol, precision = get_native_currency()
			decimals = float(10 ** 18)
			print(f"[Name] = {name}")
			print(f"[Symbol] = {symbol}")
			print(f"[Decimals] = {precision}")

		print("")

		w3.eth.set_gas_price_strategy(rpc_gas_price_strategy)

		if config.getboolean("Common","use_auto_gas_price",fallback=False):
			config['Common']['gas_price'] = str(w3.from_wei(Decimal(w3.eth.generate_gas_price()), 'gwei'))

		# print("[Current Gas Price] = " + str(w3.from_wei(w3.eth.gas_price, 'gwei')))

		print("[Generated Gas Price] = " + str(w3.from_wei(Decimal(w3.eth.generate_gas_price()), 'gwei')))


		print("\nConfigurations\n")

		print("[use_auto_gas_price] = " + str(config.getboolean("Common","use_auto_gas_price",fallback=False) ))
		print("[gas_price] = " + config.get("Common","gas_price") )
		print("[gas_limit] = " + config.get("Common","gas_limit") )

		print("[min_send_amount] = " + config.get("Common","min_send_amount") )
		print("[max_send_amount] = " + config.get("Common","max_send_amount") )




	except Exception as e:
		print(" [!!] "+str(e))
		input("Press Enter to exit... ")
		exit()

	print("[threads_count] = " + str(config.getint("Common","threads_count") ))
	print(f"[delay_between_transfer_from] = {config.get('Common','delay_between_transfer_from',fallback='')}")
	print(f"[delay_between_transfer_to] = {config.get('Common','delay_between_transfer_to',fallback='')}")
	print(f"[one_transaction_per_wallet] = {config.getboolean('Common','one_transaction_per_wallet',fallback='')}")

	print("")

	print("\nPlease ensure there is wallet data to work with before you continue...")
	input("Press Enter to continue (Ctrl+C to exit) ")

	# exit()

	global_using_source = []
	global_using_destination = []

	try:
		log.debug("Starting multi-threading")
		asyncio.run(start())
	except KeyboardInterrupt:
		log.info('Exiting...')

	input("Press Enter to exit... ")



