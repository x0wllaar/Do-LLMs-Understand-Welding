import json
from argparse import ArgumentParser

if __name__ != "__main__":
    raise ImportError("This script should not be imported")

parser = ArgumentParser()
parser.add_argument(
    "--input", "-i", help="Path to GUID JSON", type=str, action="append"
)
parser.add_argument(
    "--clazz",
    "-c",
    help="Name of the class to use",
    type=str,
    action="append",
)
args = parser.parse_args()


assert len(args.input) == len(args.clazz)

out_arr = []
for path, c in zip(args.input, args.clazz):
    with open(path, "rt", encoding="utf-8") as jf:
        c_data = json.load(jf)
    for guid in c_data:
        out_arr.append({"guid": guid, "class": c})

print(json.dumps(out_arr, indent=4))
