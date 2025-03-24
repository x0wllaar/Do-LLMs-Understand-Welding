import json
from argparse import ArgumentParser

from apiclient import run_chat_messages
from config import CONFIG
from read_data import load_image_data_pair
from util import obj2base85json, string2seed
from formats import Acceptability

if __name__ != "__main__":
    raise NotImplementedError("cannot be used as a module")


def make_init_messages(context):
    messages = [
        {
            "role": "system",
            "content": CONFIG["zero_shot_responses"][
                "generation_system_prompt"
            ].format(context=context),
        },
    ]
    return messages


def make_picture_cot_message(imageb64, context):
    return {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": CONFIG["zero_shot_responses"][
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
        "content": CONFIG["zero_shot_responses"][
            "binary_generation_prompt"
        ].format(context=context),
    }


parser = ArgumentParser()
parser.add_argument("--guid", required=True)
parser.add_argument("--out", required=True)
parser.add_argument("--model", default="gpt-4o")
ARGS = parser.parse_args()

imageb64, data = load_image_data_pair(ARGS.guid)

all_responses_out = []

for run_n in range(CONFIG["zero_shot_responses"]["n_responses"]):
    out_dict = {
        "seed_strs": [],
        "seed_nums": [],
        "message_dumps": [],
        "guid": ARGS.guid,
        "run_n": run_n,
    }
    for context_name, (binary_column, narrative_column) in CONFIG[
        "zero_shot_responses"
    ]["contexts"].items():
        # Generate seed
        seed_str = CONFIG["zero_shot_responses"]["generation_seed"].format(
            guid=ARGS.guid, run=run_n, context=context_name
        )
        seed = string2seed(seed_str)

        # Get CoT Response
        messages = make_init_messages(context_name)
        messages.append(make_picture_cot_message(imageb64, context_name))
        cot_response = run_chat_messages(
            messages=messages, seed=seed, model=ARGS.model
        )
        messages.append({"role": "assistant", "content": cot_response})

        # Get Binary Response
        messages.append(make_binary_response_message(context_name))
        raw_binary_response, parsed_binary_response = run_chat_messages(
            messages=messages, seed=seed, json=Acceptability, model=ARGS.model
        )
        messages.append(
            {"role": "assistant", "content": raw_binary_response}
        )
        try:
            binary_response = parsed_binary_response.acceptable
        except Exception as e:
            print(raw_binary_response)
            raise e

        out_dict["seed_strs"].append({context_name: seed_str})
        out_dict["seed_nums"].append({context_name: seed})

        out_dict[binary_column] = binary_response
        out_dict[narrative_column] = cot_response

        out_dict["message_dumps"].append(
            {context_name: obj2base85json(messages)}
        )

    all_responses_out.append(out_dict)

with open(ARGS.out, "wt", encoding="utf-8") as outfile:
    json.dump(all_responses_out, outfile, indent=4)
