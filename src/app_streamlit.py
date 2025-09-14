import streamlit as st
import os
from typing import Dict, List, Set
import numpy as np
from collections import defaultdict

from data_loader import load_products
from text_clean import normalize_text
from shingling import char_k_shingles
from minhash_lsh import MinHasher, LSH, jaccard_from_sigs
from metrics import precision_at_k

st.set_page_config(page_title="Amazon Similar Products (LSH)", layout="wide")

st.title("Amazon Appliances — Similar Product Finder (LSH)")

data_path = st.text_input("Path to metadata (gz JSON lines)", value=r"C:\Users\Siddhesh\Desktop\GroupXY\data\meta_Appliances.json")
if not os.path.exists(data_path):
    st.warning("Please place the dataset at data/meta_Appliances.json or data/meta_Appliances.json.gz (or update the path above).")
    st.stop()


with st.spinner("Loading products..."):
    products = load_products(data_path)

st.success(f"Loaded {len(products)} products.")

# Exercise 1: Simple listing
st.header("Exercise 1: Product Listing")
search = st.text_input("Filter by substring (title)", value="")
max_rows = st.slider("Max products to show", 10, 500, 50, 10)

def product_card(p):
    st.markdown(f"**{p['asin']}** — {p['title']}")
    if p['description']:
        st.caption((p['description'][:240] + '...') if len(p['description'])>240 else p['description'])

count = 0
for asin, p in products.items():
    if search and search.lower() not in p['title'].lower():
        continue
    with st.container():
        product_card(p)
    count += 1
    if count >= max_rows:
        break

st.divider()
st.header("Exercise 2: Similar Products with PST / PSD / PSTD")

sim_mode = st.radio("Similarity function", ["PST (title)", "PSD (description)", "PSTD (hybrid)"], index=0, horizontal=True)
K = st.select_slider("K (char shingle size)", options=[2,3,5,7,10], value=5)
num_hashes = st.select_slider("# of MinHash functions", options=[10,20,50,100,150], value=100)
b = st.number_input("LSH bands (b)", min_value=1, value=20, step=1)
r = st.number_input("LSH rows per band (r) — must satisfy b*r = #hashes", min_value=1, value=5, step=1)
top_k = st.select_slider("Top-k to show", options=[5,10,20], value=10)

if b*r != num_hashes:
    st.error("Constraint violated: b * r must equal #hashes.")
    st.stop()

# Pick a product that has similar_item entries
candidates = [p for p in products.values() if p.get('similar_item')]
default_asin = candidates[0]['asin'] if candidates else next(iter(products.keys()))
asin_choice = st.text_input("Query ASIN", value=default_asin)

if asin_choice not in products:
    st.error("ASIN not found in loaded data.")
    st.stop()

# Build representations
def build_text(p, mode:str) -> str:
    if mode.startswith("PST "):
        return p['norm_title']
    elif mode.startswith("PSD "):
        return p['norm_desc']
    else:
        # hybrid: upweight title slightly by repeating once
        return (p['norm_title'] + " " + p['norm_title'] + " " + p['norm_desc']).strip()

def build_all_shingles(mode: str) -> Dict[str, set]:
    out = {}
    for asin, p in products.items():
        text = build_text(p, mode)
        out[asin] = char_k_shingles(text, K)
    return out

with st.spinner("Building shingles and MinHash signatures..."):
    shingle_map = build_all_shingles(sim_mode)
    mh = MinHasher(num_hashes)
    signatures = {asin: mh.signature(shs) for asin, shs in shingle_map.items()}
    lsh = LSH(bands=b, rows=r)
    index = lsh.index(signatures)

query_sig = signatures[asin_choice]
cand_ids = lsh.query_candidates(query_sig, index)
cand_ids.discard(asin_choice)

# Score candidates by MinHash-Jaccard
scores = []
for cid in cand_ids:
    sim = jaccard_from_sigs(query_sig, signatures[cid])
    scores.append((cid, sim))
scores.sort(key=lambda x: x[1], reverse=True)

top = scores[:top_k]

st.subheader("Query Product")
qp = products[asin_choice]
st.markdown(f"**{qp['asin']} — {qp['title']}**")
st.caption(qp['description'][:240] + ('...' if len(qp['description'])>240 else ''))

st.subheader("Top Matches")
for cid, sc in top:
    p = products[cid]
    st.markdown(f"- **{p['asin']} — {p['title']}**  Jaccard={sc:.3f}")


# Optional: precision@k vs ground-truth similar_item if available
truth = set(qp.get('similar_item', []))
if truth:
    prec = precision_at_k([cid for cid,_ in top], truth, k=top_k)
    st.info(f"precision@{top_k} vs given similar_item set: **{prec:.3f}** (|truth|={len(truth)})")
