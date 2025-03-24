import json
from argparse import ArgumentParser

import numpy as np

if __name__ != "__main__":
    raise NotImplementedError("cannot be used as a module")

parser = ArgumentParser()
parser.add_argument("--guid", required=True)
parser.add_argument("--out", required=True)
ARGS = parser.parse_args()

print("******************WARNING******************")
print("THIS SCRIPT GENERATES FAKE DATA")
print("THE RESULTS OF THE EXPERIMENTS WILL BE TAINTED")
print("DO NOT USE FOR WRITING")
print("*******************************************")


def generate_fake_embedding(size=768):
    fakeemb = np.random.uniform(0.0, 1.0, (size,))
    return list(fakeemb)


fake_emb = generate_fake_embedding()

with open(ARGS.out, "wt", encoding="utf-8") as outfile:
    json.dump(fake_emb, outfile, indent=4)
