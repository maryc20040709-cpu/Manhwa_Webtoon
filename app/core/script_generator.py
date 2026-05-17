import random

class ScriptGenerator:
    def __init__(self, title, characters):
        self.title = title
        self.characters = characters

    def generate_dramatic_recap(self):
        if not self.characters:
            return f"In the latest episode of '{self.title}', the story continues..."
        recap_templates = [
            f"In the latest episode of '{self.title}', {random.choice(self.characters)} faces a challenging dilemma that could change everything.",
            f"This week in '{self.title}', tensions rise as {random.choice(self.characters)} needs to make a crucial decision regarding their future.",
            f"The stakes have never been higher in '{self.title}', with {random.choice(self.characters)} caught between friendships and rivalries.",
            f"Emotions run high in '{self.title}', as {random.choice(self.characters)} struggles with personal conflicts that impact their relationships.",
        ]
        return random.choice(recap_templates)
