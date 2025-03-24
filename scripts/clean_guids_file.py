import json
from argparse import ArgumentParser

from read_data import load_image_data_pair

if __name__ != "__main__":
    raise NotImplementedError("cannot be used as a module")

parser = ArgumentParser()
parser.add_argument("--guids", required=True)
args = parser.parse_args()

with open(args.guids, "r") as gf:
    all_guids = json.load(gf)

new_guids = [] 
for e in all_guids:
    c_guid = e["guid"]
    try:
        load_image_data_pair(c_guid)
        new_guids.append(e)
    except ValueError:
        print(c_guid, "missing, skipping")

with open(args.guids, "w") as gf:
    json.dump(new_guids, gf, indent=4)