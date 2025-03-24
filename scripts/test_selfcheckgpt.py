import json
from argparse import ArgumentParser

import numpy as np
import pandas as pd
from tqdm import tqdm

COLS_TO_COMPARE = [
    "NarrativeRVMarine",
    "NarrativeAeronautical",
    "NarrativeFarming",
]

parser = ArgumentParser()
parser.add_argument(
    "--guids", "-g", help="Path to GUID set JSON", type=str, required=True
)
parser.add_argument(
    "--scores",
    "-p",
    help="Path to CoT embedding JSON folder",
    type=str,
    required=True,
)
parser.add_argument(
    "--out", "-o", help="Path to output Excel", type=str, required=True
)
args = parser.parse_args()

with open(args.guids, "rt", encoding="utf-8") as gf:
    guids = json.load(gf)


def read_score_json_selfcheckgpt_file(path):
    with open(path, "rt", encoding="utf-8") as tf:
        data = json.load(tf)

    res_dict = {}
    for col in COLS_TO_COMPARE:
        res_dict[col] = []

    for run in data:
        for col in COLS_TO_COMPARE:
            emb = run[col]
            res_dict[col].append(emb)

    proc_dict = {}
    for col, arr in res_dict.items():
        proc_dict[col] = np.mean(arr, axis=0)

    return proc_dict


dicts = {}
for guid_class in tqdm(guids):
    guid = guid_class["guid"]
    clazz = guid_class["class"]

    scores = read_score_json_selfcheckgpt_file(
        f"{args.scores}/{guid}.json"
    )

    if clazz not in dicts:
        dicts[clazz] = []

    dicts[clazz].append(scores)


try:
    writer = pd.ExcelWriter(args.out)
    for clazz in dicts:
        sim_df = pd.DataFrame(dicts[clazz])
        desc_df = sim_df.describe()
        desc_df.to_excel(writer, sheet_name=clazz, index=True)
finally:
    writer.close()
