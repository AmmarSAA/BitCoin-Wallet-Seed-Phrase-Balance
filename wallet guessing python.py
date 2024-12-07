# This code is for Educational Purpose Only and should not be used for any malicious activity. 
# The code is written in Python and uses the bip_utils library to generate a BIP-39 seed phrase,
# derive a Bitcoin address from the seed phrase, check the Bitcoin balance using the Blockchain API, 
# and save the seed phrase and address if the wallet has any balance. 
# The script automates the process until a wallet with at least 1 BTC is found.

import os
import requests
from bip_utils import (
    Bip39SeedGenerator,
    Bip44,
    Bip44Coins,
    Bip39WordsNum,
    Bip39MnemonicGenerator,
    Bip44Changes,
)
import time


# Step 1: Generate a BIP-39 seed phrase
def generate_seed_phrase():
    mnemonic = Bip39MnemonicGenerator().FromWordsNumber(Bip39WordsNum.WORDS_NUM_12)
    return mnemonic


# Step 2: Derive a Bitcoin address from the seed phrase
def get_bitcoin_address(seed_phrase):
    # Generate the seed from the mnemonic
    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()

    # Create a Bip44 wallet for Bitcoin
    bip44_mst = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)

    # Derive the first receiving address (account 0, external chain, address index 0)
    bip44_acc = (
        bip44_mst.Purpose()
        .Coin()
        .Account(0)
        .Change(Bip44Changes.CHAIN_EXT)
        .AddressIndex(0)
    )

    # Get the address
    address = bip44_acc.PublicKey().ToAddress()
    return address


# Step 3: Check Bitcoin balance using Blockchain API
def check_btc_balance(address):
    url = f"https://blockchain.info/q/addressbalance/{address}?confirmations=6"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Will raise an HTTPError for bad responses (4xx or 5xx)
        balance_satoshis = int(response.text)
        balance_btc = balance_satoshis / 100000000  # Convert satoshis to BTC
        return balance_btc
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except requests.exceptions.RequestException as err:
        print(f"Error occurred: {err}")
    return 0  # Return 0 if any error occurs


# Step 4: Save the seed phrase and address if it has any balance
def save_seed_phrase(seed_phrase, address, balance_btc):
    folder_path = "Wallet_Phrases"

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Create a file with the address as the filename and save the seed phrase
    file_name = os.path.join(folder_path, f"{address}.txt")
    with open(file_name, "w") as file:
        file.write(f"Address: {address}\n")
        file.write(f"Balance: {balance_btc} BTC\n")
        file.write(f"Seed Phrase: {seed_phrase}\n")
    print(f"Seed phrase saved for wallet: {address} with {balance_btc} BTC.")


# Step 5: Automate the process until a wallet with 1 BTC is found
def automate_until_1_btc():
    while True:
        # Generate seed phrase
        seed_phrase = generate_seed_phrase()
        print(f"Generated Seed Phrase: {seed_phrase}")

        # Get the Bitcoin address from the seed phrase
        address = get_bitcoin_address(seed_phrase)
        print(f"Generated Bitcoin Address: {address}")

        # Check the wallet's balance
        balance_btc = check_btc_balance(address)
        print(f"Balance for {address}: {balance_btc} BTC")

        # If the wallet has any balance, save it
        if balance_btc > 0:
            save_seed_phrase(seed_phrase, address, balance_btc)

        # If the balance is 1 BTC or more, stop the script
        if balance_btc >= 1:
            print(
                f"Found wallet with at least 1 BTC! Address: {address}, Balance: {balance_btc} BTC"
            )
            break

        # Add a delay to avoid API rate limits
        time.sleep(2)  # Adjust the delay as needed to avoid overloading the API


# Run the automation until a wallet with 1 BTC is found
automate_until_1_btc()
