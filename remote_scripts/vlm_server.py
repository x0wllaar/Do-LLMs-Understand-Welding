from argparse import ArgumentParser

from flask import Flask, jsonify, request
from hugging_face_vlm import HuggingFaceChatModel
from server_class import OpenAIMessageDecoder

parser = ArgumentParser()
parser.add_argument("--model", required=True)
parser.add_argument("--noprompt", action="store_true")
parser.add_argument("--port", default=56873, type=int)
ARGS = parser.parse_args()

MODEL = HuggingFaceChatModel.get_class(ARGS.model)(
    ARGS.model, delete_prompt=ARGS.noprompt
)
DECODER = OpenAIMessageDecoder()

app = Flask(__name__)


@app.route("/api/generate", methods=["POST"])
def generate():
    content = request.get_json()
    assert (
        ARGS.model == content["params"]["model"]
    ), f"wrong model used, expected {ARGS.model}"
    msgs, imgs = DECODER.preprocess_chat(content["messages"])
    output = MODEL.run_messages(msgs, imgs, json=content["params"]["json"])
    return jsonify({"content": output})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=ARGS.port, debug=True)
