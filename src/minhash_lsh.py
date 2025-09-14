import random
import math
from typing import List, Dict, Tuple, Iterable, Set, DefaultDict
from collections import defaultdict
import numpy as np

class MinHasher:
    def __init__(self, num_hashes: int, seed: int = 42):
        self.num_hashes = num_hashes
        self.seed = seed
        random.seed(seed)
        # Universal hashing: h(x) = (a*x + b) mod p mod m
        # We map shingles to integers using Python's built-in hash (stable within session not guaranteed),
        # so we further mask to positive and mod a large prime.
        self.p = 2_147_483_647  # large prime
        self.a = np.array([random.randrange(1, self.p-1) for _ in range(num_hashes)], dtype=np.int64)
        self.b = np.array([random.randrange(0, self.p-1) for _ in range(num_hashes)], dtype=np.int64)

    def _hash_token(self, token: str) -> int:
        # stable-ish mapping to non-negative 64-bit
        return (hash(token) & 0x7FFFFFFFFFFFFFFF) % self.p

    def signature(self, shingles: Set[str]) -> np.ndarray:
        if not shingles:
            return np.full(self.num_hashes, fill_value=self.p, dtype=np.int64)
        vals = np.array([self._hash_token(t) for t in shingles], dtype=np.int64)
        # For each hash function, compute min over tokens
        # sig[i] = min( (a[i]*x + b[i]) mod p for x in vals )
        av = (self.a.reshape(-1,1) * vals.reshape(1,-1)) % self.p
        avb = (av + self.b.reshape(-1,1)) % self.p
        sig = avb.min(axis=1)
        return sig

def jaccard_from_sigs(sig1: np.ndarray, sig2: np.ndarray) -> float:
    return float(np.mean(sig1 == sig2))

class LSH:
    def __init__(self, bands: int, rows: int):
        assert bands > 0 and rows > 0
        self.b = bands
        self.r = rows

    def index(self, signatures: Dict[str, np.ndarray]) -> Dict[Tuple[int, int], List[str]]:
        # key: (band, bucket) -> list of ids
        buckets: DefaultDict[Tuple[int,int], List[str]] = defaultdict(list)
        for pid, sig in signatures.items():
            for band in range(self.b):
                start = band * self.r
                end = start + self.r
                band_slice = tuple(sig[start:end].tolist())
                bucket = hash(band_slice)
                buckets[(band, bucket)].append(pid)
        return buckets

    def query_candidates(self, sig: np.ndarray, buckets_index: Dict[Tuple[int,int], List[str]]) -> Set[str]:
        cands: Set[str] = set()
        for band in range(self.b):
            start = band * self.r
            end = start + self.r
            band_slice = tuple(sig[start:end].tolist())
            bucket = hash(band_slice)
            cands.update(buckets_index.get((band, bucket), []))
        return cands
