import random

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
        "Die Emotionen kochen über in '{title}', als {char} mit inneren Konflikten kämpft, die alles auf den Kopf stellen.",
    ],
    "ru": [
        "В последней главе «{title}» {char} оказывается перед трудной дилеммой, способной изменить всё.",
        "На этой неделе в «{title}» напряжение нарастает: {char} должен принять судьбоносное решение.",
        "Ставки как никогда высоки в «{title}» — {char} оказался между дружбой и соперничеством.",
        "В «{title}» кипят страсти: {char} борется с внутренними противоречиями, затрагивающими всех вокруг.",
    ],
}

FALLBACK = {
    "en": "In the latest episode of '{title}', the story continues with unexpected twists.",
    "de": "In der neuesten Episode von '{title}' nimmt die Geschichte eine unerwartete Wendung.",
    "ru": "В последней главе «{title}» история делает неожиданный поворот.",
}

class ScriptGenerator:
    def __init__(self, title: str, characters: list, lang: str = "en"):
        self.title = title
        self.characters = characters
        self.lang = lang if lang in TEMPLATES else "en"

    def generate_dramatic_recap(self) -> str:
        if not self.characters:
            return FALLBACK[self.lang].format(title=self.title)
        templates = TEMPLATES[self.lang]
        char = random.choice(self.characters)
        return random.choice(templates).format(title=self.title, char=char)
