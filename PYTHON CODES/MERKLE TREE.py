"""
Experiment 1: Merkle Tree Generation
======================================
A Merkle Tree is a binary hash tree used in blockchain systems to
efficiently verify the integrity of large sets of data. Each leaf
node contains the hash of a transaction, and each internal node
contains the hash of its two child nodes.

Modules Used : hashlib (built-in)
No external installation required.
"""

import hashlib


# ---------------------------------------------------------------------------
# Node class
# ---------------------------------------------------------------------------
class MerkleNode:
    """Represents a single node in the Merkle Tree."""

    def __init__(self, left=None, right=None, data=None, hash_value=None):
        self.left = left
        self.right = right
        self.data = data
        if hash_value:
            self.hash = hash_value
        elif data:
            self.hash = self._compute_hash(data)
        else:
            self.hash = self._compute_hash(left.hash + right.hash)

    @staticmethod
    def _compute_hash(data):
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Tree class
# ---------------------------------------------------------------------------
class MerkleTree:
    """
    Builds a Merkle Tree from a list of transactions.

    Capabilities
    -------------
    - Build tree bottom-up from transaction list
    - Display tree structure level by level
    - Generate Merkle Proof for any transaction index
    - Verify a Merkle Proof against the root hash
    """

    def __init__(self, transactions):
        self.transactions = list(transactions)
        self.leaves = []
        self.levels = []
        self.root = None
        self._build_tree()

    def _build_tree(self):
        if not self.transactions:
            print("[WARNING] No transactions provided.")
            return

        self.leaves = [MerkleNode(data=tx) for tx in self.transactions]

        if len(self.leaves) % 2 == 1:
            self.leaves.append(MerkleNode(data=self.transactions[-1]))
            print("[INFO] Odd transaction count. Last transaction duplicated.")

        self.levels = [self.leaves[:]]
        current_level = self.leaves

        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = (
                    current_level[i + 1]
                    if i + 1 < len(current_level)
                    else current_level[i]
                )
                parent = MerkleNode(left=left, right=right)
                next_level.append(parent)

            if len(next_level) > 1 and len(next_level) % 2 == 1:
                next_level.append(
                    MerkleNode(left=next_level[-1], right=next_level[-1])
                )

            self.levels.append(next_level)
            current_level = next_level

        self.root = current_level[0]

    def get_root_hash(self):
        return self.root.hash if self.root else None

    def get_merkle_proof(self, index):
        if index >= len(self.transactions):
            return None

        proof = []
        current_index = index

        for level in self.levels[:-1]:
            is_right = current_index % 2 == 1
            pair_index = current_index - 1 if is_right else current_index + 1

            if pair_index < len(level):
                proof.append({
                    "hash": level[pair_index].hash,
                    "position": "left" if is_right else "right",
                })
            current_index //= 2

        return proof

    def verify_proof(self, transaction, proof, root_hash):
        current_hash = hashlib.sha256(transaction.encode("utf-8")).hexdigest()

        for step in proof:
            if step["position"] == "left":
                combined = step["hash"] + current_hash
            else:
                combined = current_hash + step["hash"]
            current_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()

        return current_hash == root_hash

    def display_tree(self):
        total_levels = len(self.levels)
        W = 78

        print()
        print("+" + "=" * W + "+")
        print("|{:^{w}}|".format("MERKLE TREE STRUCTURE", w=W))
        print("+" + "=" * W + "+")

        for level_idx in range(total_levels - 1, -1, -1):
            level = self.levels[level_idx]

            if level_idx == total_levels - 1:
                label = "ROOT"
            elif level_idx == 0:
                label = "LEAVES (Transactions)"
            else:
                label = "LEVEL {}".format(total_levels - 1 - level_idx)

            print("+" + "-" * W + "+")
            print("| {:<{w}}|".format(label, w=W - 1))
            print("+" + "-" * W + "+")

            for i, node in enumerate(level):
                short = node.hash[:20] + "..." + node.hash[-10:]
                if level_idx == 0 and node.data:
                    line = "  [{:>2}]  {}  <-- \"{}\"".format(i, short, node.data)
                elif level_idx == total_levels - 1:
                    line = "  [ROOT]  {}".format(node.hash)
                else:
                    line = "  [{:>2}]  {}".format(i, short)
                print("| {:<{w}}|".format(line, w=W - 1))

        print("+" + "=" * W + "+")
        print("| {:<{w}}|".format(
            "Merkle Root : " + self.root.hash, w=W - 1))
        print("| {:<{w}}|".format(
            "Total Levels: {}".format(total_levels), w=W - 1))
        print("| {:<{w}}|".format(
            "Transactions: {}".format(len(self.transactions)), w=W - 1))
        print("+" + "=" * W + "+")
        print()


# ---------------------------------------------------------------------------
# Helper : show sample entry format
# ---------------------------------------------------------------------------
def show_sample_entry():
    """Show a clear sample so users know exactly what to type."""
    W = 66
    print()
    print("+" + "-" * W + "+")
    print("|{:^{w}}|".format("HOW TO ENTER TRANSACTIONS", w=W))
    print("+" + "-" * W + "+")
    print("|                                                                  |")
    print("|  You need to enter transaction texts separated by commas.        |")
    print("|  Each transaction is just a short text describing a transfer.    |")
    print("|                                                                  |")
    print("|  SAMPLE INPUT:                                                   |")
    print("|  ----------------------------------------------------------------|")
    print("|  Alice pays Bob 5 BTC, Bob pays Charlie 2 BTC, Charlie pays 1   |")
    print("|                                                                  |")
    print("|  You can also type simple ones like:                             |")
    print("|  ----------------------------------------------------------------|")
    print("|  tx1, tx2, tx3, tx4                                              |")
    print("|                                                                  |")
    print("|  RULES:                                                          |")
    print("|    - Minimum 2 transactions required                             |")
    print("|    - Separate each transaction with a comma ( , )                |")
    print("|    - Each transaction can be any text you want                    |")
    print("|    - Spaces are allowed inside a transaction                     |")
    print("|                                                                  |")
    print("+" + "-" * W + "+")
    print()


# ---------------------------------------------------------------------------
# Main menu driven program
# ---------------------------------------------------------------------------
def main():
    W = 62
    print()
    print("+" + "=" * W + "+")
    print("|{:^{w}}|".format("EXPERIMENT 1 : MERKLE TREE GENERATION", w=W))
    print("|{:^{w}}|".format("Cryptocurrency and Blockchain Lab", w=W))
    print("+" + "=" * W + "+")

    tree = None  # will hold the current tree

    while True:
        print()
        print("+" + "-" * 60 + "+")
        print("|{:^60}|".format("MAIN MENU"))
        print("+" + "-" * 60 + "+")
        print("|                                                            |")
        print("|   [1]  Build Merkle Tree   (enter your own transactions)   |")
        print("|   [2]  Build with Sample   (auto-generated example)        |")
        print("|   [3]  Verify a Transaction (Merkle Proof)                 |")
        print("|   [4]  Tamper Detection Demo                               |")
        print("|   [5]  Display Current Tree                                |")
        print("|   [0]  Exit                                                |")
        print("|                                                            |")
        print("+" + "-" * 60 + "+")

        choice = input("\n  Enter your choice (0-5) : ").strip()

        # ==================================================================
        # OPTION 1 : Build tree from user input
        # ==================================================================
        if choice == "1":
            show_sample_entry()

            raw = input("  Type your transactions : ").strip()

            if not raw:
                print("\n  [ERROR] You did not type anything. Going back to menu.")
                continue

            transactions = [t.strip() for t in raw.split(",") if t.strip()]

            if len(transactions) < 2:
                print("\n  [ERROR] Minimum 2 transactions required.")
                print("           You entered only {}.".format(len(transactions)))
                print("           Tip: separate with commas like  tx1, tx2, tx3")
                continue

            print("\n  You entered {} transactions:".format(len(transactions)))
            print("  " + "-" * 50)
            for idx, tx in enumerate(transactions):
                print("    [{}]  {}".format(idx, tx))
            print("  " + "-" * 50)

            confirm = input("\n  Proceed to build tree? (y/n) : ").strip().lower()
            if confirm not in ("y", "yes", ""):
                print("  Cancelled. Returning to menu.")
                continue

            tree = MerkleTree(transactions)
            tree.display_tree()

        # ==================================================================
        # OPTION 2 : Build with auto sample
        # ==================================================================
        elif choice == "2":
            print("\n  Building Merkle Tree with sample transactions ...")
            print("  " + "-" * 50)

            sample_transactions = [
                "Alice pays Bob 5 BTC",
                "Bob pays Charlie 2 BTC",
                "Charlie pays Dave 1 BTC",
                "Dave pays Eve 3 BTC",
                "Eve pays Frank 0.5 BTC",
                "Frank pays Grace 1.5 BTC",
                "Grace pays Heidi 2 BTC",
                "Heidi pays Ivan 0.8 BTC",
            ]

            print("\n  Sample transactions loaded:")
            for idx, tx in enumerate(sample_transactions):
                print("    [{}]  {}".format(idx, tx))

            tree = MerkleTree(sample_transactions)
            tree.display_tree()

        # ==================================================================
        # OPTION 3 : Verify a transaction
        # ==================================================================
        elif choice == "3":
            if tree is None:
                print("\n  [ERROR] No tree built yet.")
                print("           Please choose option [1] or [2] first.")
                continue

            print("\n  Current transactions in the tree:")
            print("  " + "-" * 50)
            for idx, tx in enumerate(tree.transactions):
                print("    [{}]  {}".format(idx, tx))
            print("  " + "-" * 50)
            print()
            print("  Enter the INDEX NUMBER of the transaction to verify.")
            print("  Example: To verify \"{}\", type 0".format(tree.transactions[0]))
            print()

            idx_input = input("  Transaction index : ").strip()

            if not idx_input.isdigit():
                print("\n  [ERROR] Please enter a valid number.")
                continue

            tx_index = int(idx_input)

            if tx_index < 0 or tx_index >= len(tree.transactions):
                print("\n  [ERROR] Index out of range. Valid range: 0 to {}".format(
                    len(tree.transactions) - 1))
                continue

            proof = tree.get_merkle_proof(tx_index)
            root_hash = tree.get_root_hash()

            print()
            print("  +" + "-" * 64 + "+")
            print("  |{:^64}|".format("MERKLE PROOF RESULT"))
            print("  +" + "-" * 64 + "+")
            print("  | {:<63}|".format(
                "Transaction : \"{}\"".format(tree.transactions[tx_index])))
            print("  | {:<63}|".format(
                "Index       : {}".format(tx_index)))
            print("  | {:<63}|".format(""))
            print("  | {:<63}|".format("Proof Steps:"))

            for i, step in enumerate(proof):
                line = "  Step {} : {}...  [{}]".format(
                    i + 1, step["hash"][:28], step["position"])
                print("  | {:<63}|".format(line))

            is_valid = tree.verify_proof(
                tree.transactions[tx_index], proof, root_hash)
            print("  | {:<63}|".format(""))
            result_text = "VALID - Transaction is authentic" if is_valid \
                else "INVALID - Transaction may be tampered"
            print("  | {:<63}|".format("Verification : {}".format(result_text)))
            print("  +" + "-" * 64 + "+")

        # ==================================================================
        # OPTION 4 : Tamper detection demo
        # ==================================================================
        elif choice == "4":
            if tree is None:
                print("\n  [ERROR] No tree built yet.")
                print("           Please choose option [1] or [2] first.")
                continue

            print("\n  TAMPER DETECTION DEMO")
            print("  " + "-" * 50)
            print("  This will show what happens when someone tries to")
            print("  change a transaction after the tree is built.")
            print()
            print("  Current transactions:")
            for idx, tx in enumerate(tree.transactions):
                print("    [{}]  {}".format(idx, tx))
            print()

            idx_input = input("  Which transaction to tamper? (index) : ").strip()

            if not idx_input.isdigit():
                print("\n  [ERROR] Please enter a valid number.")
                continue

            tx_index = int(idx_input)

            if tx_index < 0 or tx_index >= len(tree.transactions):
                print("\n  [ERROR] Index out of range.")
                continue

            original = tree.transactions[tx_index]

            print()
            print("  Original transaction : \"{}\"".format(original))
            print()
            print("  Now type a FAKE/MODIFIED version of this transaction.")
            print("  Example: If original is \"Alice pays Bob 5 BTC\",")
            print("           you could type \"Alice pays Bob 500 BTC\"")
            print()

            tampered = input("  Enter tampered transaction : ").strip()

            if not tampered:
                print("\n  [ERROR] You did not type anything.")
                continue

            proof = tree.get_merkle_proof(tx_index)
            root_hash = tree.get_root_hash()

            is_valid_original = tree.verify_proof(original, proof, root_hash)
            is_valid_tampered = tree.verify_proof(tampered, proof, root_hash)

            print()
            print("  +" + "-" * 64 + "+")
            print("  |{:^64}|".format("TAMPER DETECTION RESULT"))
            print("  +" + "-" * 64 + "+")
            print("  | {:<63}|".format(
                "Original : \"{}\"".format(original)))
            print("  | {:<63}|".format(
                "Tampered : \"{}\"".format(tampered)))
            print("  | {:<63}|".format(""))
            print("  | {:<63}|".format(
                "Original verification : {}".format(
                    "VALID" if is_valid_original else "INVALID")))
            print("  | {:<63}|".format(
                "Tampered verification : {}".format(
                    "VALID" if is_valid_tampered else "INVALID -- TAMPER DETECTED")))
            print("  | {:<63}|".format(""))

            if not is_valid_tampered:
                print("  | {:<63}|".format(
                    "CONCLUSION: The blockchain detected the tampering."))
                print("  | {:<63}|".format(
                    "The Merkle Root does not match the modified data."))
            else:
                print("  | {:<63}|".format(
                    "WARNING: Same hash produced (identical input?)."))

            print("  +" + "-" * 64 + "+")

        # ==================================================================
        # OPTION 5 : Display current tree
        # ==================================================================
        elif choice == "5":
            if tree is None:
                print("\n  [ERROR] No tree built yet.")
                print("           Please choose option [1] or [2] first.")
                continue
            tree.display_tree()

        # ==================================================================
        # OPTION 0 : Exit
        # ==================================================================
        elif choice == "0":
            print("\n  Exiting. Goodbye.")
            break

        # ==================================================================
        # Invalid choice
        # ==================================================================
        else:
            print("\n  [ERROR] Invalid choice. Please enter a number from 0 to 5.")


if __name__ == "__main__":
    main()
