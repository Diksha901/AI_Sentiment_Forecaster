from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
import pandas as pd
from pathlib import Path

base = Path(__file__).resolve().parent.parent
file_path = base / "output" / "results.csv"

df = pd.read_csv(file_path)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")
kw_model = KeyBERT(model)


def extract_row_keywords(text):
    
    if not isinstance(text, str) or not text.strip():
        return ""

    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1,2),
        stop_words="english",
        top_n=5
    )

    return ", ".join([kw[0] for kw in keywords])


df["row_keywords"] = df["clean_text"].apply(extract_row_keywords)

df.to_csv(base / "output" / "row_keywords_results.csv", index=False)
