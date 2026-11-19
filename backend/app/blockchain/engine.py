"""Deterministic educational SHA-256 blockchain primitives."""
from __future__ import annotations
import hashlib, json, time, uuid
from dataclasses import dataclass, asdict
from typing import Any


def canonical(data: dict[str, Any]) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

@dataclass
class Transaction:
    id: str
    sender: str
    receiver: str
    amount: float
    description: str
    timestamp: float
    status: str = "pending"
    rejection_reason: str | None = None

    @classmethod
    def create(cls, sender: str, receiver: str, amount: float, description: str = "") -> "Transaction":
        payload = {"sender": sender, "receiver": receiver, "amount": amount, "description": description, "timestamp": time.time()}
        return cls(hashlib.sha256(canonical(payload)).hexdigest(), **payload)

@dataclass
class Block:
    index: int
    timestamp: float
    transactions: list[dict[str, Any]]
    previous_hash: str
    nonce: int
    hash: str
    difficulty: int
    miner_id: str

    def hash_payload(self) -> dict[str, Any]:
        data = asdict(self); data.pop("hash", None); return data

    def calculate_hash(self) -> str:
        return hashlib.sha256(canonical(self.hash_payload())).hexdigest()

    def mine(self, difficulty: int, cancelled=lambda: False, progress=lambda *_: None) -> tuple[int, str]:
        target = "0" * difficulty; nonce = 0; started = time.time()
        while not cancelled():
            self.nonce = nonce
            digest = self.calculate_hash()
            if digest.startswith(target):
                self.hash = digest; return nonce + 1, digest
            nonce += 1
            if nonce % 1000 == 0: progress(nonce, time.time() - started, digest)
        raise InterruptedError("Mining cancelled")

class Blockchain:
    def __init__(self, difficulty: int = 3):
        self.difficulty = max(1, min(6, int(difficulty)))
        self.chain: list[Block] = []
        self.pending: list[Transaction] = []
        self.accounts = {"alice": 1000.0, "bob": 750.0, "carol": 500.0, "dave": 300.0, "treasury": 5000.0}
        self.create_genesis()

    def create_genesis(self) -> None:
        if not self.chain:
            b = Block(0, time.time(), [{"allocation": self.accounts.copy()}], "0" * 64, 0, "", 0, "genesis")
            b.hash = b.calculate_hash(); self.chain.append(b)

    @property
    def height(self) -> int: return len(self.chain) - 1

    def balance(self, account: str) -> float:
        balance = self.accounts.get(account, 0.0)
        for tx in self.pending:
            if tx.sender == account: balance -= tx.amount
            if tx.receiver == account: balance += tx.amount
        return balance

    def add_transaction(self, sender: str, receiver: str, amount: float, description: str = "") -> Transaction:
        if amount <= 0: raise ValueError("Amount must be positive")
        if sender == receiver: raise ValueError("Sender and receiver must differ")
        if sender not in self.accounts or receiver not in self.accounts: raise ValueError("Unknown account")
        if self.balance(sender) + 1e-9 < amount: raise ValueError("Insufficient balance (including pending transfers)")
        tx = Transaction.create(sender, receiver, float(amount), description)
        self.pending.append(tx); return tx

    def mine_pending(self, miner_id: str = "miner-01", difficulty: int | None = None, cancelled=lambda: False, progress=lambda *_: None) -> tuple[Block, int, float]:
        if not self.pending: raise ValueError("No pending transactions to mine")
        diff = self.difficulty if difficulty is None else max(1, min(6, int(difficulty)))
        txs = [asdict(t) for t in self.pending]
        block = Block(len(self.chain), time.time(), txs, self.chain[-1].hash, 0, "", diff, miner_id)
        start = time.time(); attempts, _ = block.mine(diff, cancelled, progress); elapsed = max(time.time()-start, 1e-9)
        self.chain.append(block)
        for tx in self.pending:
            self.accounts[tx.sender] -= tx.amount; self.accounts[tx.receiver] += tx.amount; tx.status = "confirmed"
        self.pending.clear()
        return block, attempts, elapsed

    def validate(self, chain: list[Block] | None = None) -> dict[str, Any]:
        blocks = chain if chain is not None else self.chain
        for i, block in enumerate(blocks):
            if block.hash != block.calculate_hash(): return {"valid": False, "broken_at": i, "reason": "Hash mismatch"}
            if i and block.previous_hash != blocks[i-1].hash: return {"valid": False, "broken_at": i, "reason": "Previous hash link mismatch"}
            if i and not block.hash.startswith("0" * block.difficulty): return {"valid": False, "broken_at": i, "reason": "Proof of work does not meet difficulty"}
        return {"valid": True, "broken_at": None, "reason": "All block hashes and links are valid"}

    def tamper(self, index: int) -> tuple[list[Block], dict[str, Any]]:
        import copy
        sandbox = copy.deepcopy(self.chain)
        if index <= 0 or index >= len(sandbox): raise ValueError("Choose a non-genesis block")
        sandbox[index].transactions.append({"tampered": True, "note": "sandbox-only edit"})
        return sandbox, self.validate(sandbox)

    def export(self) -> dict[str, Any]:
        return {"chain": [asdict(b) for b in self.chain], "pending": [asdict(t) for t in self.pending], "accounts": self.accounts, "difficulty": self.difficulty}
