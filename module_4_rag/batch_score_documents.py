import os
import pandas as pd
from nltk.tokenize import sent_tokenize
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), "feature_repo"))
DATA_DIR = os.path.join(BASE_DIR, "data")
INPUT_FILENAME = os.path.join(DATA_DIR, "city_wikipedia_summaries.csv")
CHUNKED_FILENAME = os.path.join(DATA_DIR, "city_wikipedia_summaries_chunked.csv")
EXPORT_FILENAME = os.path.join(
    DATA_DIR, "city_wikipedia_summaries_with_embeddings.parquet"
)
TOKENIZER = "sentence-transformers/all-MiniLM-L6-v2"
MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[
        0
    ]  # First element of model_output contains all token embeddings
    input_mask_expanded = (
        attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    )
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
        input_mask_expanded.sum(1), min=1e-9
    )


def run_model(sentences, tokenizer, model):
    encoded_input = tokenizer(
        sentences, padding=True, truncation=True, return_tensors="pt"
    )
    # Compute token embeddings
    with torch.no_grad():
        model_output = model(**encoded_input)

    sentence_embeddings = mean_pooling(model_output, encoded_input["attention_mask"])
    sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)
    return sentence_embeddings


def score_data() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(EXPORT_FILENAME):
        print("Scored data not found... generating embeddings...")

        if not os.path.exists(CHUNKED_FILENAME):
            print("Chunked data not found... generating chunked data...")
            df = pd.read_csv(INPUT_FILENAME)
            df["Sentence Chunks"] = df["Wiki Summary"].apply(lambda x: sent_tokenize(x))
            chunked_df = df.explode("Sentence Chunks")
            chunked_df.to_csv(CHUNKED_FILENAME, index=False)
            df = chunked_df
        else:
            df = pd.read_csv(CHUNKED_FILENAME)

        tokenizer = AutoTokenizer.from_pretrained(TOKENIZER)
        model = AutoModel.from_pretrained(MODEL)
        embeddings = run_model(df["Wiki Summary"].tolist(), tokenizer, model)
        print("embeddings generated...")
        df["Embeddings"] = list(embeddings.detach().cpu().numpy())
        df["event_timestamp"] = pd.to_datetime("today")
        df["item_id"] = df.index

        df.to_parquet(EXPORT_FILENAME, index=False)
        print("...data exported. Job complete")
    else:
        print("Scored data found... skipping generating embeddings.")


if __name__ == "__main__":
    score_data()
