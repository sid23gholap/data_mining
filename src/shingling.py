from typing import Set

def char_k_shingles(s: str, k: int) -> Set[str]:
    if not s:
        return set()
    s = f"^{s}$"  # boundary markers to capture prefixes/suffixes
    if len(s) < k:
        return {s}
    return { s[i:i+k] for i in range(len(s)-k+1) }
