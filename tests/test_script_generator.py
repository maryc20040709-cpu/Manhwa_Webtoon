from app.core.script_generator import ScriptGenerator

def test_returns_string():
    gen = ScriptGenerator(title="Solo Leveling", characters=["Sung Jinwoo"])
    recap = gen.generate_dramatic_recap()
    assert isinstance(recap, str)
    assert len(recap) > 0

def test_title_in_recap():
    gen = ScriptGenerator(title="Solo Leveling", characters=["Sung Jinwoo"])
    recap = gen.generate_dramatic_recap()
    assert "Solo Leveling" in recap

def test_character_in_recap():
    characters = ["Sung Jinwoo", "Cha Hae-In"]
    gen = ScriptGenerator(title="Solo Leveling", characters=characters)
    recap = gen.generate_dramatic_recap()
    assert any(char in recap for char in characters)

def test_empty_characters():
    gen = ScriptGenerator(title="Tower of God", characters=[])
    recap = gen.generate_dramatic_recap()
    assert isinstance(recap, str)
    assert "Tower of God" in recap

def test_multiple_characters():
    characters = ["Bam", "Khun", "Rak"]
    gen = ScriptGenerator(title="Tower of God", characters=characters)
    recap = gen.generate_dramatic_recap()
    assert any(char in recap for char in characters)
