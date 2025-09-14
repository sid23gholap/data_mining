import gzip
import json
from typing import Dict, Any
from bs4 import BeautifulSoup

from text_clean import normalize_text

def read_json_lines(path: str):
    """Reads either JSON array or line-delimited JSON (.json or .json.gz)."""
    if path.endswith(".gz"):
        opener = gzip.open
        mode = "rt"
    else:
        opener = open
        mode = "r"

    with opener(path, mode, encoding="utf-8") as f:
        first_char = f.read(1)
        f.seek(0)

        # Case 1: JSON array
        if first_char == "[":
            data = json.load(f)
            for obj in data:
                yield obj
        # Case 2: JSON lines
        else:
            for line in f:
                if line.strip():
                    yield json.loads(line)


def load_products(path: str) -> Dict[str, Any]:
    """Load products into dict keyed by ASIN with normalized fields."""
    products = {}
    for obj in read_json_lines(path):
        asin = obj.get("asin")
        if not asin:
            continue
        title = obj.get("title", "")

        desc = obj.get("description", "")
        # 🔥 Handle case where description is a list
        if isinstance(desc, list):
            desc = " ".join([str(d) for d in desc if d]) 
            
        related=[]
        val=obj.get("similar_item",[])
        soup = BeautifulSoup(val, "html.parser")

        asins = []
        for a in soup.find_all("a", href=True):
            if "/dp/" in a["href"]:
                asin = a["href"].split("/dp/")[1].split("/")[0]
                asins.append(asin)
                
        related.extend(asins)
       # print("simi")
       # print(asins)
        
        for key in ["also_buy","also_viewed"]:
            val=obj.get(key,[])
            if isinstance(val,list):
                #print(key)
                #print(val)
                related.extend(val) 
                
        print(asin)
        print(title)
        print(desc)
        print(normalize_text(title))
        print(normalize_text(desc))
        related

        products[asin] = {
            "asin": asin,
            "title": title,
            "description": desc,
            "norm_title": normalize_text(title),
            "norm_desc": normalize_text(desc),
            "similar_item": related
        }
        break
    return products

