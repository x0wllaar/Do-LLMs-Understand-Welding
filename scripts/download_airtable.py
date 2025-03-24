import io
import json
import re
import uuid
from argparse import ArgumentParser

import pandas as pd
import requests
from PIL import Image

if __name__ != "__main__":
    raise ImportError("This script should not be imported")

URL_REGEX = r"\((https://.*?\.airtable.*?\.com/.*?)\)"

COLUMN_NAME_MAPPING = {
    # Narrative columns
    'Is this weld acceptable in the context of "RV and Marine"?': "NarrativeRVMarine",
    "Is this weld acceptable in the context of Aeronautical": "NarrativeAeronautical",
    "Is this weld acceptable in the context of Farming?": "NarrativeFarming",
    # Binary acceptability columns
    "Acceptable - RV & Marine": "AcceptableRVMarine",
    "Acceptable - Aeronautical": "AcceptableAeronautical",
    "Acceptable - Farming": "AcceptableFarming",
}

parser = ArgumentParser()
parser.add_argument(
    "--input", "-i", help="Path to airtable CSV", type=str, required=True
)
parser.add_argument(
    "--output",
    "-o",
    help="Path to picture folder",
    type=str,
    required=True,
)
args = parser.parse_args()

csv_data = pd.read_csv(args.input, keep_default_na=False)

guids = set()
try:
    with open(f"{args.output}/guids.json", "rt", encoding="utf-8") as gf:
        guids = set(json.load(gf))
except FileNotFoundError:
    pass

for i, row in csv_data.iterrows():
    pic_text = str(row["Photo(s)"]).strip()
    urls = re.findall(URL_REGEX, pic_text)
    if len(urls) > 1:
        print("Warning: multiple URLs found in", i)
    url = urls[0]

    response = requests.get(url)
    response.raise_for_status()
    image_bytes = response.content
    pil_image = Image.open(io.BytesIO(image_bytes))

    guid = str(uuid.uuid4())
    pil_image.save(f"{args.output}/pics/{guid}.png")

    data_dict = {}
    for col, new_col in COLUMN_NAME_MAPPING.items():
        data_dict[new_col] = (
            row[col]
            if new_col.startswith("Narrative")
            else row[col].strip().lower() == "yes"
        )
    data_dict["guid"] = guid
    data_dict["row"] = i + 1

    with open(
        f"{args.output}/data/{guid}.json", "wt", encoding="utf-8"
    ) as tf:
        json.dump(data_dict, tf, indent=4)

    print("save image", "for", i, "guid", guid)

    guids.add(guid)
    with open(f"{args.output}/guids.json", "wt", encoding="utf-8") as gf:
        json.dump(list(guids), gf, indent=4)
