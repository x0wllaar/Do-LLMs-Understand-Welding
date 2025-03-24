import json
from argparse import ArgumentParser

from config import CONFIG
from read_data import load_embedding_cot_data_pair, load_image_data_pair
from tqdm import tqdm

if __name__ != "__main__":
    raise NotImplementedError("cannot be used as a module")

parser = ArgumentParser()
parser.add_argument("--out", required=True)
parser.add_argument("--guids", required=True)
args = parser.parse_args()


def load_cots_embeddings(guids, context):
    datas = {}
    for guid_ds in tqdm(guids):
        guid = guid_ds["guid"]
        dataset = guid_ds["class"]

        zshot, image_embedding = load_embedding_cot_data_pair(guid)
        _, truth = load_image_data_pair(guid)
        correct_cots = []
        for run in zshot:
            bin_var_name = CONFIG["zero_shot_responses"]["contexts"][
                context
            ][0]
            narrative_var_name = CONFIG["zero_shot_responses"]["contexts"][
                context
            ][1]
            if run[bin_var_name] != truth[bin_var_name]:
                continue
            correct_cots.append(
                (run[narrative_var_name], run[bin_var_name])
            )
        if len(correct_cots) > 0:
            cot_dict = {
                "embedding": image_embedding,
                "cots": correct_cots,
                "guid": guid,
            }
            if dataset not in datas:
                datas[dataset] = []
            datas[dataset].append(cot_dict)
    return datas


with open(args.guids, "rt", encoding="utf-8") as gf:
    guids = json.load(gf)

ctxs = list(CONFIG["zero_shot_responses"]["contexts"].keys())

embs = {}
for ctx in ctxs:
    print("Loading", ctx)
    r = load_cots_embeddings(guids, ctx)
    total = 0
    for ds, samples in r.items():
        ds_len = len(samples)
        print(ds_len, "samples in", ds)
        total += ds_len
    print(total, "samples in total")
    embs[ctx] = r

with open(args.out, "wt", encoding="utf-8") as of:
    json.dump(embs, of, indent=4)
