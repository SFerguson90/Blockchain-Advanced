import subprocess, json, os

from dotenv import load_dotenv
from constants import *
from pprint import pprint
from bit import PrivateKeyTestnet, wif_to_key
from bit.network import NetworkAPI
from web3 import Web3, middleware, Account
from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3.middleware import geth_poa_middleware

load_dotenv()
mnemonic_phrase = os.getenv("MNEMONIC")
mnemonic = os.getenv('MNEMONIC', 'leader fiction balcony priority offer fix collect snap carry walnut element neglect')
fall_back_mnemonic = os.getenv('MNEMONIC', 'imitate injury board gaze shrimp assist pond yellow police hen hen gauge')

# Connecting to Web3
w3 = Web3(Web3.HTTPProvider(os.getenv('WEB3_PROVIDER', 'http://localhost:8545')))
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Accounts
account_one = "0x9Fbf91d40EF59de7e0dF1d7DD5eF8639E213ffb5"
account_two = "0xC391339E1EB2552d18B00c534B4ED9d5a3617ABA"

# Validate Running Blockchain and blockNumber
print(w3.eth.blockNumber)

# Validate Balance of Account_One
print(w3.eth.getBalance(account_one))

# Validate Balance of Account Two
print(w3.eth.getBalance(account_two))

# COINS
coins = {
    "ETH":derive_wallets(coin="ETH"),
    "BTCTEST":derive_wallets(coin="BTCTEST")
}

# WALLET PRIV KEYS
eth_wallets_privkeys = []
btc_wallets_privkeys = []

for wallet in coins["eth"]:
    eth_wallets_privkeys.append(wallet['privkey'])
for wallet in coins["btc-test"]:
    btc_wallets_privkeys.append(wallet['privkey'])

print("Ethereum Priv Key \n")
for eprivkey in eth_wallets_privkeys:
    print(f"{eprivkey} \n")

print("="*70, "\n")

print("BTC Priv Key \n")
for bprivkey in btc_wallets_privkeys:
    print(f"{bprivkey} \n")

# DEFINITIONS
# ------------------------------------------------------------------------
#
def derive_wallets(coin=BTC, mnemonic=mnemonic, depth=3):
    command = f"php derive -g --mnemonic={mnemonic} --coin={coin} --numderive={depth} --format=json"
    
    p = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        shell=True)
    
    (output, err) = p.communicate()
    p_status = p.wait()
    return json.loads(output)

def priv_key_to_account(coin, priv_key):
    
    if coin.upper() == "ETH":
        account = Account.from_key(priv_key)
    elif coin.upper() == "BTCTEST":
        account = wif_to_key(priv_key)
    return account

def create_tx(coin, account, recipient, amount):
    
    if coin.upper() == "ETH":
        
        gasEstimate = w3.eth.estimateGas({
            "from": account, "to": recipient, "value": int(amount)
            })

        return {
            'from': account,
            'to': recipient,
            'value': int(amount),
            'gas': gasEstimate,
            'gasPrice': w3.eth.gasPrice,
            'nonce': w3.eth.getTransactionCount(account)
            }
    
    if coin.upper() == "BTCTEST":
        
        return PrivateKeyTestnet.prepare_transaction(account,[(recipient,amount,BTC)])
    
    pass

def send_tx(coin, account, recipient, amount):
    
    raw_tx = create_tx(coin, account, recipient, amount)
    
    if coin.upper() == 'ETH':
            signed_tx = account.sign_transaction(raw_tx)
            result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
            result = w3.eth.getTransaction(result.hex())
    elif coin.upper() == 'BTCTEST': 
            signed_tx = account.sign_transaction(raw_tx)
            result = bit.network.NetworkAPI.broadcast_tx_testnet(signed_tx)
    
    return result


recipient = account_two
amount = int(12345)
coin = "BTCTEST"
priv_key = "cVAgDoahzo5Ucdv8ioxxubvmE6LfU3ZQgJ21UvY4eC1xi6WkvnXe" 
rec_key = "cUMUWn4yukMK41LpebaCmnbH26XCQn9EDoSK753FxSNxQC77i5TU"

# priv_key_to_account test
#btc_sender = 
btc_sender = priv_key_to_account(coin=coin,priv_key=priv_key).address
# OBJECT: <PrivateKeyTestnet: mtgb9hthmFpY1zidrYmZ24eTF87aBA147h>
# OBJECT.address: mtgb9hthmFpY1zidrYmZ24eTF87aBA147h

btc_receiver = priv_key_to_account(coin=coin,priv_key=rec_key).address
# OBJECT: <PrivateKeyTestnet: n2QTqdWK96XyJ7o8LXqoCjNbmtrFNFbNb6>
# OBJECT.address: n2QTqdWK96XyJ7o8LXqoCjNbmtrFNFbNb6

# Going to BTC-Test Faucet for coins, with which we can transfer & make tx

#----------------------------------------------------------------------
#testnet-faucet.mempool.co
#Transaction sent
#----------------------------------------------------------------------
#TxID: f3e3bdefb7f9fe671f87bde0267b6d7411ec9321db67b0864530bef4e809f10d
#Address: mtgb9hthmFpY1zidrYmZ24eTF87aBA147h
#Amount: 0.01
#----------------------------------------------------------------------


# create_tx test
#create_tx(coin=coin,account=btc_sender,recipient=account_two,amount=12345)

# send_tx test
#send_tx(coin=coin, account=btc_sender, recipient=account_two, amount=amount)