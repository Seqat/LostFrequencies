from __future__ import annotations

import re

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


class NLPPoetryGenerator:
    def __init__(self) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
        self.model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")

    def generate_line(
        self,
        imagery: str,
        mood: str = "",
        station_character: str = "",
        contour: str = "",
        poetry_station_hint: str = "",
        poetry_mood_tone: str = "",
    ) -> str:
        imagery = str(imagery or "").strip()
        if not imagery:
            imagery = "dust, wind, fading light, an empty western road"
        mood = str(mood or "farewell").strip()
        station_character = str(station_character or "faded signal").strip()
        contour = str(contour or "descending").strip()
        station_hint = str(poetry_station_hint or "").strip() or "a half-lost roadside station at dusk"
        mood_hint = str(poetry_mood_tone or "").strip() or "restrained grief, tender and weathered"

        prompt = (
            "Write exactly one short poetic sentence in English."
            "Style: dusty 1970's western, cinematic, tender, lonely. This sentence is in radio. "
            "Return only the sentence, with NO LABELS ORE PREFACE. "
            "Do not repeat words or phrases. "
            "Do not use bullet points. "
            "Keep it under 12 words. "
            f"Station mood: {station_hint}. "
            f"Emotional intensity: {mood_hint}. "
            f"Core mood: {mood}. "
            f"Signal character: {station_character}. "
            f"Motion contour: {contour}. "
            f"Imagery: {imagery}."
        )
        try:
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=160,
            )
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=20,
                min_new_tokens=8,
                num_return_sequences=1,
                do_sample=True,
                temperature=0.95,
                top_p=0.92,
                no_repeat_ngram_size=3,
                repetition_penalty=1.4,
            )
        except Exception:
            return ""

        if output_ids is None or len(output_ids) == 0:
            return ""

        generated = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return self._clean_line(generated)

    @staticmethod
    def _clean_line(text: str) -> str:
        text = " ".join(str(text).split())
        text = re.sub(r"^(imagery|sentence|phrase|poem)\s*:\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"^['\"-:\s]+", "", text)
        if not text:
            return "The wind drifts low across a tired and empty road."
        if text[-1] not in ".!?":
            text += "."
        return text
