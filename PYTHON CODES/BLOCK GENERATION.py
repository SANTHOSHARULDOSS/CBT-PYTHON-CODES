"""
Experiment 3: Block Generation and Blockchain Generation
==========================================================
A complete professional implementation covering:

    OPTION 1 - Block Generation
        - Create a single standalone block
        - User enters transactions interactively
        - Block is mined with Proof of Work
        - Full block details displayed

    OPTION 2 - Blockchain Generation
        - Build a full chain of multiple blocks
        - Genesis block auto-created
        - Add transactions in batches per block
        - Mine each block and link to chain
        - Full chain visualization
        - Chain validation
        - Balance ledger
        - Tamper detection demo
        - Export to JSON

Modules Used:
    hashlib  (built-in)
    json     (built-in)
    time     (built-in)
    datetime (built-in)

No external installation required.
"""

import hashlib
import json
import time
from datetime import datetime


# ===========================================================================
# UTILITY FUNCTIONS
# ===========================================================================
def hline(char="-", width=72):
    return char * width


def print_header(title, width=64):
    print()
    print("+" + "=" * width + "+")
    print("|{:^{w}}|".format(title, w=width))
    print("+" + "=" * width + "+")


def print_subheader(title, width=64):
    print()
    print("+" + "-" * width + "+")
    print("|{:^{w}}|".format(title, w=width))
    print("+" + "-" * width + "+")


def print_info_box(rows, title="", width=68):
    """Print a bordered box with key-value rows."""
    print()
    if title:
        print("  +" + "-" * width + "+")
        print("  |{:^{w}}|".format(title, w=width))
        print("  +" + "-" * width + "+")
    else:
        print("  +" + "-" * width + "+")

    for label, value in rows:
        val_str = str(value)
        if len(val_str) > width - 24:
            # split long values across two lines
            print("  | {:<20} : {:<{vw}}|".format(
                label, val_str[:width - 24], vw=width - 24))
            remaining = val_str[width - 24:]
            while remaining:
                chunk = remaining[:width - 24]
                remaining = remaining[width - 24:]
                print("  | {:<20}   {:<{vw}}|".format("", chunk, vw=width - 24))
        else:
            print("  | {:<20} : {:<{vw}}|".format(label, val_str, vw=width - 24))

    print("  +" + "-" * width + "+")


def show_transaction_help():
    """Display how to enter transactions for beginners."""
    W = 68
    print()
    print("  +" + "-" * W + "+")
    print("  |{:^{w}}|".format("HOW TO ENTER TRANSACTIONS", w=W))
    print("  +" + "-" * W + "+")
    print("  |{:<{w}}|".format("", w=W))
    print("  |{:<{w}}|".format(
        "  Enter one transaction per line.", w=W))
    print("  |{:<{w}}|".format(
        "  Format:  <sender> <receiver> <amount>", w=W))
    print("  |{:<{w}}|".format("", w=W))
    print("  |{:<{w}}|".format("  EXAMPLES:", w=W))
    print("  |{:<{w}}|".format(
        "    Alice Bob 5.0", w=W))
    print("  |{:<{w}}|".format(
        "    Bob Charlie 2.5", w=W))
    print("  |{:<{w}}|".format(
        "    Charlie Dave 1.0", w=W))
    print("  |{:<{w}}|".format("", w=W))
    print("  |{:<{w}}|".format(
        "  Type 'done' when you have finished entering transactions.", w=W))
    print("  |{:<{w}}|".format(
        "  Minimum 1 transaction required per block.", w=W))
    print("  |{:<{w}}|".format("", w=W))
    print("  +" + "-" * W + "+")
    print()


def read_transactions_from_user():
    """
    Interactively read transactions from the user.
    Returns a list of transaction dicts.
    """
    show_transaction_help()
    transactions = []
    tx_number = 1

    while True:
        print("  Transaction #{} (or type 'done' to finish):".format(tx_number))
        line = input("    > ").strip()

        if line.lower() == "done":
            if len(transactions) == 0:
                print("\n  [ERROR] You must enter at least 1 transaction.")
                print("           Try again.\n")
                continue
            break

        if not line:
            print("    [WARNING] Empty input. Skipped.\n")
            continue

        parts = line.split()

        if len(parts) < 3:
            print("    [ERROR] Invalid format.")
            print("            Expected: <sender> <receiver> <amount>")
            print("            Example:  Alice Bob 5.0\n")
            continue

        sender = parts[0]
        receiver = parts[1]

        try:
            amount = float(parts[2])
        except ValueError:
            print("    [ERROR] Amount must be a number.")
            print("            You entered: '{}'\n".format(parts[2]))
            continue

        if amount <= 0:
            print("    [ERROR] Amount must be greater than 0.\n")
            continue

        tx = {
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tx_hash": hashlib.sha256(
                "{}{}{}{}".format(sender, receiver, amount, time.time()).encode()
            ).hexdigest()[:16],
        }

        transactions.append(tx)
        print("    [OK] {} --> {} : {} coins  [{}]".format(
            sender, receiver, amount, tx["tx_hash"]))
        print()
        tx_number += 1

    # Show summary
    print("\n  Transactions entered: {}".format(len(transactions)))
    print("  " + hline("-", 56))
    print("  {:<4} {:<12} {:<12} {:>10}".format(
        "No.", "Sender", "Receiver", "Amount"))
    print("  " + hline("-", 56))
    for i, tx in enumerate(transactions):
        print("  {:<4} {:<12} {:<12} {:>10.2f}".format(
            i + 1, tx["sender"], tx["receiver"], tx["amount"]))
    print("  " + hline("-", 56))

    return transactions


# ===========================================================================
# BLOCK CLASS
# ===========================================================================
class Block:
    """
    Represents a single block.

    Fields
    ------
    index          : position in chain (0 for standalone)
    timestamp      : creation time
    transactions   : list of transaction dicts
    previous_hash  : hash of preceding block (zeros for standalone/genesis)
    nonce          : proof-of-work counter
    merkle_root    : merkle root of transactions
    hash           : SHA-256 hash of this block
    mining_time    : seconds spent mining
    difficulty     : number of leading zeros required
    """

    def __init__(self, index, transactions, previous_hash, difficulty=4):
        self.index = index
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.difficulty = difficulty
        self.nonce = 0
        self.merkle_root = self._compute_merkle_root()
        self.hash = None
        self.mining_time = 0.0

    def _compute_merkle_root(self):
        if not self.transactions:
            return hashlib.sha256(b"empty").hexdigest()

        hashes = [
            hashlib.sha256(
                json.dumps(tx, sort_keys=True).encode()
            ).hexdigest()
            for tx in self.transactions
        ]

        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])
            hashes = [
                hashlib.sha256(
                    (hashes[i] + hashes[i + 1]).encode()
                ).hexdigest()
                for i in range(0, len(hashes), 2)
            ]
        return hashes[0]

    def compute_hash(self):
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "merkle_root": self.merkle_root,
            "nonce": self.nonce,
        }
        return hashlib.sha256(
            json.dumps(block_data, sort_keys=True).encode()
        ).hexdigest()

    def mine_block(self):
        target = "0" * self.difficulty
        start = time.time()
        attempts = 0

        print()
        print("  Mining Block #{} ...".format(self.index))
        print("  Difficulty : {}  |  Target prefix : '{}'".format(
            self.difficulty, target))
        print("  " + hline(".", 56))

        while True:
            self.hash = self.compute_hash()
            attempts += 1

            if attempts % 100000 == 0:
                print("    attempt {:>10,}  nonce {:>10,}  hash {}...".format(
                    attempts, self.nonce, self.hash[:20]))

            if self.hash.startswith(target):
                self.mining_time = time.time() - start
                print()
                print("  Block #{} mined successfully.".format(self.index))
                print("  " + hline("-", 56))
                print("  {:.<20} {}".format("Hash", self.hash))
                print("  {:.<20} {:,}".format("Nonce", self.nonce))
                print("  {:.<20} {:.4f} seconds".format("Time", self.mining_time))
                print("  {:.<20} {:,}".format("Attempts", attempts))
                print("  " + hline("-", 56))
                return self.hash

            self.nonce += 1

    def display(self):
        """Display full block details in bordered format."""
        W = 72
        is_genesis = (self.index == 0 and
                      self.previous_hash == "0" * 64 and
                      any(tx.get("sender") == "GENESIS"
                          for tx in self.transactions))
        label = "GENESIS BLOCK" if is_genesis else "BLOCK #{}".format(self.index)

        print()
        print("  +" + "=" * W + "+")
        print("  |{:^{w}}|".format(label, w=W))
        print("  +" + "=" * W + "+")

        fields = [
            ("Index", self.index),
            ("Timestamp", self.timestamp),
            ("Difficulty", self.difficulty),
            ("Nonce", "{:,}".format(self.nonce)),
            ("Mining Time", "{:.4f} seconds".format(self.mining_time)),
            ("Merkle Root", self.merkle_root),
            ("Previous Hash", self.previous_hash),
            ("Block Hash", self.hash),
            ("Transactions", len(self.transactions)),
        ]

        for label_text, value in fields:
            val_str = str(value)
            if len(val_str) > W - 22:
                print("  | {:<18} : {:<{vw}}|".format(
                    label_text, val_str[:W - 22], vw=W - 22))
                rest = val_str[W - 22:]
                while rest:
                    chunk = rest[:W - 22]
                    rest = rest[W - 22:]
                    print("  | {:<18}   {:<{vw}}|".format("", chunk, vw=W - 22))
            else:
                print("  | {:<18} : {:<{vw}}|".format(
                    label_text, val_str, vw=W - 22))

        print("  +" + "-" * W + "+")
        print("  |{:^{w}}|".format("TRANSACTION DETAILS", w=W))
        print("  +" + "-" * W + "+")

        # table header
        print("  | {:<4} {:<14} {:<14} {:>10} {:<{rw}}|".format(
            "No.", "Sender", "Receiver", "Amount", "TX Hash",
            rw=W - 48))
        print("  |" + "-" * W + "|")

        for i, tx in enumerate(self.transactions):
            sender = str(tx.get("sender", "N/A"))[:14]
            receiver = str(tx.get("receiver", "N/A"))[:14]
            amount = tx.get("amount", 0)
            tx_hash = str(tx.get("tx_hash", "N/A"))[:W - 48]
            print("  | {:<4} {:<14} {:<14} {:>10.2f} {:<{rw}}|".format(
                i + 1, sender, receiver, amount, tx_hash, rw=W - 48))

        print("  +" + "=" * W + "+")

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "merkle_root": self.merkle_root,
            "nonce": self.nonce,
            "hash": self.hash,
            "difficulty": self.difficulty,
            "mining_time": "{:.4f}s".format(self.mining_time),
        }


# ===========================================================================
# BLOCKCHAIN CLASS
# ===========================================================================
class Blockchain:
    """
    Full blockchain with mining, validation, balances, and export.
    """

    def __init__(self, difficulty=4, mining_reward=10.0):
        self.chain = []
        self.pending_transactions = []
        self.difficulty = difficulty
        self.mining_reward = mining_reward
        self.block_size_limit = 10

    def create_genesis_block(self):
        print("\n  Creating Genesis Block ...")
        genesis_tx = [{
            "sender": "GENESIS",
            "receiver": "NETWORK",
            "amount": 0,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tx_hash": "0000000000000000",
        }]
        genesis = Block(0, genesis_tx, "0" * 64, self.difficulty)
        genesis.mine_block()
        self.chain.append(genesis)
        return genesis

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, sender, receiver, amount):
        tx = {
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tx_hash": hashlib.sha256(
                "{}{}{}{}".format(sender, receiver, amount, time.time()).encode()
            ).hexdigest()[:16],
        }
        self.pending_transactions.append(tx)
        return tx

    def mine_pending_transactions(self, miner_address):
        if not self.pending_transactions:
            print("\n  [WARNING] No pending transactions to mine.")
            return None

        # mining reward
        reward_tx = {
            "sender": "MINING_REWARD",
            "receiver": miner_address,
            "amount": self.mining_reward,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tx_hash": "REWARD",
        }

        block_txs = self.pending_transactions[:self.block_size_limit]
        block_txs.append(reward_tx)
        self.pending_transactions = self.pending_transactions[self.block_size_limit:]

        new_block = Block(
            index=len(self.chain),
            transactions=block_txs,
            previous_hash=self.get_latest_block().hash,
            difficulty=self.difficulty,
        )
        new_block.mine_block()
        self.chain.append(new_block)

        print("  Mining reward of {} coins credited to '{}'.".format(
            self.mining_reward, miner_address))
        return new_block

    def is_chain_valid(self):
        print("\n  Validating blockchain integrity ...")
        print("  " + hline("-", 60))

        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]

            if curr.hash != curr.compute_hash():
                print("  Block #{}: FAILED -- hash mismatch (data tampered).".format(i))
                print("  " + hline("-", 60))
                print("  RESULT : CHAIN IS INVALID")
                return False

            if curr.previous_hash != prev.hash:
                print("  Block #{}: FAILED -- previous hash link broken.".format(i))
                print("  " + hline("-", 60))
                print("  RESULT : CHAIN IS INVALID")
                return False

            if not curr.hash.startswith("0" * curr.difficulty):
                print("  Block #{}: FAILED -- proof of work invalid.".format(i))
                print("  " + hline("-", 60))
                print("  RESULT : CHAIN IS INVALID")
                return False

            print("  Block #{}: OK".format(i))

        print("  " + hline("-", 60))
        print("  RESULT : CHAIN IS VALID  ({} blocks verified)".format(
            len(self.chain)))
        return True

    def get_balance(self, address):
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx["sender"] == address:
                    balance -= tx["amount"]
                if tx["receiver"] == address:
                    balance += tx["amount"]
        return balance

    def get_all_addresses(self):
        addresses = set()
        for block in self.chain:
            for tx in block.transactions:
                if tx["sender"] not in ("GENESIS", "MINING_REWARD"):
                    addresses.add(tx["sender"])
                if tx["receiver"] not in ("NETWORK",):
                    addresses.add(tx["receiver"])
        return sorted(addresses)

    def display_chain(self):
        W = 72

        print()
        print("+" + "=" * (W + 4) + "+")
        print("|{:^{w}}|".format("COMPLETE BLOCKCHAIN", w=W + 4))
        print("+" + "=" * (W + 4) + "+")

        for block in self.chain:
            block.display()
            if block.index < len(self.chain) - 1:
                print("  {:^{w}}".format("|", w=W))
                print("  {:^{w}}".format("| linked by hash", w=W))
                print("  {:^{w}}".format("V", w=W))

        # chain statistics
        total_tx = sum(len(b.transactions) for b in self.chain)
        total_time = sum(b.mining_time for b in self.chain)

        print()
        print_info_box([
            ("Total Blocks", len(self.chain)),
            ("Difficulty", self.difficulty),
            ("Mining Reward", "{} coins".format(self.mining_reward)),
            ("Pending TX", len(self.pending_transactions)),
            ("Total Transactions", total_tx),
            ("Total Mining Time", "{:.4f} seconds".format(total_time)),
        ], title="CHAIN STATISTICS")

    def display_balances(self):
        addresses = self.get_all_addresses()

        if not addresses:
            print("\n  No transactions found in chain.")
            return

        W = 42
        print()
        print("  +" + "-" * W + "+")
        print("  |{:^{w}}|".format("ACCOUNT BALANCES", w=W))
        print("  +" + "-" * W + "+")
        print("  | {:<20} {:>18} |".format("Address", "Balance"))
        print("  |" + "-" * W + "|")

        for addr in addresses:
            bal = self.get_balance(addr)
            print("  | {:<20} {:>14.2f} coins|".format(addr, bal))

        print("  +" + "-" * W + "+")

    def tamper_block(self, block_index, field_index, new_data):
        if block_index < 0 or block_index >= len(self.chain):
            print("  [ERROR] Block #{} does not exist.".format(block_index))
            return False

        block = self.chain[block_index]

        if field_index < 0 or field_index >= len(block.transactions):
            print("  [ERROR] Transaction index {} out of range.".format(field_index))
            return False

        original = block.transactions[field_index]
        print("\n  TAMPERING Block #{}, Transaction #{}".format(
            block_index, field_index))
        print("  " + hline("-", 56))
        print("  Original : {} --> {} : {} coins".format(
            original["sender"], original["receiver"], original["amount"]))
        block.transactions[field_index] = new_data
        print("  Tampered : {} --> {} : {} coins".format(
            new_data["sender"], new_data["receiver"], new_data["amount"]))
        print("  " + hline("-", 56))
        print("  Block hash is now inconsistent with stored data.")
        return True

    def export_to_json(self, filename="blockchain_export.json"):
        data = {
            "blockchain": [b.to_dict() for b in self.chain],
            "chain_length": len(self.chain),
            "difficulty": self.difficulty,
            "mining_reward": self.mining_reward,
            "export_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print("\n  Blockchain exported to : {}".format(filename))
        return filename


# ===========================================================================
# OPTION 1 : STANDALONE BLOCK GENERATION
# ===========================================================================
def option_block_generation():
    """Generate a single standalone block interactively."""

    print_header("BLOCK GENERATION")

    # difficulty
    print("\n  Set mining difficulty (number of leading zeros in hash).")
    print("  Recommended: 2 (fast), 4 (moderate), 5 (slow)")
    print()
    diff_input = input("  Enter difficulty (default 4) : ").strip()

    if diff_input.isdigit() and 1 <= int(diff_input) <= 8:
        difficulty = int(diff_input)
    else:
        difficulty = 4
        if diff_input:
            print("  [INFO] Invalid input. Using default difficulty 4.")
        else:
            print("  [INFO] Using default difficulty 4.")

    # transactions
    print_subheader("ENTER TRANSACTIONS FOR THE BLOCK")
    transactions = read_transactions_from_user()

    if not transactions:
        print("\n  [ERROR] No transactions entered. Aborting.")
        return

    confirm = input("\n  Mine this block with {} transactions? (y/n) : ".format(
        len(transactions))).strip().lower()

    if confirm not in ("y", "yes", ""):
        print("  Cancelled.")
        return

    # create and mine
    block = Block(
        index=0,
        transactions=transactions,
        previous_hash="0" * 64,
        difficulty=difficulty,
    )
    block.mine_block()

    # display
    print_subheader("MINED BLOCK DETAILS")
    block.display()

    print_info_box([
        ("Status", "Successfully Mined"),
        ("Transactions", len(transactions)),
        ("Difficulty", difficulty),
        ("Nonce", "{:,}".format(block.nonce)),
        ("Mining Time", "{:.4f} seconds".format(block.mining_time)),
        ("Block Hash", block.hash),
    ], title="BLOCK GENERATION SUMMARY")


# ===========================================================================
# OPTION 2 : FULL BLOCKCHAIN GENERATION
# ===========================================================================
def option_blockchain_generation():
    """Build a full blockchain interactively."""

    print_header("BLOCKCHAIN GENERATION")

    # configuration
    print("\n  Configure your blockchain before building.")
    print()

    diff_input = input("  Mining difficulty (default 4) : ").strip()
    if diff_input.isdigit() and 1 <= int(diff_input) <= 8:
        difficulty = int(diff_input)
    else:
        difficulty = 4
        print("  [INFO] Using default difficulty 4.")

    reward_input = input("  Mining reward per block (default 10.0) : ").strip()
    try:
        reward = float(reward_input) if reward_input else 10.0
    except ValueError:
        reward = 10.0
        print("  [INFO] Using default reward 10.0 coins.")

    miner = input("  Miner name / address (default 'Miner') : ").strip()
    if not miner:
        miner = "Miner"

    blocks_input = input("  Number of blocks to create (default 3) : ").strip()
    if blocks_input.isdigit() and 1 <= int(blocks_input) <= 20:
        num_blocks = int(blocks_input)
    else:
        num_blocks = 3
        if blocks_input:
            print("  [INFO] Invalid input. Using default 3 blocks.")
        else:
            print("  [INFO] Using default 3 blocks.")

    # confirm configuration
    print_info_box([
        ("Difficulty", difficulty),
        ("Mining Reward", "{} coins".format(reward)),
        ("Miner Address", miner),
        ("Blocks to Create", num_blocks),
    ], title="BLOCKCHAIN CONFIGURATION")

    confirm = input("\n  Start building blockchain? (y/n) : ").strip().lower()
    if confirm not in ("y", "yes", ""):
        print("  Cancelled.")
        return

    # initialize blockchain
    blockchain = Blockchain(difficulty=difficulty, mining_reward=reward)

    # Step 1 : Genesis
    print_subheader("STEP 1 : GENESIS BLOCK")
    blockchain.create_genesis_block()
    blockchain.chain[0].display()

    # Step 2..N : Build blocks
    for block_num in range(1, num_blocks + 1):
        print_subheader("BLOCK {}/{} : ENTER TRANSACTIONS".format(
            block_num, num_blocks))

        print("\n  You are adding transactions for Block #{}.".format(block_num))
        transactions = read_transactions_from_user()

        if not transactions:
            print("  [WARNING] No transactions. Skipping this block.")
            continue

        for tx in transactions:
            blockchain.add_transaction(tx["sender"], tx["receiver"], tx["amount"])

        print_subheader("MINING BLOCK #{}".format(len(blockchain.chain)))
        blockchain.mine_pending_transactions(miner)
        blockchain.chain[-1].display()

    # post-build menu
    while True:
        print()
        print("  +" + "-" * 60 + "+")
        print("  |{:^60}|".format("BLOCKCHAIN OPERATIONS"))
        print("  +" + "-" * 60 + "+")
        print("  |                                                            |")
        print("  |   [1]  Display Full Blockchain                             |")
        print("  |   [2]  Validate Chain Integrity                            |")
        print("  |   [3]  View Account Balances                               |")
        print("  |   [4]  Add More Transactions and Mine New Block            |")
        print("  |   [5]  Tamper Detection Demo                               |")
        print("  |   [6]  Export Blockchain to JSON                           |")
        print("  |   [0]  Return to Main Menu                                |")
        print("  |                                                            |")
        print("  +" + "-" * 60 + "+")

        sub_choice = input("\n  Enter choice (0-6) : ").strip()

        # -- display chain --
        if sub_choice == "1":
            blockchain.display_chain()

        # -- validate --
        elif sub_choice == "2":
            blockchain.is_chain_valid()

        # -- balances --
        elif sub_choice == "3":
            blockchain.display_balances()

        # -- add more blocks --
        elif sub_choice == "4":
            print_subheader("ADD TRANSACTIONS FOR NEW BLOCK")
            transactions = read_transactions_from_user()

            if not transactions:
                print("  [WARNING] No transactions entered.")
                continue

            for tx in transactions:
                blockchain.add_transaction(
                    tx["sender"], tx["receiver"], tx["amount"])

            blockchain.mine_pending_transactions(miner)
            blockchain.chain[-1].display()

        # -- tamper demo --
        elif sub_choice == "5":
            print("\n  TAMPER DETECTION DEMONSTRATION")
            print("  " + hline("-", 56))
            print("  This simulates an attacker modifying a transaction")
            print("  inside the chain. The validation will then fail.")
            print()

            print("  Blocks in chain:")
            for b in blockchain.chain:
                is_gen = (b.index == 0 and
                          any(tx.get("sender") == "GENESIS"
                              for tx in b.transactions))
                label = "Genesis" if is_gen else "Block #{}".format(b.index)
                print("    [{}]  {}  ({} transactions)".format(
                    b.index, label, len(b.transactions)))

            print()
            bi_input = input("  Which block to tamper? (index) : ").strip()

            if not bi_input.isdigit():
                print("  [ERROR] Enter a valid block index.")
                continue

            bi = int(bi_input)

            if bi < 0 or bi >= len(blockchain.chain):
                print("  [ERROR] Block #{} does not exist. Valid: 0 to {}".format(
                    bi, len(blockchain.chain) - 1))
                continue

            block = blockchain.chain[bi]
            print("\n  Transactions in Block #{}:".format(bi))
            for i, tx in enumerate(block.transactions):
                print("    [{}]  {} --> {} : {} coins".format(
                    i, tx["sender"], tx["receiver"], tx["amount"]))

            print()
            ti_input = input("  Which transaction to tamper? (index) : ").strip()

            if not ti_input.isdigit():
                print("  [ERROR] Enter a valid transaction index.")
                continue

            ti = int(ti_input)

            if ti < 0 or ti >= len(block.transactions):
                print("  [ERROR] Transaction #{} does not exist.".format(ti))
                continue

            print()
            print("  Enter the FAKE transaction details:")
            fake_sender = input("    Fake sender   : ").strip() or "HACKER"
            fake_receiver = input("    Fake receiver : ").strip() or "HACKER"
            fake_amount_input = input("    Fake amount   : ").strip()

            try:
                fake_amount = float(fake_amount_input) if fake_amount_input else 999999
            except ValueError:
                fake_amount = 999999

            fake_tx = {
                "sender": fake_sender,
                "receiver": fake_receiver,
                "amount": fake_amount,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tx_hash": "TAMPERED",
            }

            blockchain.tamper_block(bi, ti, fake_tx)

            print("\n  Now validating chain after tampering ...")
            blockchain.is_chain_valid()

        # -- export --
        elif sub_choice == "6":
            fname = input(
                "\n  Filename (default: blockchain_export.json) : ").strip()
            if not fname:
                fname = "blockchain_export.json"
            blockchain.export_to_json(fname)

        # -- exit --
        elif sub_choice == "0":
            print("\n  Returning to main menu.")
            break

        else:
            print("\n  [ERROR] Invalid choice. Enter a number from 0 to 6.")


# ===========================================================================
# MAIN MENU
# ===========================================================================
def main():
    W = 64
    print()
    print("+" + "=" * W + "+")
    print("|{:^{w}}|".format("EXPERIMENT 3", w=W))
    print("|{:^{w}}|".format("BLOCK GENERATION AND BLOCKCHAIN GENERATION", w=W))
    print("|{:^{w}}|".format("Cryptocurrency and Blockchain Lab", w=W))
    print("+" + "=" * W + "+")

    while True:
        print()
        print("+" + "-" * W + "+")
        print("|{:^{w}}|".format("MAIN MENU", w=W))
        print("+" + "-" * W + "+")
        print("|{:<{w}}|".format("", w=W))
        print("|{:<{w}}|".format(
            "   [1]  Block Generation", w=W))
        print("|{:<{w}}|".format(
            "        - Create a single standalone block", w=W))
        print("|{:<{w}}|".format(
            "        - Enter transactions, mine, and view result", w=W))
        print("|{:<{w}}|".format("", w=W))
        print("|{:<{w}}|".format(
            "   [2]  Blockchain Generation", w=W))
        print("|{:<{w}}|".format(
            "        - Build a full chain with multiple blocks", w=W))
        print("|{:<{w}}|".format(
            "        - Genesis block, mining, validation, balances", w=W))
        print("|{:<{w}}|".format(
            "        - Tamper detection, JSON export", w=W))
        print("|{:<{w}}|".format("", w=W))
        print("|{:<{w}}|".format(
            "   [0]  Exit", w=W))
        print("|{:<{w}}|".format("", w=W))
        print("+" + "-" * W + "+")

        choice = input("\n  Enter your choice (0, 1, or 2) : ").strip()

        if choice == "1":
            option_block_generation()

        elif choice == "2":
            option_blockchain_generation()

        elif choice == "0":
            print()
            print("+" + "=" * W + "+")
            print("|{:^{w}}|".format("PROGRAM TERMINATED", w=W))
            print("|{:^{w}}|".format("Thank you.", w=W))
            print("+" + "=" * W + "+")
            print()
            break

        else:
            print("\n  [ERROR] Invalid choice. Please enter 0, 1, or 2.")


if __name__ == "__main__":
    main()
