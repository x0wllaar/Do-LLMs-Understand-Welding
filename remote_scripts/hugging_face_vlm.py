import torch
from server_class import ChatModel
from transformers import (AutoModelForVision2Seq, AutoProcessor,
                          BitsAndBytesConfig,
                          LlavaNextForConditionalGeneration,
                          Qwen2VLForConditionalGeneration)
from transformers_cfg.generation.logits_process import \
    GrammarConstrainedLogitsProcessor
from transformers_cfg.grammar_utils import IncrementalGrammarConstraint
from transformers_cfg.tokenization.utils import get_tokenizer_charset

DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
# we fail early if we don't have GPU
assert DEVICE.startswith("cuda"), "no GPU available"

with open("./json.ebnf", "r") as file:
    JSON_GRAMMAR_STR = file.read()

QUANT_CONFIG = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype="float16",
)


class HuggingFaceChatModel(ChatModel):
    def __init__(
        self,
        model_name,
        delete_prompt=False,
        temperature=0.8,
        top_p=0.7,
    ):
        processor, model = self.get_processor_model(model_name)

        self.processor = processor
        self.model = model

        eos = self.model.generation_config.eos_token_id
        if isinstance(eos, int):
            self.model.generation_config.pad_token_id = eos
        self.delete_prompt = delete_prompt
        self.temperature = temperature
        self.top_p = top_p

    @staticmethod
    def get_processor_model(model_name):
        raise NotImplementedError(
            "this class is intended for abstract use only"
        )

    def preprocess_messages(self, conversation):
        raise NotImplementedError(
            "this class is intended for abstract use only"
        )

    def run_messages(self, conversation, images=None, json=False) -> str:
        conversation = self.preprocess_messages(conversation)
        prompt = self.processor.apply_chat_template(conversation)
        inputs = self.processor(
            images=images, text=prompt, return_tensors="pt"
        ).to(DEVICE)
        if not self.delete_prompt:
            prompt_length = 0
        else:
            prompt_length = inputs["input_ids"].shape[1]
        if json:
            grammar = IncrementalGrammarConstraint(
                JSON_GRAMMAR_STR, "root", self.processor.tokenizer
            )
            grammar_processor = GrammarConstrainedLogitsProcessor(grammar)
            output = self.model.generate(
                **inputs,
                max_new_tokens=1024,
                logits_processor=[grammar_processor],
                do_sample=True,
                temperature=self.temperature,
                top_p=self.top_p,
                num_beams=1
            )
        else:
            output = self.model.generate(
                **inputs,
                max_new_tokens=1024,
                do_sample=True,
                temperature=self.temperature,
                top_p=self.top_p,
                num_beams=1
            )

        decoded = self.processor.decode(
            output[0][prompt_length:], skip_special_tokens=True
        )
        return decoded

    @staticmethod
    def get_class(model_name):
        if "llava-v1.6" in model_name.lower():
            return LLaVANextChatModel
        if "idefics2" in model_name.lower():
            return Idefics2ChatModel
        if "qwen2" in model_name.lower():
            return Qwen2ChatModel
        return HuggingFaceChatModel


# llava-hf/llava-v1.6-mistral-7b-hf
class LLaVANextChatModel(HuggingFaceChatModel):
    @staticmethod
    def get_processor_model(model_name):
        processor = AutoProcessor.from_pretrained(model_name)
        model = LlavaNextForConditionalGeneration.from_pretrained(
            model_name,
            quantization_config=QUANT_CONFIG,
            device_map="auto",
        )
        return processor, model

    def preprocess_messages(self, conversation):
        for m in conversation:
            if m["role"] == "system":
                m["role"] = "user"
        return conversation


class Idefics2ChatModel(HuggingFaceChatModel):
    @staticmethod
    def get_processor_model(model_name):
        processor = AutoProcessor.from_pretrained(model_name)
        model = AutoModelForVision2Seq.from_pretrained(
            model_name,
            quantization_config=QUANT_CONFIG,
            device_map="auto",
        )
        return processor, model

    def preprocess_messages(self, conversation):
        for m in conversation:
            if m["role"] == "system":
                m["role"] = "user"
        return conversation


class Qwen2ChatModel(HuggingFaceChatModel):
    @staticmethod
    def get_processor_model(model_name):
        processor = AutoProcessor.from_pretrained(model_name)
        model = Qwen2VLForConditionalGeneration.from_pretrained(
            model_name,
            quantization_config=QUANT_CONFIG,
            device_map="auto",
        )
        return processor, model

    def preprocess_messages(self, conversation):
        for m in conversation:
            if m["role"] == "system":
                m["role"] = "user"
        return conversation
