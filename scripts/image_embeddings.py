import json
from argparse import ArgumentParser

from read_data import load_image_pil
from transformers import ViTImageProcessor, ViTModel

parser = ArgumentParser()
parser.add_argument("--guid", required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()

# Transformer and Image Processor Initialized
processor = ViTImageProcessor.from_pretrained(
    "google/vit-base-patch16-224-in21k"
)
model = ViTModel.from_pretrained("google/vit-base-patch16-224-in21k")


parser = ArgumentParser()
parser.add_argument("--guid", required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()

image = load_image_pil(args.guid)

# Do image preprocessing
inputs = processor(images=image, return_tensors="pt")

outputs = model(**inputs)
last_hidden_states = (
    outputs.last_hidden_state.squeeze().detach().numpy().tolist()
)
# Last Layer State Detached, Converted to Numpy
# Then Converted to Python List to be Easily Stored in JSON File

output_data = last_hidden_states[0]

# Output Stored as JSON File
with open(args.out, "w") as outfile:
    json.dump(output_data, outfile, indent=4)
