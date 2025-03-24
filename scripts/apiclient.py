from config import CONFIG
from openai import OpenAI

client = OpenAI(api_key=CONFIG["secrets"]["openai_key"])

external_model_api = CONFIG["remotemodels"]["api_url"]
external_client = OpenAI(api_key="-", base_url=external_model_api)


def run_openai_chat_messages(
    messages, model="gpt-4o", seed=None, json=False
):
    local_client = client
    if not model.lower().startswith("gpt"):
        local_client = external_client
    
    chat_funtion = local_client.chat.completions.create
    parsing = False
    if isinstance(json, bool):
        fmt = {"type": "json_object"} if json else None
    else:
        fmt = json
        chat_funtion = local_client.beta.chat.completions.parse
        parsing = True
    
    response = chat_funtion(
        model=model,
        messages=messages,
        seed=seed,
        response_format=fmt,
    )
    choice = response.choices[0]
    assert choice.finish_reason == "stop", f"Finish reason: {choice.finish_reason}"
    msg = choice.message
    
    if parsing:
        return msg.content, msg.parsed
    return msg.content


def run_chat_messages(messages, model="gpt-4o", seed=None, json=False):
    return run_openai_chat_messages(messages, model, seed, json)


# From: https://platform.openai.com/docs/guides/embeddings/use-cases
def generate_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ").strip()
    emb = (
        client.embeddings.create(input=[text], model=model)
        .data[0]
        .embedding
    )
    return emb
