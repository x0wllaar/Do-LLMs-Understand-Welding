import json
from argparse import ArgumentParser

import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, roc_auc_score
from tqdm import tqdm

COLS_TO_COMPARE = [
    "AcceptableRVMarine",
    "AcceptableAeronautical",
    "AcceptableFarming",
]

parser = ArgumentParser()
parser.add_argument(
    "--guids", "-g", help="Path to GUID set JSON", type=str, required=True
)
parser.add_argument(
    "--truth",
    "-t",
    help="Path to truth JSON folder",
    type=str,
    required=True,
)
parser.add_argument(
    "--pred",
    "-p",
    help="Path to predicted JSON folder",
    type=str,
    required=True,
)
parser.add_argument(
    "--out", "-o", help="Path to output Excel", type=str, required=True
)
args = parser.parse_args()

with open(args.guids, "rt", encoding="utf-8") as gf:
    guids = json.load(gf)


def read_pred_json_file(path):
    with open(path, "rt", encoding="utf-8") as tf:
        data = json.load(tf)

    res_dict = {}
    for col in COLS_TO_COMPARE:
        res_dict[col] = []

    for run in data:
        for col in COLS_TO_COMPARE:
            res = run[col]
            assert isinstance(res, bool)
            res_dict[col].append(res)

    proc_dict = {}
    dec_val_dict = {}
    for col, arr in res_dict.items():
        proc_dict[col] = (np.array(arr) + 0).mean() > 0.5
        dec_val_dict[col] = (np.array(arr) + 0).mean()

    return proc_dict, dec_val_dict


def read_truth_json_file(path):
    with open(path, "rt", encoding="utf-8") as tf:
        data = json.load(tf)

    res_dict = {}
    for col in COLS_TO_COMPARE:
        res_dict[col] = data[col]

    return res_dict


truths = {}
preds = {}
dec_vals = {}
for guid_class in tqdm(guids):
    guid = guid_class["guid"]
    clazz = guid_class["class"]

    truth = read_truth_json_file(f"{args.truth}/{guid}.json")
    pred, dec_val = read_pred_json_file(f"{args.pred}/{guid}.json")

    for col in COLS_TO_COMPARE:
        assert truth[col] in [True, False]
        assert pred[col] in [True, False]

    if clazz not in truths:
        truths[clazz] = []
    if clazz not in preds:
        preds[clazz] = []
    if clazz not in dec_vals:
        dec_vals[clazz] = []

    truths[clazz].append(truth)
    preds[clazz].append(pred)
    dec_vals[clazz].append(dec_val)

assert tuple(sorted(set(truths.keys()))) == tuple(
    sorted(set(preds.keys()))
)

try:
    writer = pd.ExcelWriter(args.out)

    for clazz in truths:
        truths_df = pd.DataFrame(truths[clazz])
        preds_df = pd.DataFrame(preds[clazz])
        dec_vals_df = pd.DataFrame(dec_vals[clazz])

        report = classification_report(
            truths_df,
            preds_df,
            target_names=COLS_TO_COMPARE,
            output_dict=True,
        )

        roc_auc_per_class_scores = roc_auc_score(
            truths_df, dec_vals_df, average=None
        )
        for n, col in enumerate(dec_vals_df.columns.tolist()):
            report[col]["rocauc"] = float(roc_auc_per_class_scores[n])
        for avg_type in ["macro", "micro", "weighted", "samples"]:
            try:
                roc_auc_c_score = roc_auc_score(
                    truths_df, dec_vals_df, average=avg_type
                )
            except ValueError:
                roc_auc_c_score = float("NaN")
            report[f"{avg_type} avg"]["rocauc"] = roc_auc_c_score

        report_df = pd.DataFrame(report).T

        print(report)

        # We need index=True there, otherwise it will not save
        # the names of the metrics used
        report_df.to_excel(writer, sheet_name=clazz, index=True)

finally:
    writer.close()
