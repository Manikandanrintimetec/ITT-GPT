from transformers import pipeline

from app.core.config import settings

from app.llm.base import BaseLLM


class HuggingFaceProvider(BaseLLM):

    def __init__(self):
        if not all([settings.HF_MODEL, settings.HUGGINGFACE_API_KEY]):
            raise ValueError("HuggingFace requires HF_MODEL and HUGGINGFACE_API_KEY to be set in .env")

        self.pipe = pipeline(
            "text-generation",
            model=settings.HF_MODEL,
            token=settings.HUGGINGFACE_API_KEY
        )

    def generate(self, messages):

        prompt = messages[-1]["content"]

        result = self.pipe(
            prompt,
            max_new_tokens=200
        )

        generated_text = result[0]["generated_text"]

        final_text = generated_text.replace(
            prompt,
            ""
        ).strip()

        return {
            "content": final_text,
            "prompt_tokens": 0,
            "completion_tokens": 0
        }