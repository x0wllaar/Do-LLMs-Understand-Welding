import base64
import io
import json
import os

from PIL import Image

PICS_PATH = "./data/pics/"
DATA_PATH = "./data/data/"
ZERO_SHOT_RESPONES_PATH = "./results/zero-shot-responses/"
IMAGE_EMBEDDIGS_PATH = "./results/image-embeddings/"

MAX_PIC_SIZE = (512, 512)


def load_image_pil(guid: str) -> Image:
    guid = guid.lower()
    for ext in [".jpg", ".webp", ".png"]:
        path = f"{PICS_PATH}{guid}{ext}"
        if os.path.isfile(path):
            with Image.open(path) as im:
                # resize to at most 512x512, otherwise might get expensive
                im.thumbnail(MAX_PIC_SIZE)
                im = im.convert("RGB")
                return im
    raise ValueError(f"Could not find image for guid {guid}")


def _load_image(guid: str) -> str:
    imbytes = io.BytesIO()
    im = load_image_pil(guid)
    im.save(imbytes, format="JPEG")
    imbytes_array = imbytes.getvalue()
    base64_bytes = base64.b64encode(imbytes_array)
    base64_string = base64_bytes.decode("utf-8")
    return base64_string


def _load_data(guid: str) -> str:
    guid = guid.lower()
    path = f"{DATA_PATH}/{guid}.json"
    with open(path, "rt", encoding="utf-8") as tf:
        content = json.load(tf)
        return content


def load_image_data_pair(guid: str) -> tuple[str, str]:
    return (_load_image(guid), _load_data(guid))


def _load_json_path_guid(path: str, guid: str) -> any:
    guid = guid.lower()
    fpath = f"{path}/{guid}.json"
    with open(fpath, "rt", encoding="utf-8") as tf:
        content = json.load(tf)
        return content


def _load_zeroshot(guid: str) -> any:
    return _load_json_path_guid(ZERO_SHOT_RESPONES_PATH, guid)


def _load_image_embedding(guid: str) -> list[float]:
    return _load_json_path_guid(IMAGE_EMBEDDIGS_PATH, guid)


def load_embedding_cot_data_pair(guid: str) -> tuple[any, list[int]]:
    return (_load_zeroshot(guid), _load_image_embedding(guid))
