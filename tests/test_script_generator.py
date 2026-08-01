from app.core.script_generator import ScriptGenerator, GeminiAnalyzer

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


# ── GeminiAnalyzer._parse() ──────────────────────────────────────────────
# These exist because of a real incident (Aug 2026): Groq's Qwen 3.6 27B
# model wraps its answer in a <think>...</think> reasoning block by default,
# and the old parser silently failed on that, falling back to the generic
# template recap with no error in the logs. If Groq (or a future model)
# changes its response format again, these tests should catch it in CI
# instead of a user noticing the missing "✦ AI" badge.

analyzer = GeminiAnalyzer()

def test_parse_plain_json():
    text = '{"recap": "A hero rises.", "mood": "action"}'
    assert analyzer._parse(text) == {"recap": "A hero rises.", "mood": "action"}

def test_parse_markdown_fenced_json():
    text = '```json\n{"recap": "A hero rises.", "mood": "action"}\n```'
    assert analyzer._parse(text) == {"recap": "A hero rises.", "mood": "action"}

def test_parse_with_think_tags():
    text = (
        '<think>\nThe user wants a JSON response analyzing an image.\n'
        'Let me look at the panels carefully.\n</think>\n'
        '{"recap": "A hero rises.", "mood": "action"}'
    )
    assert analyzer._parse(text) == {"recap": "A hero rises.", "mood": "action"}

def test_parse_with_preamble_text():
    text = 'Sure! Here is the analysis:\n{"recap": "A hero rises.", "mood": "action"}\nHope that helps!'
    assert analyzer._parse(text) == {"recap": "A hero rises.", "mood": "action"}

def test_parse_invalid_mood_falls_back_to_drama():
    text = '{"recap": "A hero rises.", "mood": "not_a_real_mood"}'
    assert analyzer._parse(text) == {"recap": "A hero rises.", "mood": "drama"}

def test_parse_empty_recap_returns_none():
    text = '{"recap": "", "mood": "action"}'
    assert analyzer._parse(text) is None

def test_parse_truncated_think_block_returns_none():
    # This is exactly what happened in production: the model ran out of
    # tokens mid-reasoning and never emitted the JSON object at all.
    text = (
        '\n<think>\nThe user wants a JSON response analyzing an image.\n'
        'The image provided is just a solid beige background with a thin '
        'white strip at the top. There are absolutely no panels visible. '
        'But wai'
    )
    assert analyzer._parse(text) is None

def test_parse_garbage_text_returns_none():
    assert analyzer._parse("I'm not sure what you mean.") is None
