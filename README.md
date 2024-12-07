# **DISCLAIMER**

This Tutorial is for Educational Purpose Only and should not be used for any malicious activity.
The code is written in Python and uses the bip_utils library to generate a BIP-39 seed phrase,
derive a Bitcoin address from the seed phrase, check the Bitcoin balance using the Blockchain API,
and save the seed phrase and address if the wallet has any balance.
The script automates the process until a wallet with at least 1 BTC is found.

# **Tutorial: Automating Bitcoin Wallet Balance Check Using Python and Hosting it on AWS EC2**

In this tutorial, we will build a Python script that automatically generates Bitcoin wallets, checks their balances using a public API, and saves the seed phrases of wallets with any balance. The ultimate goal is to find a wallet with 1 Bitcoin (BTC). We'll cover the following steps:

1. Writing the Python script for Bitcoin wallet generation and balance checking.
2. Setting up a virtual environment.
3. Running the script locally.
4. Hosting the script on AWS EC2 for continuous operation using `tmux`.

---

## **Step 1: Writing the Python Script**

The core of this tutorial is a Python script that generates BIP-39 seed phrases, derives Bitcoin addresses, and checks the balance of these addresses using the Blockchain.info API. The final script is as follows:

```python
import os
import requests
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip39WordsNum, Bip39MnemonicGenerator, Bip44Changes
import time

# Step 1: Generate a BIP-39 seed phrase
def generate_seed_phrase():
    mnemonic = Bip39MnemonicGenerator().FromWordsNumber(Bip39WordsNum.WORDS_NUM_12)
    return mnemonic

# Step 2: Derive a Bitcoin address from the seed phrase
def get_bitcoin_address(seed_phrase):
    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
    bip44_mst = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
    bip44_acc = bip44_mst.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
    address = bip44_acc.PublicKey().ToAddress()
    return address

# Step 3: Check Bitcoin balance using Blockchain API
def check_btc_balance(address):
    url = f"https://blockchain.info/q/addressbalance/{address}?confirmations=6"
    try:
        response = requests.get(url)
        response.raise_for_status()
        balance_satoshis = int(response.text)
        balance_btc = balance_satoshis / 100000000  # Convert from satoshis to BTC
        return balance_btc
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except requests.exceptions.RequestException as err:
        print(f"Error occurred: {err}")
    return 0  # Return 0 if any error occurs

# Step 4: Save the seed phrase and address if it has any balance
def save_seed_phrase(seed_phrase, address, balance_btc):
    folder_path = 'Wallet_Phrases'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    file_name = os.path.join(folder_path, f"{address}.txt")
    with open(file_name, 'w') as file:
        file.write(f"Address: {address}
")
        file.write(f"Balance: {balance_btc} BTC
")
        file.write(f"Seed Phrase: {seed_phrase}
")
    print(f"Seed phrase saved for wallet: {address} with {balance_btc} BTC.")

# Step 5: Automate the process until a wallet with 1 BTC is found
def automate_until_1_btc():
    while True:
        seed_phrase = generate_seed_phrase()
        print(f"Generated Seed Phrase: {seed_phrase}")
        address = get_bitcoin_address(seed_phrase)
        print(f"Generated Bitcoin Address: {address}")
        balance_btc = check_btc_balance(address)
        print(f"Balance for {address}: {balance_btc} BTC")
        if balance_btc > 0:
            save_seed_phrase(seed_phrase, address, balance_btc)
        if balance_btc >= 1:
            print(f"Found wallet with at least 1 BTC! Address: {address}, Balance: {balance_btc} BTC")
            break
        time.sleep(2)

# Run the automation until a wallet with 1 BTC is found
automate_until_1_btc()
```

## **Step 2: Setting Up a Virtual Environment**

To avoid conflicts with system-wide Python packages, it's best to run the script inside a virtual environment.

1. **Install Python and Virtual Environment**:
   Make sure Python3 and `venv` are installed:
   ```bash
   sudo apt update
   sudo apt install python3 python3-venv
   ```

2. **Create a Virtual Environment**:
   Create a virtual environment named `myenv`:
   ```bash
   python3 -m venv myenv
   ```

3. **Activate the Virtual Environment**:
   Activate the environment:
   ```bash
   source myenv/bin/activate
   ```

4. **Install Dependencies**:
   Install the required Python libraries:
   ```bash
   pip install requests bip_utils
   ```

## **Step 3: Running the Script Locally**

You can now run the Python script by executing:

```bash
python wallet_script.py
```

Ensure the script is working correctly by testing the address generation and balance checking.

## **Step 4: Hosting the Script on AWS EC2**

To keep the script running indefinitely and ensure it can continue to check Bitcoin wallet balances, you can host it on an AWS EC2 instance.

1. **Launch an AWS EC2 Instance**:
   - Go to the AWS EC2 console and launch a new instance.
   - Choose an Amazon Machine Image (AMI) with Ubuntu Server.
   - Select an appropriate instance type (e.g., t2.micro).
   - Configure security group rules to allow SSH access.

2. **SSH into the EC2 Instance**:
   Use your terminal to connect to the EC2 instance via SSH:
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-public-ip
   ```

3. **Install Python and Virtual Environment on EC2**:
   Similar to Step 2, install Python and set up a virtual environment on the EC2 instance:
   ```bash
   sudo apt update
   sudo apt install python3 python3-venv
   python3 -m venv myenv
   source myenv/bin/activate
   ```

4. **Transfer Script to EC2**:
   Upload your Python script to the EC2 instance. Use `scp` to transfer the file from your local machine to the EC2 instance:
   ```bash
   scp -i your-key.pem wallet_script.py ubuntu@your-ec2-public-ip:/home/ubuntu/
   ```

5. **Install Dependencies and Run the Script**:
   Install the necessary libraries on EC2:
   ```bash
   pip install requests bip_utils
   python wallet_script.py
   ```

## **Step 5: Keeping the Script Running with `tmux`**

Since the EC2 instance will disconnect your session when you exit, you need a way to keep the script running in the background. `tmux` is a terminal multiplexer that allows you to keep processes running even after logging out.

1. **Install `tmux`**:
   ```bash
   sudo apt install tmux
   ```

2. **Start a New `tmux` Session**:
   ```bash
   tmux new -s wallet_checker
   ```

3. **Run the Script Inside the `tmux` Session**:
   Activate the virtual environment and run the Python script:
   ```bash
   source myenv/bin/activate
   python wallet_script.py > output.log 2>&1
   ```

4. **Detach from the `tmux` Session**:
   Detach from the session without stopping the script:
   ```bash
   Ctrl+b, then press d
   ```

You can later reattach the session using:
```bash
tmux attach -t wallet_checker
```

## **Step 6: Monitoring and Log Files**

You can monitor the output of the script by checking the `output.log` file:

```bash
cat output.log
```

---

## **Conclusion**

In this tutorial, we built a Python script to generate Bitcoin wallets and check balances using a public API. We then hosted it on AWS EC2 and ensured that it runs continuously using `tmux`. By following this step-by-step guide, you now have a powerful script running autonomously to search for Bitcoin balances.

