# core polymarket api
# https://github.com/Polymarket/py-clob-client/tree/main/examples

import os
import pdb
import time
import ast
import requests
import json

from dotenv import load_dotenv

from web3 import Web3
from web3.constants import MAX_INT
# Handle different web3 versions
try:
    from web3.middleware import geth_poa_middleware
except ImportError:
    # For newer web3 versions, geth_poa_middleware might not exist
    # We'll define a no-op middleware
    def geth_poa_middleware(make_request, web3):
        return make_request

import httpx
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from py_clob_client.constants import AMOY, POLYGON
from py_order_utils.builders import OrderBuilder
from py_order_utils.model import OrderData
from py_order_utils.signer import Signer
from py_clob_client.clob_types import (
    OrderArgs,
    MarketOrderArgs,
    OrderType,
    OrderBookSummary,
)
from py_clob_client.order_builder.constants import BUY

from agents.models.schemas import SimpleMarket, SimpleEvent
from colorama import Fore, Style

load_dotenv()


class Polymarket:
    def __init__(self):
        load_dotenv()
        self.dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
        
        # Configuración básica
        self.private_key = os.getenv("POLYGON_WALLET_PRIVATE_KEY")
        self.chain_id = POLYGON
        
        # URLs y endpoints
        self.clob_url = "https://clob.polymarket.com"
        self.gamma_url = "https://gamma-api.polymarket.com"
        self.gamma_markets_endpoint = f"{self.gamma_url}/markets"
        self.gamma_events_endpoint = f"{self.gamma_url}/events"
        self.polygon_rpc = "https://polygon-rpc.com"
        
        # Web3 setup
        self.w3 = Web3(Web3.HTTPProvider(self.polygon_rpc))
        try:
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        except TypeError:
            # For newer web3 versions that require different middleware setup
            pass
        
        # Wallet setup (optional for demo mode)
        try:
            self.wallet_address = self.get_address_for_private_key()
            print(f"Initialized wallet: {self.wallet_address}")
        except Exception as e:
            if self.dry_run:
                self.wallet_address = "demo_address"
                print(f"Warning: Using demo mode - {e}")
            else:
                raise
        
        # Contract addresses (usando checksum addresses)
        self.exchange_address = Web3.to_checksum_address("0x4bfb41d5b3570defd03c39a9a4d8de6bd8b8982e")
        self.neg_risk_exchange_address = Web3.to_checksum_address("0xC5d563A36AE78145C45a50134d48A1215220f80a")
        self.usdc_address = Web3.to_checksum_address("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174")  # USDC en Polygon
        
        # USDC contract setup
        self.usdc_abi = '''[
            {
                "constant": true,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": false,
                "inputs": [{"name": "_spender", "type": "address"},{"name": "_value", "type": "uint256"}],
                "name": "approve",
                "outputs": [{"name": "success", "type": "bool"}],
                "type": "function"
            },
            {
                "constant": true,
                "inputs": [{"name": "_owner", "type": "address"},{"name": "_spender", "type": "address"}],
                "name": "allowance",
                "outputs": [{"name": "remaining", "type": "uint256"}],
                "type": "function"
            }
        ]'''
        
        self.usdc = self.w3.eth.contract(
            address=self.usdc_address,
            abi=json.loads(self.usdc_abi)
        )
        
        # Initialize CLOB client (conditional based on wallet setup)
        if self.wallet_address != "demo_address":
            self.client = ClobClient(
                self.clob_url,
                key=self.private_key,
                chain_id=self.chain_id
            )
            
            # Set API credentials
            creds = ApiCreds(
                api_key=os.getenv("CLOB_API_KEY"),
                api_secret=os.getenv("CLOB_SECRET"),
                api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
            )
            self.client.set_api_creds(creds)
        else:
            self.client = None
            print("Warning: CLOB client not initialized - running in demo mode")

        self.erc20_approve = """[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"authorizer","type":"address"},{"indexed":true,"internalType":"bytes32","name":"nonce","type":"bytes32"}],"name":"AuthorizationCanceled","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"authorizer","type":"address"},{"indexed":true,"internalType":"bytes32","name":"nonce","type":"bytes32"}],"name":"AuthorizationUsed","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"account","type":"address"}],"name":"Blacklisted","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"userAddress","type":"address"},{"indexed":false,"internalType":"address payable","name":"relayerAddress","type":"address"},{"indexed":false,"internalType":"bytes","name":"functionSignature","type":"bytes"}],"name":"MetaTransactionExecuted","type":"event"},{"anonymous":false,"inputs":[],"name":"Pause","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"newRescuer","type":"address"}],"name":"RescuerChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"bytes32","name":"previousAdminRole","type":"bytes32"},{"indexed":true,"internalType":"bytes32","name":"newAdminRole","type":"bytes32"}],"name":"RoleAdminChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"address","name":"account","type":"address"},{"indexed":true,"internalType":"address","name":"sender","type":"address"}],"name":"RoleGranted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"address","name":"account","type":"address"},{"indexed":true,"internalType":"address","name":"sender","type":"address"}],"name":"RoleRevoked","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"account","type":"address"}],"name":"UnBlacklisted","type":"event"},{"anonymous":false,"inputs":[],"name":"Unpause","type":"event"},{"inputs":[],"name":"APPROVE_WITH_AUTHORIZATION_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"BLACKLISTER_ROLE","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"CANCEL_AUTHORIZATION_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"DECREASE_ALLOWANCE_WITH_AUTHORIZATION_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"DEFAULT_ADMIN_ROLE","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"DEPOSITOR_ROLE","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"DOMAIN_SEPARATOR","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"EIP712_VERSION","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"INCREASE_ALLOWANCE_WITH_AUTHORIZATION_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"META_TRANSACTION_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"PAUSER_ROLE","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"PERMIT_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"RESCUER_ROLE","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"TRANSFER_WITH_AUTHORIZATION_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"WITHDRAW_WITH_AUTHORIZATION_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"uint256","name":"validAfter","type":"uint256"},{"internalType":"uint256","name":"validBefore","type":"uint256"},{"internalType":"bytes32","name":"nonce","type":"bytes32"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"approveWithAuthorization","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"authorizer","type":"address"},{"internalType":"bytes32","name":"nonce","type":"bytes32"}],"name":"authorizationState","outputs":[{"internalType":"enum GasAbstraction.AuthorizationState","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"blacklist","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"blacklisters","outputs":[{"internalType":"address[]","name":"","type":"address[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"authorizer","type":"address"},{"internalType":"bytes32","name":"nonce","type":"bytes32"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"cancelAuthorization","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"decrement","type":"uint256"},{"internalType":"uint256","name":"validAfter","type":"uint256"},{"internalType":"uint256","name":"validBefore","type":"uint256"},{"internalType":"bytes32","name":"nonce","type":"bytes32"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"decreaseAllowanceWithAuthorization","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"},{"internalType":"bytes","name":"depositData","type":"bytes"}],"name":"deposit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"userAddress","type":"address"},{"internalType":"bytes","name":"functionSignature","type":"bytes"},{"internalType":"bytes32","name":"sigR","type":"bytes32"},{"internalType":"bytes32","name":"sigS","type":"bytes32"},{"internalType":"uint8","name":"sigV","type":"uint8"}],"name":"executeMetaTransaction","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"}],"name":"getRoleAdmin","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"uint256","name":"index","type":"uint256"}],"name":"getRoleMember","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"}],"name":"getRoleMemberCount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"grantRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"hasRole","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"increment","type":"uint256"},{"internalType":"uint256","name":"validAfter","type":"uint256"},{"internalType":"uint256","name":"validBefore","type":"uint256"},{"internalType":"bytes32","name":"nonce","type":"bytes32"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"increaseAllowanceWithAuthorization","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string","name":"newName","type":"string"},{"internalType":"string","name":"newSymbol","type":"string"},{"internalType":"uint8","name":"newDecimals","type":"uint8"},{"internalType":"address","name":"childChainManager","type":"address"}],"name":"initialize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"initialized","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"isBlacklisted","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"nonces","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pausers","outputs":[{"internalType":"address[]","name":"","type":"address[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"permit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"renounceRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract IERC20","name":"tokenContract","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"rescueERC20","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"rescuers","outputs":[{"internalType":"address[]","name":"","type":"address[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"revokeRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"uint256","name":"validAfter","type":"uint256"},{"internalType":"uint256","name":"validBefore","type":"uint256"},{"internalType":"bytes32","name":"nonce","type":"bytes32"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"transferWithAuthorization","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"unBlacklist","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"unpause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string","name":"newName","type":"string"},{"internalType":"string","name":"newSymbol","type":"string"}],"name":"updateMetadata","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"uint256","name":"validAfter","type":"uint256"},{"internalType":"uint256","name":"validBefore","type":"uint256"},{"internalType":"bytes32","name":"nonce","type":"bytes32"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"withdrawWithAuthorization","outputs":[],"stateMutability":"nonpayable","type":"function"}]"""
        self.erc1155_set_approval = """[{"inputs": [{ "internalType": "address", "name": "operator", "type": "address" },{ "internalType": "bool", "name": "approved", "type": "bool" }],"name": "setApprovalForAll","outputs": [],"stateMutability": "nonpayable","type": "function"}]"""

        self.usdc_address = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
        self.ctf_address = "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"

        self.web3 = Web3(Web3.HTTPProvider(self.polygon_rpc))
        try:
            self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        except TypeError:
            # For newer web3 versions that require different middleware setup
            pass

        self.usdc = self.web3.eth.contract(
            address=self.usdc_address, abi=self.erc20_approve
        )
        self.ctf = self.web3.eth.contract(
            address=self.ctf_address, abi=self.erc1155_set_approval
        )

        self._init_api_keys()
        self._init_approvals(False)

    def _init_api_keys(self) -> None:
        if self.wallet_address != "demo_address":
            self.client = ClobClient(
                self.clob_url, key=self.private_key, chain_id=self.chain_id
            )
            self.credentials = self.client.create_or_derive_api_creds()
            self.client.set_api_creds(self.credentials)
            # print(self.credentials)
        else:
            self.credentials = None
            print("Warning: API keys not initialized - running in demo mode")

    def _init_approvals(self, run: bool = False) -> None:
        if not run:
            return

        priv_key = self.private_key
        pub_key = self.get_address_for_private_key()
        chain_id = self.chain_id
        web3 = self.web3
        nonce = web3.eth.get_transaction_count(pub_key)
        usdc = self.usdc
        ctf = self.ctf

        # CTF Exchange
        raw_usdc_approve_txn = usdc.functions.approve(
            "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E", int(MAX_INT, 0)
        ).build_transaction({"chainId": chain_id, "from": pub_key, "nonce": nonce})
        signed_usdc_approve_tx = web3.eth.account.sign_transaction(
            raw_usdc_approve_txn, private_key=priv_key
        )
        send_usdc_approve_tx = web3.eth.send_raw_transaction(
            signed_usdc_approve_tx.raw_transaction
        )
        usdc_approve_tx_receipt = web3.eth.wait_for_transaction_receipt(
            send_usdc_approve_tx, 600
        )
        print(usdc_approve_tx_receipt)

        nonce = web3.eth.get_transaction_count(pub_key)

        raw_ctf_approval_txn = ctf.functions.setApprovalForAll(
            "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E", True
        ).build_transaction({"chainId": chain_id, "from": pub_key, "nonce": nonce})
        signed_ctf_approval_tx = web3.eth.account.sign_transaction(
            raw_ctf_approval_txn, private_key=priv_key
        )
        send_ctf_approval_tx = web3.eth.send_raw_transaction(
            signed_ctf_approval_tx.raw_transaction
        )
        ctf_approval_tx_receipt = web3.eth.wait_for_transaction_receipt(
            send_ctf_approval_tx, 600
        )
        print(ctf_approval_tx_receipt)

        nonce = web3.eth.get_transaction_count(pub_key)

        # Neg Risk CTF Exchange
        raw_usdc_approve_txn = usdc.functions.approve(
            "0xC5d563A36AE78145C45a50134d48A1215220f80a", int(MAX_INT, 0)
        ).build_transaction({"chainId": chain_id, "from": pub_key, "nonce": nonce})
        signed_usdc_approve_tx = web3.eth.account.sign_transaction(
            raw_usdc_approve_txn, private_key=priv_key
        )
        send_usdc_approve_tx = web3.eth.send_raw_transaction(
            signed_usdc_approve_tx.raw_transaction
        )
        usdc_approve_tx_receipt = web3.eth.wait_for_transaction_receipt(
            send_usdc_approve_tx, 600
        )
        print(usdc_approve_tx_receipt)

        nonce = web3.eth.get_transaction_count(pub_key)

        raw_ctf_approval_txn = ctf.functions.setApprovalForAll(
            "0xC5d563A36AE78145C45a50134d48A1215220f80a", True
        ).build_transaction({"chainId": chain_id, "from": pub_key, "nonce": nonce})
        signed_ctf_approval_tx = web3.eth.account.sign_transaction(
            raw_ctf_approval_txn, private_key=priv_key
        )
        send_ctf_approval_tx = web3.eth.send_raw_transaction(
            signed_ctf_approval_tx.raw_transaction
        )
        ctf_approval_tx_receipt = web3.eth.wait_for_transaction_receipt(
            send_ctf_approval_tx, 600
        )
        print(ctf_approval_tx_receipt)

        nonce = web3.eth.get_transaction_count(pub_key)

        # Neg Risk Adapter
        raw_usdc_approve_txn = usdc.functions.approve(
            "0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296", int(MAX_INT, 0)
        ).build_transaction({"chainId": chain_id, "from": pub_key, "nonce": nonce})
        signed_usdc_approve_tx = web3.eth.account.sign_transaction(
            raw_usdc_approve_txn, private_key=priv_key
        )
        send_usdc_approve_tx = web3.eth.send_raw_transaction(
            signed_usdc_approve_tx.raw_transaction
        )
        usdc_approve_tx_receipt = web3.eth.wait_for_transaction_receipt(
            send_usdc_approve_tx, 600
        )
        print(usdc_approve_tx_receipt)

        nonce = web3.eth.get_transaction_count(pub_key)

        raw_ctf_approval_txn = ctf.functions.setApprovalForAll(
            "0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296", True
        ).build_transaction({"chainId": chain_id, "from": pub_key, "nonce": nonce})
        signed_ctf_approval_tx = web3.eth.account.sign_transaction(
            raw_ctf_approval_txn, private_key=priv_key
        )
        send_ctf_approval_tx = web3.eth.send_raw_transaction(
            signed_ctf_approval_tx.raw_transaction
        )
        ctf_approval_tx_receipt = web3.eth.wait_for_transaction_receipt(
            send_ctf_approval_tx, 600
        )
        print(ctf_approval_tx_receipt)

    def get_all_markets(self) -> "list[SimpleMarket]":
        markets = []
        # Add query parameters to get only current, active markets
        params = {
            "active": "true",
            "closed": "false", 
            "archived": "false",
            "limit": 1000  # Increased to 1000 to get many more markets
        }
        res = httpx.get(self.gamma_markets_endpoint, params=params)
        if res.status_code == 200:
            from datetime import datetime, timezone
            current_time = datetime.now(timezone.utc)
            
            for market in res.json():
                try:
                    market_data = self.map_api_to_market(market)
                    
                    # Additional filter: check if market end date is in the future
                    end_date_str = market_data.get('end')
                    if end_date_str:
                        try:
                            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                            # Only include markets that haven't ended yet
                            if end_date > current_time:
                                markets.append(SimpleMarket(**market_data))
                        except Exception as date_error:
                            # If we can't parse the date, include it anyway (fallback)
                            markets.append(SimpleMarket(**market_data))
                    else:
                        # If no end date, include it
                        markets.append(SimpleMarket(**market_data))
                except Exception as e:
                    print(f"Error processing market: {e}")
                    pass
        return markets

    def filter_markets_for_trading(self, markets: "list[SimpleMarket]"):
        """Enhanced algorithm to select the best trading markets"""
        from datetime import datetime, timezone
        
        current_time = datetime.now(timezone.utc)
        featured_markets = []
        
        # Score each market based on multiple factors
        scored_markets = []
        for market in markets:
            if not market.active:
                continue
                
            score = 0
            
            # Factor 1: Spread quality (lower spread = better, max 30 points)
            if market.spread > 0:
                spread_score = max(0, 30 - (market.spread * 100))
                score += spread_score
            
            # Factor 2: Time sensitivity (markets ending soon get priority, max 25 points)
            try:
                end_date = datetime.fromisoformat(market.end.replace('Z', '+00:00'))
                days_remaining = (end_date - current_time).days
                if days_remaining > 0:
                    # Higher score for markets ending in 1-90 days
                    if 1 <= days_remaining <= 30:
                        score += 25
                    elif 31 <= days_remaining <= 90:
                        score += 20
                    elif 91 <= days_remaining <= 180:
                        score += 15
                    else:
                        score += 5
            except:
                score += 10  # Default if date parsing fails
            
            # Factor 3: Market size/importance (funded markets are better, max 20 points)
            if market.funded:
                score += 20
            
            # Factor 4: Question quality (longer, detailed questions = better, max 15 points)
            question_length = len(market.question)
            if question_length > 100:
                score += 15
            elif question_length > 50:
                score += 10
            else:
                score += 5
            
            # Factor 5: Minimum size requirements (max 10 points)
            if hasattr(market, 'rewardsMinSize') and market.rewardsMinSize:
                if market.rewardsMinSize >= 100:
                    score += 10
                elif market.rewardsMinSize >= 50:
                    score += 7
                else:
                    score += 3
            
            scored_markets.append((market, score))
        
        # Sort by score (highest first)
        scored_markets.sort(key=lambda x: x[1], reverse=True)
        
        # Select diverse markets across categories
        category_counts = {}
        max_per_category = 8  # Increased from 3 to 8 markets per category for more variety
        
        for market, score in scored_markets:
            category = self.detect_category(market.question)
            
            if category_counts.get(category, 0) < max_per_category:
                featured_markets.append(market)
                category_counts[category] = category_counts.get(category, 0) + 1
                
                # Stop when we have enough markets
                if len(featured_markets) >= 50:  # Increased from 20 to 50 for more variety
                    break
        
        return featured_markets

    def get_market(self, token_id: str) -> SimpleMarket:
        params = {"clob_token_ids": token_id}
        res = httpx.get(self.gamma_markets_endpoint, params=params)
        if res.status_code == 200:
            data = res.json()
            market = data[0]
            return self.map_api_to_market(market, token_id)

    def map_api_to_market(self, market, token_id: str = "") -> SimpleMarket:
        market = {
            "id": int(market.get("id", 0)),
            "question": market.get("question", ""),
            "end": market.get("endDate", market.get("end", "")),
            "description": market.get("description", ""),
            "active": market.get("active", True),
            # "deployed": market.get("deployed"),
            "funded": market.get("funded", True),
            "rewardsMinSize": float(market.get("rewardsMinSize", 0)),
            "rewardsMaxSpread": float(market.get("rewardsMaxSpread", 0)),
            # "volume": float(market.get("volume", 0)),
            "spread": float(market.get("spread", 0)),
            "outcomes": str(market.get("outcomes", [])),
            "outcome_prices": str(market.get("outcomePrices", market.get("outcome_prices", "[]"))),
            "clob_token_ids": str(market.get("clobTokenIds", market.get("clob_token_ids", ""))),
        }
        if token_id:
            market["clob_token_ids"] = token_id
        return market

    def get_all_events(self) -> "list[SimpleEvent]":
        """Get all events from Gamma API"""
        try:
            params = {
                "active": "true",
                "closed": "false",
                "archived": "false",
                "limit": "100",
                "order": "volume",
                "ascending": "false"
            }
            
            res = httpx.get(
                f"{self.gamma_url}/markets",
                params=params,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "Mozilla/5.0"
                },
                timeout=30.0
            )
            
            if res.status_code == 200:
                markets = res.json()
                if markets:
                    events = []
                    for market in markets:
                        if float(market.get("volume", 0)) > 10000:
                            event_data = {
                                "id": str(market.get("id")),
                                "title": market.get("question", ""),
                                "description": market.get("description", ""),
                                "markets": str(market.get("id", "")),
                                "metadata": {
                                    "question": market.get("question", ""),
                                    "markets": str(market.get("id", "")),
                                    "volume": float(market.get("volume", 0)),
                                    "featured": market.get("featured", False),
                                    "outcome_prices": market.get("outcomePrices", "[]"),
                                    "outcomes": market.get("outcomes", "[]")
                                }
                            }
                            events.append(SimpleEvent(**event_data))
                    
                    print(f"\nTop mercados por volumen total:")
                    for market in markets[:5]:
                        print(f"- {market.get('question')}: ${float(market.get('volume', 0)):,.2f}")
                    
                    return events
                
            return []
        except Exception as e:
            print(f"Error getting events: {e}")
            return []

    def get_all_tradeable_events(self) -> "list[SimpleEvent]":
        try:
            params = {
                "active": "true",
                "closed": "false",
                "archived": "false",
                "limit": "100",
                "order": "volume",
                "ascending": "false"
            }
            
            res = httpx.get(
                f"{self.gamma_url}/markets",
                params=params,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "Mozilla/5.0"
                },
                timeout=30.0
            )
            
            if res.status_code == 200:
                markets = res.json()
                if markets:
                    events = []
                    for market in markets:
                        # Solo considerar mercados con volumen significativo
                        if float(market.get("volume", 0)) > 10000:
                            event_data = {
                                "id": str(market.get("id")),  # Convertir a string
                                "title": market.get("question", ""),
                                "description": market.get("description", ""),
                                "markets": str(market.get("id", "")),
                                "metadata": {
                                    "question": market.get("question", ""),
                                    "markets": str(market.get("id", "")),
                                    "volume": float(market.get("volume", 0)),
                                    "featured": market.get("featured", False),
                                    "outcome_prices": market.get("outcomePrices", "[]"),
                                    "outcomes": market.get("outcome", "[]")
                                }
                            }
                            event = SimpleEvent(**event_data)
                            events.append(event)
                    
                    print(f"\nTop mercados por volumen total:")
                    for market in markets[:5]:
                        print(f"- {market.get('question')}: ${float(market.get('volume', 0)):,.2f}")
                    
                    return events
            return []
        except Exception as e:
            print(f"{Fore.RED}Error getting events: {str(e)}{Style.RESET_ALL}")
            return []

    def get_sampling_simplified_markets(self) -> "list[SimpleEvent]":
        markets = []
        raw_sampling_simplified_markets = self.client.get_sampling_simplified_markets()
        for raw_market in raw_sampling_simplified_markets["data"]:
            token_one_id = raw_market["tokens"][0]["token_id"]
            market = self.get_market(token_one_id)
            markets.append(market)
        return markets

    def get_orderbook(self, token_id: str) -> OrderBookSummary:
        return self.client.get_order_book(token_id)

    def get_orderbook_price(self, token_id: str) -> float:
        return float(self.client.get_price(token_id))

    def get_address_for_private_key(self):
        if not self.private_key or self.private_key == "your_wallet_private_key_here":
            raise ValueError("No valid private key configured")
        account = self.w3.eth.account.from_key(str(self.private_key))
        return account.address

    def build_order(
        self,
        market_token: str,
        amount: float,
        nonce: str = str(round(time.time())),  # for cancellations
        side: str = "BUY",
        expiration: str = "0",  # timestamp after which order expires
    ):
        signer = Signer(self.private_key)
        builder = OrderBuilder(self.exchange_address, self.chain_id, signer)

        buy = side == "BUY"
        side = 0 if buy else 1
        maker_amount = amount if buy else 0
        taker_amount = amount if not buy else 0
        order_data = OrderData(
            maker=self.get_address_for_private_key(),
            tokenId=market_token,
            makerAmount=maker_amount,
            takerAmount=taker_amount,
            feeRateBps="1",
            nonce=nonce,
            side=side,
            expiration=expiration,
        )
        order = builder.build_signed_order(order_data)
        return order

    def execute_order(self, price, size, side, token_id) -> str:
        return self.client.create_and_post_order(
            OrderArgs(price=price, size=size, side=side, token_id=token_id)
        )

    def get_token_balance(self, token_id: str) -> float:
        """Get balance of a specific outcome token"""
        try:
            # ERC1155 balance ABI
            erc1155_abi = '''[{
                "inputs": [
                    {"internalType": "address", "name": "account", "type": "address"},
                    {"internalType": "uint256", "name": "id", "type": "uint256"}
                ],
                "name": "balanceOf",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            }]'''
            
            # CTF token contract address
            ctf_address = Web3.to_checksum_address("0x4D97DCd97eC945f40cF65F87097ACe5EA0476045")
            
            # Create contract
            ctf = self.w3.eth.contract(address=ctf_address, abi=erc1155_abi)
            
            # Get balance
            balance = ctf.functions.balanceOf(self.wallet_address, int(token_id)).call()
            return float(balance)
            
        except Exception as e:
            print(f"Error getting token balance: {e}")
            return 0.0

    def execute_market_order(self, market, amount):
        try:
            # Obtener datos del mercado usando los atributos correctos
            token_ids = ast.literal_eval(market.clob_token_ids)  # Usar el atributo directamente
            
            # Si el trade dice SELL -> compramos NO
            # Si el trade dice BUY -> compramos YES
            if hasattr(market, 'trade') and market.trade.get('side') == "SELL":
                token_id = token_ids[0]  # Token NO
                position = "NO"
            else:
                token_id = token_ids[1]  # Token YES
                position = "YES"
            
            # Verificar si ya tenemos una posición
            current_balance = self.get_token_balance(token_id)
            if current_balance > 0:
                print(f"Already have position in this market: {current_balance} {position} tokens")
                return None
            
            # Obtener el precio actual del mercado
            market_price_resp = self.client.get_price(token_id, "SELL")
            market_price = float(market_price_resp.get("price", 0))
            print(f"Current market price for {position}: ${market_price}")
            
            # Obtener el orderbook para ver las órdenes disponibles
            orderbook = self.client.get_order_book(token_id)
            
            # Calcular el tamaño mínimo requerido en tokens
            min_size = 5.0  # Tamaño mínimo en tokens
            min_cost = min_size * market_price  # Costo mínimo en USDC
            
            print(f"Creating order for {position} position:")
            print(f"Token ID: {token_id}")
            print(f"Market price: ${market_price}")
            print(f"Minimum size: {min_size} tokens")
            print(f"Minimum cost: ${min_cost:.4f} USDC")
            
            # Crear orden usando OrderArgs
            order_args = OrderArgs(
                token_id=token_id,
                size=min_size,
                price=market_price,
                side=BUY  # Siempre compramos (YES o NO)
            )
            
            # Crear y firmar la orden
            signed_order = self.client.create_order(order_args)
            print("Signed order created:", signed_order)
            
            # Add delay to avoid rate limiting
            import time
            time.sleep(1)
            
            # Postear la orden
            resp = self.client.post_order(signed_order)
            print("Order response:", resp)
            print("Done!")
            
            if self.dry_run:
                print(f"\n{Fore.GREEN}🔍 DRY RUN: Order would be executed with these parameters:{Style.RESET_ALL}")
                print(f"   Token ID: {token_id}")
                print(f"   Position: {position}")
                print(f"   Size: {min_size} tokens")
                print(f"   Price: ${market_price}")
                print(f"   Total Cost: ${min_cost:.4f} USDC")
                return {"status": "simulated", "dry_run": True}
                
            return resp
            
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg and "cloudflare" in error_msg.lower():
                print(f"🚫 Cloudflare blocked the request. This usually means:")
                print("   1. Missing API credentials (CLOB_API_KEY, CLOB_SECRET, CLOB_PASS_PHRASE)")
                print("   2. Rate limiting - too many requests")
                print("   3. Your IP may be flagged for bot activity")
                print("   4. Need to verify account or complete KYC")
                print("   💡 Try setting up proper API credentials in your .env file")
            else:
                print(f"Error executing market order: {e}")
                print(f"Full error details: {str(e)}")
            return None

    def check_usdc_allowance(self) -> float:
        """Check how much USDC we've approved for spending"""
        try:
            allowance = self.usdc.functions.allowance(
                Web3.to_checksum_address(self.wallet_address),
                Web3.to_checksum_address(self.exchange_address)
            ).call()
            return float(allowance) / 1_000_000  # Convertir de wei a USDC
        except Exception as e:
            print(f"Error checking allowance: {e}")
            return 0.0

    def approve_usdc_spend(self, amount: float):
        """Approve USDC spending"""
        try:
            # Convertir el monto a la unidad correcta (6 decimales para USDC)
            amount_wei = int(amount * 1_000_000)  # Convertir a unidades USDC
            
            # Convertir direcciones a checksum
            exchange_address = Web3.to_checksum_address(self.exchange_address)
            wallet_address = Web3.to_checksum_address(self.wallet_address)
            
            print(f"Approving {amount} USDC ({amount_wei} wei) for {exchange_address}")
            
            # Construir la transacción de aprobación usando el contrato directamente
            approve_txn = self.usdc.functions.approve(
                exchange_address,
                amount_wei
            ).build_transaction({
                'from': wallet_address,
                'nonce': self.w3.eth.get_transaction_count(wallet_address),
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price,
                'chainId': self.chain_id
            })
            
            # Firmar la transacción
            signed_txn = self.w3.eth.account.sign_transaction(approve_txn, private_key=self.private_key)
            
            # Enviar la transacción - usar raw_transaction en lugar de rawTransaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            print(f"Approval transaction sent: {tx_hash.hex()}")
            
            # Esperar a que se confirme
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Approval confirmed in block: {receipt['blockNumber']}")
            
            # Verificar el nuevo allowance
            new_allowance = self.check_usdc_allowance()
            print(f"New allowance: ${new_allowance}")
            
            return True
            
        except Exception as e:
            print(f"Error approving USDC: {e}")
            print(f"Full error details: {str(e)}")
            import traceback
            print(f"Stack trace: {traceback.format_exc()}")
            return False

    def get_usdc_balance(self) -> float:
        """Get USDC balance for the current wallet"""
        try:
            # Verificar que la wallet está configurada
            if not self.wallet_address:
                print("Wallet address not configured")
                return 0.0
                
            # Obtener balance
            balance_res = self.usdc.functions.balanceOf(self.wallet_address).call()
            balance = float(balance_res) / 1_000_000  # USDC tiene 6 decimales
            
            print(f"Raw balance: {balance_res}")
            print(f"Wallet: {self.wallet_address}")
            print(f"USDC Contract: {self.usdc_address}")
            
            return balance
            
        except Exception as e:
            print(f"Error getting USDC balance: {e}")
            print(f"Wallet: {self.wallet_address}")
            return 0.0

    def get_outcome_token_balance(self, token_id: str) -> float:
        """Get outcome token balance for the current wallet"""
        try:
            # TODO: Implementar verificación de balance de tokens outcome usando el contrato ERC1155
            return 0.0
        except Exception as e:
            print(f"Error getting outcome token balance: {e}")
            return 0.0

    def check_outcome_token_allowance(self, token_id: str) -> float:
        """Check outcome token allowance"""
        try:
            # TODO: Implementar verificación de allowance de tokens outcome
            return 0.0
        except Exception as e:
            print(f"Error checking outcome token allowance: {e}")
            return 0.0

    def approve_outcome_token_spend(self, token_id: str, amount: float):
        """Approve outcome token spending"""
        try:
            # TODO: Implementar aprobación de gasto de tokens outcome
            return False
        except Exception as e:
            print(f"Error approving outcome token spend: {e}")
            return False

    def set_all_allowances(self):
        """Set all necessary allowances for trading"""
        try:
            print("Setting allowances for all contracts...")
            
            # Addresses
            ctf_address = Web3.to_checksum_address("0x4D97DCd97eC945f40cF65F87097ACe5EA0476045")
            exchange_address = Web3.to_checksum_address("0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E")
            neg_risk_exchange = Web3.to_checksum_address("0xC5d563A36AE78145C45a50134d48A1215220f80a")
            neg_risk_adapter = Web3.to_checksum_address("0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296")
            
            # ERC1155 approval ABI
            erc1155_abi = '''[{
                "inputs": [
                    {"internalType": "address", "name": "operator", "type": "address"},
                    {"internalType": "bool", "name": "approved", "type": "bool"}
                ],
                "name": "setApprovalForAll",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }]'''
            
            # Create CTF contract
            ctf = self.w3.eth.contract(address=ctf_address, abi=erc1155_abi)
            
            # Get current nonce
            nonce = self.w3.eth.get_transaction_count(self.wallet_address)
            
            # Approve USDC for all contracts
            for contract in [exchange_address, neg_risk_exchange, neg_risk_adapter]:
                print(f"\nApproving USDC for {contract}...")
                
                # Build USDC approval transaction
                approve_txn = self.usdc.functions.approve(
                    contract,
                    int(MAX_INT, 0)  # Approve maximum amount
                ).build_transaction({
                    'chainId': self.chain_id,
                    'from': self.wallet_address,
                    'nonce': nonce,
                    'gas': 100000,
                    'gasPrice': self.w3.eth.gas_price
                })
                
                # Sign and send transaction
                signed_txn = self.w3.eth.account.sign_transaction(approve_txn, private_key=self.private_key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                print(f"USDC approval confirmed in block {receipt['blockNumber']}")
                
                nonce += 1
                
                # Approve CTF tokens
                print(f"Approving CTF tokens for {contract}...")
                ctf_txn = ctf.functions.setApprovalForAll(
                    contract,
                    True
                ).build_transaction({
                    'chainId': self.chain_id,
                    'from': self.wallet_address,
                    'nonce': nonce,
                    'gas': 100000,
                    'gasPrice': self.w3.eth.gas_price
                })
                
                # Sign and send transaction
                signed_txn = self.w3.eth.account.sign_transaction(ctf_txn, private_key=self.private_key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                print(f"CTF approval confirmed in block {receipt['blockNumber']}")
                
                nonce += 1
            
            print("\nAll allowances set successfully!")
            return True
            
        except Exception as e:
            print(f"Error setting allowances: {e}")
            return False

    def get_pinned_markets(self) -> "list[SimpleEvent]":
        """Get pinned markets from Gamma API"""
        try:
            # Obtener mercados pinned usando el endpoint específico o un filtro
            params = {
                "pinned": True,
                "active": True,
                "closed": False
            }
            response = httpx.get(self.gamma_markets_endpoint, params=params)
            if response.status_code == 200:
                markets = response.json()
                return [SimpleEvent(**market) for market in markets]
            return []
        except Exception as e:
            print(f"Error getting pinned markets: {e}")
            return []

    def get_high_volume_markets(self, min_volume: float = 10000) -> "list[SimpleEvent]":
        """Get markets with volume above threshold"""
        events = self.get_all_events()
        return [
            event for event in events 
            if event.active and not event.closed 
            and float(event.volume) > min_volume
        ]

    def detect_category(self, question: str) -> str:
        """Enhanced market categorization with comprehensive keyword matching"""
        question = question.lower()
        
        # Comprehensive keyword sets for accurate categorization
        politics_keywords = [
            'election', 'president', 'presidential', 'vote', 'voting', 'congress', 'senate', 'senator',
            'minister', 'government', 'governor', 'mayor', 'politician', 'political', 'candidate',
            'fed', 'federal', 'rate', 'interest', 'chancellor', 'prime minister', 'biden', 'trump',
            'harris', 'desantis', 'republican', 'democrat', 'gop', 'party', 'campaign', 'debate',
            'poll', 'electoral', 'impeach', 'cabinet', 'white house', 'policy', 'law', 'legislation',
            'supreme court', 'justice', 'scotus', 'midterm', '2024', '2025', 'inauguration'
        ]
        
        sports_keywords = [
            'nba', 'nfl', 'mlb', 'nhl', 'soccer', 'football', 'basketball', 'baseball', 'hockey',
            'league', 'cup', 'championship', 'playoffs', 'win', 'wins', 'relegated', 'super bowl',
            'world cup', 'olympics', 'fifa', 'uefa', 'champions league', 'epl', 'premier league',
            'la liga', 'bundesliga', 'serie a', 'mvp', 'rookie', 'draft', 'trade', 'player',
            'team', 'coach', 'manager', 'season', 'finals', 'semifinal', 'quarterback', 'goal',
            'touchdown', 'home run', 'points', 'score', 'games', 'match', 'tournament', 'tennis',
            'golf', 'pga', 'masters', 'wimbledon', 'open', 'formula 1', 'f1', 'racing'
        ]
        
        crypto_keywords = [
            'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptocurrency', 'token', 'blockchain',
            'opensea', 'nft', 'defi', 'solana', 'sol', 'cardano', 'ada', 'dogecoin', 'doge',
            'binance', 'coinbase', 'exchange', 'wallet', 'mining', 'hash', 'altcoin', 'satoshi',
            'web3', 'dao', 'smart contract', 'yield', 'staking', 'liquidity', 'usd', 'usdc',
            'price', '$100', '$50', '$1000', 'coin', 'market cap', 'volume', 'trading'
        ]
        
        entertainment_keywords = [
            'movie', 'film', 'actor', 'actress', 'director', 'award', 'oscar', 'academy', 'golden globe',
            'emmy', 'grammy', 'song', 'album', 'artist', 'singer', 'show', 'tv', 'television',
            'streaming', 'netflix', 'disney', 'marvel', 'star wars', 'hollywood', 'box office',
            'celebrity', 'fame', 'concert', 'tour', 'music', 'video', 'youtube', 'tiktok',
            'instagram', 'social media', 'influencer', 'podcast', 'series', 'season', 'episode'
        ]
        
        tech_keywords = [
            'ai', 'artificial intelligence', 'openai', 'chatgpt', 'gpt', 'technology', 'software',
            'app', 'application', 'launch', 'google', 'apple', 'microsoft', 'meta', 'facebook',
            'amazon', 'tesla', 'elon musk', 'twitter', 'x.com', 'iphone', 'android', 'ios',
            'startup', 'ipo', 'stock', 'valuation', 'revenue', 'company', 'ceo', 'tech',
            'computer', 'robot', 'automation', 'cloud', 'data', 'internet', 'cyber', 'security'
        ]
        
        economy_keywords = [
            'economy', 'economic', 'recession', 'inflation', 'gdp', 'unemployment', 'jobs',
            'market', 'stock market', 'dow', 'nasdaq', 's&p', 'sp500', 'bear market', 'bull market',
            'interest rate', 'federal reserve', 'bank', 'banking', 'finance', 'financial',
            'dollar', 'euro', 'currency', 'trade', 'tariff', 'debt', 'deficit', 'budget'
        ]
        
        climate_keywords = [
            'climate', 'global warming', 'temperature', 'weather', 'hurricane', 'storm',
            'flood', 'drought', 'wildfire', 'carbon', 'emissions', 'renewable', 'solar',
            'wind', 'electric', 'ev', 'environment', 'green', 'sustainability'
        ]
        
        health_keywords = [
            'health', 'medical', 'disease', 'virus', 'vaccine', 'covid', 'pandemic',
            'hospital', 'doctor', 'medicine', 'drug', 'fda', 'approval', 'treatment',
            'cure', 'clinical', 'trial', 'study', 'research'
        ]
        
        # Check categories in order of specificity
        if any(keyword in question for keyword in politics_keywords):
            return 'politics'
        elif any(keyword in question for keyword in sports_keywords):
            return 'sports'
        elif any(keyword in question for keyword in crypto_keywords):
            return 'crypto'
        elif any(keyword in question for keyword in tech_keywords):
            return 'tech'
        elif any(keyword in question for keyword in entertainment_keywords):
            return 'entertainment'
        elif any(keyword in question for keyword in economy_keywords):
            return 'economy'
        elif any(keyword in question for keyword in climate_keywords):
            return 'climate'
        elif any(keyword in question for keyword in health_keywords):
            return 'health'
        else:
            return 'other'


def test():
    host = "https://clob.polymarket.com"
    key = os.getenv("POLYGON_WALLET_PRIVATE_KEY")
    print(key)
    chain_id = POLYGON

    # Create CLOB client and get/set API credentials
    client = ClobClient(host, key=key, chain_id=chain_id)
    client.set_api_creds(client.create_or_derive_api_creds())

    creds = ApiCreds(
        api_key=os.getenv("CLOB_API_KEY"),
        api_secret=os.getenv("CLOB_SECRET"),
        api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
    )
    chain_id = AMOY
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds)

    print(client.get_markets())
    print(client.get_simplified_markets())
    print(client.get_sampling_markets())
    print(client.get_sampling_simplified_markets())
    print(client.get_market("condition_id"))

    print("Done!")


def gamma():
    url = "https://gamma-com"
    markets_url = url + "/markets"
    res = httpx.get(markets_url)
    code = res.status_code
    if code == 200:
        markets: list[SimpleMarket] = []
        data = res.json()
        for market in data:
            try:
                market_data = {
                    "id": int(market.get("id", 0)),
                    "question": market.get("question", ""),
                    # "start": market.get('startDate'),
                    "end": market.get("endDate", market.get("end", "")),
                    "description": market.get("description", ""),
                    "active": market.get("active", True),
                    "deployed": market.get("deployed", True),
                    "funded": market.get("funded", True),
                    # "orderMinSize": float(market.get('orderMinSize', 0)) if market.get('orderMinSize') else 0,
                    # "orderPriceMinTickSize": float(market.get('orderPriceMinTickSize', 0)),
                    "rewardsMinSize": float(market.get("rewardsMinSize", 0)),
                    "rewardsMaxSpread": float(market.get("rewardsMaxSpread", 0)),
                    "volume": float(market.get("volume", 0)),
                    "spread": float(market.get("spread", 0)),
                    "outcome_a": str(market.get("outcomes", ["", ""])[0] if market.get("outcomes") else ""),
                    "outcome_b": str(market.get("outcomes", ["", ""])[1] if market.get("outcomes") and len(market.get("outcomes", [])) > 1 else ""),
                    "outcome_a_price": str(market.get("outcomePrices", [0, 0])[0] if market.get("outcomePrices") else 0),
                    "outcome_b_price": str(market.get("outcomePrices", [0, 0])[1] if market.get("outcomePrices") and len(market.get("outcomePrices", [])) > 1 else 0),
                }
                markets.append(SimpleMarket(**market_data))
            except Exception as err:
                print(f"error {err} for market {id}")
        pdb.set_trace()
    else:
        raise Exception()


def main():
    # auth()
    # test()
    # gamma()
    print(Polymarket().get_all_events())


if __name__ == "__main__":
    load_dotenv()

    p = Polymarket()

    # k = p.get_api_key()
    # m = p.get_sampling_simplified_markets()

    # print(m)
    # m = p.get_market('11015470973684177829729219287262166995141465048508201953575582100565462316088')

    # t = m[0]['token_id']
    # o = p.get_orderbook(t)
    # pdb.set_trace()

    """
    
    (Pdb) pprint(o)
            OrderBookSummary(
                market='0x26ee82bee2493a302d21283cb578f7e2fff2dd15743854f53034d12420863b55', 
                asset_id='11015470973684177829729219287262166995141465048508201953575582100565462316088', 
                bids=[OrderSummary(price='0.01', size='600005'), OrderSummary(price='0.02', size='200000'), ...
                asks=[OrderSummary(price='0.99', size='100000'), OrderSummary(price='0.98', size='200000'), ...
            )
    
    """

    # https://polygon-rpc.com

    test_market_token_id = (
        "101669189743438912873361127612589311253202068943959811456820079057046819967115"
    )
    test_market_data = p.get_market(test_market_token_id)

    # test_size = 0.0001
    test_size = 1
    test_side = BUY
    test_price = float(ast.literal_eval(test_market_data["outcome_prices"])[0])

    # order = p.execute_order(
    #    test_price,
    #    test_size,
    #    test_side,
    #    test_market_token_id,
    # )

    # order = p.execute_market_order(test_price, test_market_token_id)

    balance = p.get_usdc_balance()
