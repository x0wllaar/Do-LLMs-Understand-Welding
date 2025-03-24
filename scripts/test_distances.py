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
    "--truth",
    "-t",
    help="Path to truth embedding JSON folder",
    type=str,
    required=True,
)
parser.add_argument(
    "--pred",
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


def read_pred_json_emb_file(path):
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


def read_truth_json_emb_file(path):
    with open(path, "rt", encoding="utf-8") as tf:
        data = json.load(tf)

    res_dict = {}
    for col in COLS_TO_COMPARE:
        res_dict[col] = np.array(data[col])

    return res_dict


dists = {}
for guid_class in tqdm(guids):
    guid = guid_class["guid"]
    clazz = guid_class["class"]

    truth = read_truth_json_emb_file(f"{args.truth}/{guid}.json")
    pred = read_pred_json_emb_file(f"{args.pred}/{guid}.json")

    c_dict = {}
    for col in COLS_TO_COMPARE:
        assert len(truth[col]) == 1536
        assert len(pred[col]) == 1536

        u = truth[col]
        v = pred[col]

        # We need to add small epsilon to avoid division by zero
        sim = (u @ v.T) / (np.linalg.norm(u) * np.linalg.norm(v) + 1e-6)
        c_dict[col] = sim

    if clazz not in dists:
        dists[clazz] = []
    dists[clazz].append(c_dict)


try:
    writer = pd.ExcelWriter(args.out)

    for clazz in dists:
        sim_df = pd.DataFrame(dists[clazz])
        desc_df = sim_df.describe()

        desc_df.to_excel(writer, sheet_name=clazz, index=True)
finally:
    writer.close()
