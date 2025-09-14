from typing import List, Set, Dict

def precision_at_k(pred: List[str], truth: Set[str], k: int) -> float:
    if k <= 0:
        return 0.0
    pred_k = pred[:k]
    hits = sum(1 for x in pred_k if x in truth)
    return hits / k

def average_precision_at_k(pred: List[str], truth: Set[str], k: int) -> float:
    if not truth:
        return 0.0
    ap = 0.0
    hits = 0
    for i, pid in enumerate(pred[:k], start=1):
        if pid in truth:
            hits += 1
            ap += hits / i
    return ap / min(len(truth), k)

def map_at_k(all_preds: Dict[str, List[str]], truth_sets: Dict[str, Set[str]], k: int) -> float:
    if not all_preds:
        return 0.0
    total = 0.0
    n = 0
    for pid, preds in all_preds.items():
        ap = average_precision_at_k(preds, truth_sets.get(pid, set()), k)
        total += ap
        n += 1
    return total / max(n,1)
