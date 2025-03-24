from io import BytesIO
from urllib import request

from PIL import Image


class ChatModel(object):
    def run_messages(self, conversation, images=None, json=False) -> str:
        raise NotImplementedError("this is an abstract class")


class ConversationPreprocessor(object):
    def preprocess_chat(self, input_conversation):
        raise NotImplementedError("this is an abstract class")


class OpenAIMessageDecoder(ConversationPreprocessor):
    def preprocess_chat(self, input_conversation):
        images = []
        messages = []
        for msg in input_conversation:
            role = msg["role"].lower()
            assert role in {
                "user",
                "assistant",
                "system",
            }, f"unsupported role {role}"
            c_msg = {}
            c_msg["role"] = role
            content = msg["content"]
            if isinstance(content, str):
                c_msg["content"] = [{"type": "text", "text": content}]
            else:
                c_content = []
                for chunk in content:
                    typ = chunk["type"]
                    assert typ in {"text", "image_url"}
                    if typ == "text":
                        c_content.append(
                            {"type": "text", "text": chunk["text"]}
                        )
                    elif typ == "image_url":
                        c_content.append({"type": "image"})
                        url = chunk["image_url"]["url"]
                        assert url.startswith("data:image")
                        with request.urlopen(url) as resp:
                            image_bytes = resp.read()
                        img = Image.open(BytesIO(image_bytes))
                        images.append(img)
                c_msg["content"] = c_content
            messages.append(c_msg)
        return messages, images
