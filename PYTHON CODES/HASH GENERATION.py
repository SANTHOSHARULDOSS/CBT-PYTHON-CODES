"""
Experiment 2: Universal Hash Generator
========================================
Generates cryptographic hashes for any input type:
    - Plain text / strings
    - Files of any format
    - Entire directories (recursive)
    - Existing hash values (double / chain hashing)

Supported algorithms:
    MD5, SHA-1, SHA-224, SHA-256, SHA-384, SHA-512,
    SHA3-256, SHA3-512, BLAKE2b, BLAKE2s

Modules Used:
    hashlib (built-in), os (built-in), json (built-in),
    tqdm (pip install tqdm), tabulate (pip install tabulate)
"""

import hashlib
import os
import json
import time
from pathlib import Path

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("[INFO] Install tqdm for progress bars : pip install tqdm")

try:
    from tabulate import tabulate
    TABULATE_AVAILABLE = True
except ImportError:
    TABULATE_AVAILABLE = False
    print("[INFO] Install tabulate for table output : pip install tabulate")


# ---------------------------------------------------------------------------
# Utility : formatted box printer
# ---------------------------------------------------------------------------
def print_box(title, rows, col_widths=None):
    """
    Print a bordered box with a title and key-value rows.
    rows : list of (label, value) tuples
    """
    max_label = max(len(r[0]) for r in rows) if rows else 10
    max_value = max(len(str(r[1])) for r in rows) if rows else 10
    inner = max(max_label + max_value + 5, len(title) + 4)

    border = "+" + "-" * (inner + 2) + "+"
    print()
    print(border)
    print("| {:<{w}} |".format(title, w=inner))
    print(border)
    for label, value in rows:
        line = "  {:<{lw}} : {}".format(label, value, lw=max_label)
        print("| {:<{w}} |".format(line, w=inner))
    print(border)
    print()


def print_table(headers, data):
    """Print a table using tabulate if available, else manual formatting."""
    if TABULATE_AVAILABLE:
        print(tabulate(data, headers=headers, tablefmt="grid"))
    else:
        # manual fallback
        col_w = []
        for i, h in enumerate(headers):
            w = len(h)
            for row in data:
                w = max(w, len(str(row[i])))
            col_w.append(w)

        sep = "+-" + "-+-".join("-" * w for w in col_w) + "-+"
        fmt = "| " + " | ".join("{:<" + str(w) + "}" for w in col_w) + " |"

        print(sep)
        print(fmt.format(*headers))
        print(sep)
        for row in data:
            print(fmt.format(*[str(c) for c in row]))
        print(sep)


# ---------------------------------------------------------------------------
# Core class
# ---------------------------------------------------------------------------
class UniversalHashGenerator:
    """
    Hash generator supporting multiple algorithms and input types.
    """

    SUPPORTED_ALGORITHMS = [
        "md5", "sha1", "sha224", "sha256", "sha384", "sha512",
        "sha3_256", "sha3_512", "blake2b", "blake2s",
    ]

    BUFFER_SIZE = 65536  # 64 KB

    def __init__(self, algorithm="sha256"):
        algo = algorithm.lower()
        if algo not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(
                "Unsupported algorithm: '{}'. Supported: {}".format(
                    algorithm, ", ".join(self.SUPPORTED_ALGORITHMS))
            )
        self.algorithm = algo

    def _get_hasher(self):
        return hashlib.new(self.algorithm)

    # -- 1. TEXT ------------------------------------------------------------
    def hash_text(self, text, encoding="utf-8"):
        hasher = self._get_hasher()
        raw = text.encode(encoding)
        hasher.update(raw)

        preview = text[:80] + ("..." if len(text) > 80 else "")
        return {
            "Input Type": "Text",
            "Input Preview": preview,
            "Algorithm": self.algorithm.upper(),
            "Hash Digest": hasher.hexdigest(),
            "Digest Length (bytes)": len(hasher.digest()),
            "Input Size (bytes)": len(raw),
        }

    # -- 2. FILE ------------------------------------------------------------
    def hash_file(self, filepath):
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError("File not found: {}".format(filepath))
        if not filepath.is_file():
            raise ValueError("Path is not a file: {}".format(filepath))

        file_size = filepath.stat().st_size
        hasher = self._get_hasher()

        if TQDM_AVAILABLE and file_size > 1_000_000:
            with open(filepath, "rb") as f:
                with tqdm(total=file_size, unit="B", unit_scale=True,
                          desc="  Hashing {}".format(filepath.name)) as pbar:
                    while True:
                        chunk = f.read(self.BUFFER_SIZE)
                        if not chunk:
                            break
                        hasher.update(chunk)
                        pbar.update(len(chunk))
        else:
            with open(filepath, "rb") as f:
                while True:
                    chunk = f.read(self.BUFFER_SIZE)
                    if not chunk:
                        break
                    hasher.update(chunk)

        return {
            "Input Type": "File",
            "File Name": filepath.name,
            "File Path": str(filepath.absolute()),
            "File Size": self._human_size(file_size),
            "Algorithm": self.algorithm.upper(),
            "Hash Digest": hasher.hexdigest(),
        }

    # -- 3. FOLDER ----------------------------------------------------------
    def hash_folder(self, folder_path, recursive=True):
        folder_path = Path(folder_path)
        if not folder_path.exists():
            raise FileNotFoundError("Folder not found: {}".format(folder_path))
        if not folder_path.is_dir():
            raise ValueError("Path is not a directory: {}".format(folder_path))

        if recursive:
            files = sorted(f for f in folder_path.rglob("*") if f.is_file())
        else:
            files = sorted(f for f in folder_path.glob("*") if f.is_file())

        print("\n  Folder   : {}".format(folder_path))
        print("  Files    : {}".format(len(files)))
        print("  Mode     : {}".format("Recursive" if recursive else "Top-level only"))

        combined_hasher = self._get_hasher()
        file_results = []

        for fpath in files:
            try:
                result = self.hash_file(fpath)
                rel = str(fpath.relative_to(folder_path))
                file_results.append((rel, result["Hash Digest"], result["File Size"]))
                combined_hasher.update(
                    (rel + result["Hash Digest"]).encode("utf-8")
                )
            except (PermissionError, OSError) as exc:
                rel = str(fpath.relative_to(folder_path))
                file_results.append((rel, "ERROR: {}".format(exc), "N/A"))

        return {
            "Input Type": "Folder",
            "Folder Path": str(folder_path.absolute()),
            "Total Files": len(files),
            "Algorithm": self.algorithm.upper(),
            "Folder Hash": combined_hasher.hexdigest(),
            "_file_details": file_results,
        }

    # -- 4. HASH OF HASH ----------------------------------------------------
    def hash_hash(self, input_hash, iterations=1):
        chain = [input_hash]
        current = input_hash

        for _ in range(iterations):
            hasher = self._get_hasher()
            hasher.update(current.encode("utf-8"))
            current = hasher.hexdigest()
            chain.append(current)

        return {
            "Input Type": "Hash-of-Hash",
            "Original Hash": input_hash,
            "Algorithm": self.algorithm.upper(),
            "Iterations": iterations,
            "Final Hash": current,
            "_chain": chain,
        }

    # -- 5. ALL ALGORITHMS --------------------------------------------------
    def hash_all_algorithms(self, text):
        results = []
        for algo in self.SUPPORTED_ALGORITHMS:
            h = hashlib.new(algo)
            h.update(text.encode("utf-8"))
            results.append((algo.upper(), h.hexdigest(), len(h.digest()) * 8))
        return results

    # -- utility ------------------------------------------------------------
    @staticmethod
    def _human_size(nbytes):
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if nbytes < 1024.0:
                return "{:.2f} {}".format(nbytes, unit)
            nbytes /= 1024.0
        return "{:.2f} PB".format(nbytes)

    # -- display helpers ----------------------------------------------------
    def display_result(self, result):
        """Pretty-print any result dictionary."""
        rows = []
        for key, val in result.items():
            if key.startswith("_"):
                continue
            rows.append((key, str(val)))

        print_box("HASH RESULT", rows)

        # file details table
        if "_file_details" in result and result["_file_details"]:
            print("  Per-File Hash Details:")
            table_data = []
            for rel, digest, size in result["_file_details"]:
                truncated = digest[:36] + "..." if len(digest) > 36 else digest
                table_data.append((rel, truncated, size))
            print_table(("File", "Hash (truncated)", "Size"), table_data)
            print()

        # hash chain
        if "_chain" in result:
            print("  Hash Chain:")
            print("  " + "-" * 76)
            for i, h in enumerate(result["_chain"]):
                label = "Input   " if i == 0 else "Round {:>2}".format(i)
                print("  {} --> {}".format(label, h))
            print("  " + "-" * 76)
            print()


# ---------------------------------------------------------------------------
# Interactive menu
# ---------------------------------------------------------------------------
def main():
    W = 62
    print()
    print("+" + "=" * W + "+")
    print("|{:^{w}}|".format("EXPERIMENT 2 : UNIVERSAL HASH GENERATOR", w=W))
    print("|{:^{w}}|".format("Cryptocurrency and Blockchain Lab", w=W))
    print("+" + "=" * W + "+")

    gen = UniversalHashGenerator("sha256")

    while True:
        print()
        print("+" + "-" * 56 + "+")
        print("|{:^56}|".format("MENU"))
        print("+" + "-" * 56 + "+")
        print("|  [1]  Hash a Text / String                            |")
        print("|  [2]  Hash a File                                     |")
        print("|  [3]  Hash a Folder / Directory                       |")
        print("|  [4]  Hash of a Hash  (double / chain hashing)        |")
        print("|  [5]  Compare ALL Algorithms on a Text                |")
        print("|  [6]  Change Algorithm  (current: {:<20})|".format(
            gen.algorithm.upper()))
        print("|  [0]  Exit                                            |")
        print("+" + "-" * 56 + "+")

        choice = input("  Enter choice : ").strip()

        if choice == "1":
            text = input("\n  Enter text to hash : ")
            result = gen.hash_text(text)
            gen.display_result(result)

        elif choice == "2":
            fpath = input("\n  Enter file path : ").strip().strip("\"'")
            try:
                result = gen.hash_file(fpath)
                gen.display_result(result)
            except (FileNotFoundError, ValueError) as exc:
                print("\n  [ERROR] {}".format(exc))

        elif choice == "3":
            folder = input("\n  Enter folder path : ").strip().strip("\"'")
            rec = input("  Include subfolders? (y/n, default y) : ").strip().lower()
            recursive = rec != "n"
            try:
                result = gen.hash_folder(folder, recursive)
                gen.display_result(result)
            except (FileNotFoundError, ValueError) as exc:
                print("\n  [ERROR] {}".format(exc))

        elif choice == "4":
            h = input("\n  Enter hash value to re-hash : ").strip()
            n = input("  Number of iterations (default 1) : ").strip()
            n = int(n) if n.isdigit() and int(n) > 0 else 1
            result = gen.hash_hash(h, n)
            gen.display_result(result)

        elif choice == "5":
            text = input("\n  Enter text : ")
            results = gen.hash_all_algorithms(text)
            preview = text[:50] + ("..." if len(text) > 50 else "")
            print('\n  All algorithm hashes for : "{}"'.format(preview))
            print_table(
                ("Algorithm", "Hash Digest", "Bits"),
                [(a, d, "{} bits".format(b)) for a, d, b in results],
            )
            print()

        elif choice == "6":
            print("\n  Available : {}".format(
                ", ".join(gen.SUPPORTED_ALGORITHMS)))
            algo = input("  Enter algorithm name : ").strip().lower()
            try:
                gen = UniversalHashGenerator(algo)
                print("  Algorithm changed to {}.".format(algo.upper()))
            except ValueError as exc:
                print("  [ERROR] {}".format(exc))

        elif choice == "0":
            print("\n  Exiting. Goodbye.")
            break

        else:
            print("\n  [WARNING] Invalid choice. Try again.")


if __name__ == "__main__":
    main()
