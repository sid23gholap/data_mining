# GroupXY — LSH-based Similar Product Finder (Amazon Appliances)

This repo contains a minimal, *ready-to-run* implementation that uses **character shingles → MinHash → LSH** to find similar Amazon products by title/description.

## Dataset
Use the **Appliances** metadata (2018) from the Amazon dataset:
- Landing: https://cseweb.ucsd.edu/~jmcauley/datasets/amazon_v2/
- Download metadata JSON (e.g., `meta_Appliances.json.gz`)

Place the downloaded file at: `data/meta_Appliances.json.gz` (create the `data/` folder).

> ⚠️ Do **not** include the dataset in your submission zip.

## Quickstart

```bash
# 1) Create env and install deps
pip install -r requirements.txt

# 2) Run the Streamlit app (UI for Exercise 1 & 2)
streamlit run src/app_streamlit.py
```

- The app lists products (Exercise 1) and lets you pick a product and search similar ones using:
  - **PST** (title only)
  - **PSD** (description only)
  - **PSTD** (title + description hybrid)
- You can change **K (shingle size)**, **#hashes**, and **LSH b, r**. The app shows **Top-k** results.

```bash
# 3) Run the evaluation (Exercise 3)
python src/eval.py --data data/meta_Appliances.json.gz   --k_list 2 3 5 7 10   --n_hash_list 10 20 50 100 150   --b_list 5 10 25 50   --r_list 2 5 10   --top_k 10   --eval_size 100
```

The evaluation script will:
- Build an **evaluation set** of the top-100 products with the largest `similar_item` lists.
- Report **MAP@10** while sweeping the specified hyperparameters.
- Save CSVs and plots in `reports/`.

## Deliverables
- **Part A**: Submit a single zip with **source only** (no dataset nor dependency wheels). Use the name `GroupXY.zip`.
- **Part B**: Submit `GroupXY.pdf` (report). See `reports/GroupXY_report_template.md` and export to PDF.

## Code Structure
```
src/
  app_streamlit.py        # Streamlit UI (Exercises 1 & 2)
  data_loader.py          # Gzip JSON loader + cleaning
  text_clean.py           # HTML stripping, normalization
  shingling.py            # Char-shingles
  minhash_lsh.py          # MinHash + LSH
  metrics.py              # Precision@k, MAP@k
  eval.py                 # Exercise 3 experiments
reports/
  GroupXY_report_template.md
requirements.txt
README.md
```

## Notes
- We use **character shingles** + **Jaccard** approximated by **MinHash**. LSH buckets speed up candidate generation.
- PSTD (hybrid) concatenates `title` and repeated `title` once more (light weighting) + description, then shingle.
- All hyperparameters are exposed; feel free to tune and document your choices in the report.
