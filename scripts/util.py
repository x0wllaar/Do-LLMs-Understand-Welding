import base64
import hashlib
import io
import json
import lzma


# OpenAI only accepts seeds <2*63, so we cap them lower
def string2seed(seeds: str, max_seed: int = 2**62) -> int:
    ns = bytes(f"STRING2SEEDHASH|{seeds}", encoding="utf-8")
    shash = hashlib.sha3_256(ns).digest()
    hashint = int.from_bytes(shash, byteorder="little", signed=False)
    return hashint % max_seed


def obj2base85json(obj: any) -> str:
    with io.BytesIO() as lzma_bytes:
        with lzma.open(lzma_bytes, "wt", preset=8) as lzma_file:
            json.dump(obj, lzma_file)
        lzma_bytes.seek(0)
        lzma_bytearr = lzma_bytes.read()
    b85_str = base64.b85encode(lzma_bytearr).decode("utf-8")
    return b85_str


def base85json2obj(b85_str: str) -> any:
    lzma_bytes = base64.b85decode(b85_str)
    with io.BytesIO(lzma_bytes) as lzma_bytes_io:
        with lzma.open(lzma_bytes_io, "rt") as lzma_file:
            obj = json.load(lzma_file)
    return obj
