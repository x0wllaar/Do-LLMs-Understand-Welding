import json
from argparse import ArgumentParser

from read_data import load_image_data_pair
from tqdm import tqdm

if __name__ != "__main__":
    raise NotImplementedError("cannot be used as a module")

parser = ArgumentParser()
parser.add_argument("--guids", required=True)
args = parser.parse_args()

ACCEPTABLE_COLS = [
    "AcceptableRVMarine",
    "AcceptableAeronautical",
    "AcceptableFarming",
]

dataset_stats = {}

with open(args.guids, "rt", encoding="utf-8") as gf:
    guid_ds_s = json.load(gf)

for guid_ds in tqdm(guid_ds_s):
    c_guid = guid_ds["guid"]
    c_ds = guid_ds["class"]

    _, data = load_image_data_pair(c_guid)

    if c_ds not in dataset_stats:
        dataset_stats[c_ds] = dict()
        dataset_stats[c_ds]["total"] = 0
        for c in ACCEPTABLE_COLS:
            dataset_stats[c_ds][c] = dict(((True, 0), (False, 0)))

    dataset_stats[c_ds]["total"] += 1
    for c in ACCEPTABLE_COLS:
        dataset_stats[c_ds][c][data[c]] += 1

print(dataset_stats)
