import json
from argparse import ArgumentParser

import numpy as np

from apiclient import generate_embedding

if __name__ != "__main__":
    raise NotImplementedError("cannot be used as a module")

NARRATIVE_COLS = [
    "NarrativeRVMarine",
    "NarrativeAeronautical",
    "NarrativeFarming",
]

parser = ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--out", required=True)
ARGS = parser.parse_args()

with open(ARGS.input, "rt", encoding="utf-8") as f:
    data = json.load(f)

if not isinstance(data, list):
    data = [data]


embeddings = []
for d in data:
    emb_dict = {}
    for col in NARRATIVE_COLS:
        text = d[col].strip()
        if text == "":
            # By default, the length of the embedding vector will be 1536 for text-embedding-3-small or 3072 for text-embedding-3-large.
            # if empty, we will fill it with zeros
            emb_dict[f"{col}"] = list(np.zeros(1536))
        else:
            emb_dict[f"{col}"] = generate_embedding(d[col])
    embeddings.append(emb_dict)

if len(embeddings) == 1:
    embeddings = embeddings[0]

with open(ARGS.out, "wt", encoding="utf-8") as f:
    json.dump(embeddings, f, indent=4)
