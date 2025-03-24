# A simple implementation of SelfCheckGPT
# https://arxiv.org/pdf/2303.08896.pdf

import json
import statistics
from argparse import ArgumentParser

from apiclient import run_chat_messages
from config import CONFIG
from read_data import load_image_data_pair
from util import string2seed

if __name__ != "__main__":
    raise NotImplementedError("cannot be used as a module")

COLS_TO_COMPARE = [
    "NarrativeRVMarine",
    "NarrativeAeronautical",
    "NarrativeFarming",
]


def make_messages(text):
    messages = [
        {
            "role": "system",
            "content": CONFIG["selfcheckgpt"]["system_prompt"],
        },
        {"role": "user", "content": text},
    ]
    return messages


def selfcheckgpt(context_text: str, text_to_check: str, guid: str):
    ttc_sentences = [
        s.strip().replace("\n", " ") + "."
        for s in text_to_check.split(".")
    ]
    context_text = context_text.strip().replace("\n", " ")
    scores = []
    for sentence in ttc_sentences:
        sent_prompt = CONFIG["selfcheckgpt"]["user_prompt"].format(
            context=context_text, sentence=sentence
        )
        seed_str = CONFIG["selfcheckgpt"]["seed"].format(
            context=context_text, sentence=sentence, guid=guid
        )
        seed = string2seed(seed_str)
        messages = make_messages(sent_prompt)
        json_resp = run_chat_messages(
            messages=messages, model="gpt-4o-mini", seed=seed, json=True
        )
        try:
            resp = json.loads(json_resp)
        except:
            print("Could not decode response", json_resp)
            scores.append(0.5)
            continue

        if resp["is_supported"]:
            scores.append(1.0)
        else:
            scores.append(0.0)
    mean_score = statistics.mean(scores)
    return {"score": mean_score, "sentence_scores": scores}


parser = ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--out", required=True)
parser.add_argument("--guid", required=True)
ARGS = parser.parse_args()

_, ground_truth_data = load_image_data_pair(ARGS.guid)

with open(ARGS.input, "rt", encoding="utf-8") as f:
    preds = json.load(f)

all_dicts = []
for run in preds:
    run_dict = {}
    for col in COLS_TO_COMPARE:
        truth = ground_truth_data[col]
        pred = run[col]

        if truth.strip() == "":
            print("Warning: empty truth")
            run_dict[f"{col}"] = 0.5
            run_dict[f"{col}_sentence_scores"] = [0.5]
        else:
            sc = selfcheckgpt(
                context_text=truth, text_to_check=pred, guid=ARGS.guid
            )
            run_dict[f"{col}"] = sc["score"]
            run_dict[f"{col}_sentence_scores"] = sc["sentence_scores"]
    all_dicts.append(run_dict)

with open(ARGS.out, "wt", encoding="utf-8") as f:
    json.dump(all_dicts, f, indent=4)
