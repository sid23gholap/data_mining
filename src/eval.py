import argparse
from typing import Dict, List, Set, Tuple
import os
import pandas as pd
import numpy as np
from collections import Counter

from .data_loader import load_products
from .shingling import char_k_shingles
from .minhash_lsh import MinHasher, LSH, jaccard_from_sigs
from .metrics import map_at_k

def build_text(p: dict, mode: str) -> str:
    if mode == "PST":
        return p['norm_title']
    if mode == "PSD":
        return p['norm_desc']
    # PSTD hybrid
    return (p['norm_title'] + " " + p['norm_title'] + " " + p['norm_desc']).strip()

def eval_once(products: Dict[str,dict], mode: str, K: int, num_hashes: int, b: int, r: int, top_k: int, eval_ids: List[str]) -> float:
    # Shingles + signatures
    shingles = {asin: char_k_shingles(build_text(p, mode), K) for asin,p in products.items()}
    mh = MinHasher(num_hashes)
    sigs = {asin: mh.signature(sh) for asin, sh in shingles.items()}
    lsh = LSH(bands=b, rows=r)
    index = lsh.index(sigs)

    preds = {}
    truth_sets = {asin: set(products[asin].get('similar_item', [])) for asin in eval_ids}
    for q in eval_ids:
        qsig = sigs[q]
        cands = lsh.query_candidates(qsig, index)
        cands.discard(q)
        scored = [(cid, jaccard_from_sigs(qsig, sigs[cid])) for cid in cands]
        scored.sort(key=lambda x: x[1], reverse=True)
        preds[q] = [cid for cid,_ in scored[:top_k]]
    return map_at_k(preds, truth_sets, top_k)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="path to meta_Appliances.json.gz")
    ap.add_argument("--mode", choices=["PST","PSD","PSTD"], default="PSTD")
    ap.add_argument("--k_list", nargs="+", type=int, default=[2,3,5,7,10])
    ap.add_argument("--n_hash_list", nargs="+", type=int, default=[10,20,50,100,150])
    ap.add_argument("--b_list", nargs="+", type=int, default=[5,10,25,50])
    ap.add_argument("--r_list", nargs="+", type=int, default=[2,5,10])
    ap.add_argument("--top_k", type=int, default=10)
    ap.add_argument("--eval_size", type=int, default=100)
    ap.add_argument("--out_dir", default="reports")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    products = load_products(args.data)

    # Build evaluation set: top-N by number of similar_item
    counts = [(asin, len(p.get('similar_item', []))) for asin,p in products.items() if p.get('similar_item')]
    counts.sort(key=lambda x: x[1], reverse=True)
    eval_ids = [asin for asin,_ in counts[:args.eval_size]]

    if not eval_ids:
        print("No products with non-empty similar_item sets found in data.")
        return

    max_given = max(len(products[asin].get('similar_item', [])) for asin in eval_ids)
    min_given = min(len(products[asin].get('similar_item', [])) for asin in eval_ids)
    with open(os.path.join(args.out_dir, "eval_set_stats.txt"), "w") as f:
        f.write(f"Evaluation size: {len(eval_ids)}\n")
        f.write(f"Max given similar_item size: {max_given}\n")
        f.write(f"Min given similar_item size: {min_given}\n")

    # Sweep K
    rows = []
    fixed_hashes = 100 if 100 in args.n_hash_list else args.n_hash_list[-1]
    fixed_b, fixed_r = 20, fixed_hashes//20 if fixed_hashes%20==0 else (10, fixed_hashes//10)
    for K in args.k_list:
        if fixed_b * fixed_r != fixed_hashes:
            continue
        score = eval_once(products, args.mode, K, fixed_hashes, fixed_b, fixed_r, args.top_k, eval_ids)
        rows.append({"vary":"K","K":K,"num_hashes":fixed_hashes,"b":fixed_b,"r":fixed_r,"MAP@10":score})
    df_k = pd.DataFrame(rows)
    df_k.to_csv(os.path.join(args.out_dir, "map_by_K.csv"), index=False)

    # Sweep num_hashes
    rows = []
    fixed_K = 5 if 5 in args.k_list else args.k_list[0]
    for H in args.n_hash_list:
        # choose b,r so that b*r = H (simple factorization preference: r=5 if divisible)
        if H % 5 == 0:
            r = 5
            b = H // r
        else:
            r = 10 if H % 10 == 0 else 1
            b = H // r
        if b*r != H or b==0:
            continue
        score = eval_once(products, args.mode, fixed_K, H, b, r, args.top_k, eval_ids)
        rows.append({"vary":"hashes","K":fixed_K,"num_hashes":H,"b":b,"r":r,"MAP@10":score})
    df_h = pd.DataFrame(rows)
    df_h.to_csv(os.path.join(args.out_dir, "map_by_hashes.csv"), index=False)

    # Sweep (b,r) with fixed H
    rows = []
    H = fixed_hashes
    fixed_K = 5 if 5 in args.k_list else args.k_list[0]
    # enumerate factor pairs of H
    pairs = []
    for r in range(1, H+1):
        if H % r == 0:
            b = H // r
            pairs.append((b,r))
    for b,r in pairs:
        score = eval_once(products, args.mode, fixed_K, H, b, r, args.top_k, eval_ids)
        rows.append({"vary":"bands_rows","K":fixed_K,"num_hashes":H,"b":b,"r":r,"MAP@10":score})
    df_br = pd.DataFrame(rows)
    df_br.to_csv(os.path.join(args.out_dir, "map_by_b_r.csv"), index=False)

    print("Saved results to", args.out_dir)

if __name__ == "__main__":
    main()
