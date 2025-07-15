import sys
print("Running with:", sys.executable)
print("Search path:", sys.path, end="\n\n")

import os
from py_clob_client.client import ClobClient
from dotenv import load_dotenv

load_dotenv("keys.env")
host = "https://clob.polymarket.com"
key = os.getenv("PK")
client = ClobClient(host, key=key, chain_id=137)         # Polygon Mainnet
api_creds = client.create_or_derive_api_creds()           # POST /auth/api-key
print("API Key:", api_creds.api_key)
print("Secret:", api_creds.api_secret)
print("Passphrase:", api_creds.api_passphrase)