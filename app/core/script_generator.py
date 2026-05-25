import random
import os
import json
import re
import logging

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


# ── Gemini Flash analyser (google-genai SDK) ──────────────────────────────────
class GeminiAnalyzer:
    """Real AI image analysis — sends the panel image to Gemini Flash."""

    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_API_KEY")

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
        Returns {"recap": str, "mood": str} based on what Gemini actually sees
        in the image. Returns None if unavailable or on any error.
        """
        if not self.available:
            logger.warning("GOOGLE_API_KEY not set — skipping Gemini")
            return None

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)

            language  = LANG_NAMES.get(lang, "English")
            chars_str = ", ".join(characters) if characters else "the main character"

            prompt = (
                f'You are analyzing a manhwa/webtoon chapter image.\n'
                f'Title: "{title}"\n'
                f'Main characters: {chars_str}\n\n'
                f'Look carefully at the panels in this image. Based on what you actually SEE:\n\n'
                f'1. Write a dramatic and engaging 1-2 sentence story recap in {language}. '
                f'Be specific — mention the action, emotions, or key moments visible in the panels.\n'
                f'2. Identify the dominant mood. Choose EXACTLY ONE: '
                f'action, romance, drama, mystery, comedy\n\n'
                f'Respond with valid JSON only (no markdown, no extra text):\n'
                f'{{"recap": "your recap here", "mood": "one_mood_here"}}'
            )

            # Try models in order — free-tier keys don't always have all models
            for model_name in [
                "gemini-2.0-flash",
                "gemini-2.0-flash-lite",
                "gemini-1.5-flash",
                "gemini-1.5-flash-8b",
            ]:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[
                            types.Part.from_bytes(
                                data=image_bytes,
                                mime_type=mime_type or "image/jpeg",
                            ),
                            prompt,
                        ],
                    )
                    result = self._parse(response.text)
                    if result:
                        logger.info("Gemini OK with model: %s", model_name)
                        return result
                except Exception as exc:
                    logger.warning("Model %s failed: %s", model_name, exc)
                    continue

            return None

        except Exception as exc:
            logger.warning("Gemini analysis failed: %s", exc)
            return None

    # ── helpers ──────────────────────────────────────────────────────────────
    def _parse(self, text: str) -> dict | None:
        """Extract and validate JSON from Gemini's response."""
        try:
            return self._validate(json.loads(text.strip()))
        except (json.JSONDecodeError, ValueError):
            pass
        match = re.search(r'\{.*?\}', text, re.DOTALL)
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
        if not self.characters:
            return FALLBACK[self.lang].format(title=self.title)
        char = random.choice(self.characters)
        return random.choice(TEMPLATES[self.lang]).format(title=self.title, char=char)
