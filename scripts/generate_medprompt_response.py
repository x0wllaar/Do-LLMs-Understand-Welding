import json
from argparse import ArgumentParser
from copy import deepcopy

from apiclient import run_chat_messages
from config import CONFIG
from read_data import load_embedding_cot_data_pair, load_image_data_pair
from scipy import spatial
from util import obj2base85json, string2seed
from formats import Acceptability

if __name__ != "__main__":
    raise NotImplementedError("cannot be used as a module")

parser = ArgumentParser()
parser.add_argument("--out", required=True)
parser.add_argument("--guid", required=True)
parser.add_argument("--cotdata", required=True)
parser.add_argument("--guids", required=True)
parser.add_argument("--model", default="gpt-4o")
args = parser.parse_args()


def make_init_messages(context):
    messages = [
        {
            "role": "system",
            "content": CONFIG["medprompt_responses"][
                "generation_system_prompt"
            ].format(context=context),
        },
    ]
    return messages


def make_cot_injection_message(context, cot_data):
    formatted_cots = "\n".join(
        [
            "\n".join(
                [
                    (c[0] + "\n" + "Acceptable: ")
                    + ("Yes" if c[1] else "No")
                    for c in d["cots"]
                ]
            )
            for d in cot_data
        ]
    )
    image_b64s = [load_image_data_pair(d["guid"])[0] for d in cot_data]

    msg_text = (
        CONFIG["medprompt_responses"][
            "medprompt_cot_injection_prompt"
        ].format(context=context)
        + "\n\n"
        + formatted_cots
    )

    img_token_list = [
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{imageb64}"},
        }
        for imageb64 in image_b64s
    ]

    return {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": msg_text,
            }
        ]
        + img_token_list,
    }


def make_picture_cot_message(imageb64, context):
    return {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": CONFIG["medprompt_responses"][
                    "cot_generation_prompt"
                ].format(context=context),
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{imageb64}"},
            },
        ],
    }


def make_binary_response_message(context):
    return {
        "role": "user",
        "content": CONFIG["medprompt_responses"][
            "binary_generation_prompt"
        ].format(context=context),
    }


def cosine_sim(a, b):
    return 1 - spatial.distance.cosine(a, b)


def find_best_match_cot(emb, ds, ctx, cotdata):
    best_point = None
    best_sim = float("-Inf")
    for point in cotdata[ctx][ds]:
        csim = cosine_sim(emb, point["embedding"])
        if csim > best_sim:
            best_point = point
            best_sim = csim
    assert best_point is not None
    return best_point


def find_k_best_match_cot(emb, ds, ctx, cotdata, k=5):
    cotdata = deepcopy(cotdata)
    points = []
    for i in range(k):
        c_point = find_best_match_cot(emb, ds, ctx, cotdata)
        drop_guid(c_point["guid"], ctx, cotdata)
        points.append(c_point)
    return points


def find_guid_dataset(guid, guids):
    for guid_ds in guids:
        c_guid = guid_ds["guid"]
        dataset = guid_ds["class"]
        if c_guid == guid:
            return dataset
    raise ValueError(f"GUID {guid} was not found")


def drop_guid(guid, ctx, data):
    for ds_name, ds in data[ctx].items():
        for i in range(len(ds)):
            if ds[i]["guid"] == guid:
                ds.pop(i)
                return
    raise ValueError(f"GUID {guid} was not found")


with open(args.guids, "rt", encoding="utf-8") as gf:
    guids = json.load(gf)

with open(args.cotdata, "rt", encoding="utf-8") as cotfile:
    cot_data = json.load(cotfile)

imageb64, data = load_image_data_pair(args.guid)
_, input_emb = load_embedding_cot_data_pair(args.guid)
input_ds = find_guid_dataset(args.guid, guids)

ctxs = list(CONFIG["zero_shot_responses"]["contexts"].keys())
for ctx in ctxs:
    try:
        drop_guid(args.guid, ctx, cot_data)
    except ValueError:
        print("Warn! Error dropping GUID", args.guid)

all_responses_out = []

for run_n in range(CONFIG["medprompt_responses"]["n_responses"]):
    out_dict = {
        "seed_strs": [],
        "seed_nums": [],
        "message_dumps": [],
        "guid": args.guid,
        "run_n": run_n,
    }
    for context_name, (binary_column, narrative_column) in CONFIG[
        "zero_shot_responses"
    ]["contexts"].items():
        c_cot_data = deepcopy(cot_data)
        emb_guids = find_k_best_match_cot(
            input_emb, input_ds, context_name, c_cot_data
        )
        # Assert that there's no data leak
        exact_emb_guids = set([g["guid"] for g in emb_guids])
        assert args.guid not in exact_emb_guids

        # Generate seed
        seed_str = CONFIG["medprompt_responses"]["generation_seed"].format(
            guid=args.guid, run=run_n, context=context_name
        )
        seed = string2seed(seed_str)

        # Inject MedPrompt CoT
        messages = make_init_messages(context_name)
        messages.append(
            make_cot_injection_message(context_name, emb_guids)
        )
        messages.append(
            {
                "role": "assistant",
                "content": run_chat_messages(
                    messages=messages, seed=seed, model=args.model
                ),
            }
        )

        # Get CoT Response

        messages.append(make_picture_cot_message(imageb64, context_name))
        cot_response = run_chat_messages(
            messages=messages, seed=seed, model=args.model
        )
        messages.append({"role": "assistant", "content": cot_response})

        # Get Binary Response
        messages.append(make_binary_response_message(context_name))
        raw_binary_response, parsed_binary_response = run_chat_messages(
            messages=messages, seed=seed, json=Acceptability, model=args.model
        )
        messages.append(
            {"role": "assistant", "content": raw_binary_response}
        )
        try:
            binary_response = parsed_binary_response.acceptable
        except:
            print("FAILED JSON DECODE")
            print(raw_binary_response)
            exit(1)

        out_dict["seed_strs"].append({context_name: seed_str})
        out_dict["seed_nums"].append({context_name: seed})

        out_dict[binary_column] = binary_response
        out_dict[narrative_column] = cot_response

        out_dict["message_dumps"].append(
            {context_name: obj2base85json(messages)}
        )

    all_responses_out.append(out_dict)

with open(args.out, "wt", encoding="utf-8") as outfile:
    json.dump(all_responses_out, outfile, indent=4)
