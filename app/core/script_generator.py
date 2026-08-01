import random
import os
import json
import re
import base64
import logging
import httpx

logger = logging.getLogger(__name__)

# ── Fallback templates (used when Gemini is unavailable) ──────────────────────
TEMPLATES = {
    "en": [
        "In the latest episode of '{title}', {char} faces a challenging dilemma that could change everything.",
        "This week in '{title}', tensions rise as {char} needs to make a crucial decision regarding their future.",
        "The stakes have never been higher in '{title}', with {char} caught between friendships and rivalries.",
        "Emotions run high in '{title}', as {char} struggles with personal conflicts that impact their relationships.",
    ],
    "de": [
        "In der neuesten Episode von '{title}' steht {char} vor einem schwierigen Dilemma, das alles verändern könnte.",
        "Diese Woche in '{title}' steigen die Spannungen, als {char} eine entscheidende Wahl treffen muss.",
        "Die Lage war noch nie so ernst in '{title}' — {char} ist zwischen Freundschaft und Rivalität gefangen.",
        "Die Emotionen kochen über in '{title}', als {char} mit inneren Konflikten kämpft.",
    ],
    "ru": [
        "В последней главе «{title}» {char} оказывается перед трудной дилеммой, способной изменить всё.",
        "На этой неделе в «{title}» напряжение нарастает: {char} должен принять судьбоносное решение.",
        "Ставки как никогда высоки в «{title}» — {char} оказался между дружбой и соперничеством.",
        "В «{title}» кипят страсти: {char} борется с внутренними противоречиями.",
    ],
}

FALLBACK = {
    "en": "In the latest episode of '{title}', the story continues with unexpected twists.",
    "de": "In der neuesten Episode von '{title}' nimmt die Geschichte eine unerwartete Wendung.",
    "ru": "В последней главе «{title}» история делает неожиданный поворот.",
}

VALID_MOODS = {"action", "romance", "drama", "mystery", "comedy"}
LANG_NAMES  = {"en": "English", "de": "German", "ru": "Russian"}

# Used instead of a literal "Unknown" when no title was provided
TITLE_FALLBACK = {
    "en": "this chapter",
    "de": "dieses Kapitel",
    "ru": "эту главу",
}


def _display_title(title: str, lang: str) -> str:
    title = (title or "").strip()
    if title and title.lower() != "unknown":
        return title
    return TITLE_FALLBACK.get(lang, TITLE_FALLBACK["en"])


# ── Groq Vision analyser (OpenAI-compatible API) ───────────────────────────────
class GeminiAnalyzer:
    """Real AI image analysis — sends the panel image to a Groq vision model."""

    GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def analyze(
        self,
        image_bytes: bytes,
        mime_type: str,
        title: str,
        characters: list,
        lang: str,
    ) -> dict | None:
        """
        Returns {"recap": str, "mood": str} based on what the model actually sees
        in the image. Returns None if unavailable or on any error.
        """
        if not self.available:
            logger.warning("GROQ_API_KEY not set — skipping AI analysis")
            return None

        try:
            language     = LANG_NAMES.get(lang, "English")
            chars_str    = ", ".join(characters) if characters else "the main character"
            title_display = _display_title(title, lang)

            prompt = (
                f'You are analyzing a manhwa/webtoon chapter image.\n'
                f'Title: "{title_display}"\n'
                f'Main characters: {chars_str}\n\n'
                f'Look carefully at the panels in this image. Based on what you actually SEE:\n\n'
                f'1. Write a dramatic and engaging 1-2 sentence story recap in {language}. '
                f'Be specific — mention the action, emotions, or key moments visible in the panels.\n'
                f'2. Identify the dominant mood. Choose EXACTLY ONE: '
                f'action, romance, drama, mystery, comedy\n\n'
                f'Respond with valid JSON only (no markdown, no extra text):\n'
                f'{{"recap": "your recap here", "mood": "one_mood_here"}}'
            )

            b64_image = base64.b64encode(image_bytes).decode("utf-8")
            data_url  = f"data:{mime_type or 'image/jpeg'};base64,{b64_image}"

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            # Groq deprecated the Llama-4 vision models (scout/maverick) — as of
            # August 2026 the only vision-capable model on Groq is Qwen 3.6 27B.
            # Kept as a list so we can add fallbacks again if Groq ships more.
            for model_name in [
                "qwen/qwen3.6-27b",
            ]:
                try:
                    payload = {
                        "model": model_name,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {"type": "image_url", "image_url": {"url": data_url}},
                                ],
                            }
                        ],
                        "temperature": 0.7,
                        "max_completion_tokens": 400,
                    }
                    # Qwen 3.6 27B is a "thinking" model by default — it burns its
                    # whole token budget on a <think>...</think> block and never
                    # reaches the JSON answer. Disabling reasoning fixes that.
                    if model_name.startswith("qwen/"):
                        payload["reasoning_effort"] = "none"
                    response = httpx.post(
                        self.GROQ_URL, headers=headers, json=payload, timeout=30.0
                    )
                    response.raise_for_status()
                    content = response.json()["choices"][0]["message"]["content"]
                    result = self._parse(content)
                    if result:
                        logger.info("Groq OK with model: %s", model_name)
                        return result
                    else:
                        # The call succeeded but we couldn't extract valid JSON —
                        # log the raw content so we can see what the model actually
                        # returned (e.g. reasoning text, markdown fences, etc.)
                        logger.warning(
                            "Model %s returned unparseable content: %r",
                            model_name, content[:500]
                        )
                except Exception as exc:
                    logger.warning("Model %s failed: %s", model_name, exc)
                    continue

            return None

        except Exception as exc:
            logger.warning("Groq analysis failed: %s", exc)
            return None

    # ── helpers ──────────────────────────────────────────────────────────────
    def _parse(self, text: str) -> dict | None:
        """Extract and validate JSON from the model's response."""
        cleaned = text.strip()
        # Some models wrap JSON in markdown code fences (```json ... ```)
        cleaned = re.sub(r'^```(?:json)?\s*|\s*```$', '', cleaned, flags=re.IGNORECASE).strip()
        # "Thinking" models may prepend reasoning in <think>...</think> tags
        cleaned = re.sub(r'<think>.*?</think>', '', cleaned, flags=re.DOTALL).strip()

        try:
            return self._validate(json.loads(cleaned))
        except (json.JSONDecodeError, ValueError):
            pass

        # Greedy match: grabs from the first '{' to the LAST '}' in the text,
        # which survives extra preamble/explanation text around the JSON object.
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            try:
                return self._validate(json.loads(match.group()))
            except (json.JSONDecodeError, ValueError):
                pass
        return None

    def _validate(self, data: dict) -> dict:
        recap = str(data.get("recap", "")).strip()
        mood  = str(data.get("mood", "")).strip().lower()
        if not recap:
            raise ValueError("empty recap")
        if mood not in VALID_MOODS:
            mood = "drama"
        return {"recap": recap, "mood": mood}


# ── Template-based fallback ───────────────────────────────────────────────────
class ScriptGenerator:
    def __init__(self, title: str, characters: list, lang: str = "en"):
        self.title      = title
        self.characters = characters
        self.lang       = lang if lang in TEMPLATES else "en"

    def generate_dramatic_recap(self) -> str:
        title_display = _display_title(self.title, self.lang)
        if not self.characters:
            return FALLBACK[self.lang].format(title=title_display)
        char = random.choice(self.characters)
        return random.choice(TEMPLATES[self.lang]).format(title=title_display, char=char)
