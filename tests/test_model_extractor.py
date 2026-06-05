from model_extractor import ModelExtractor, extract_mentions


def test_extract_basic_models():
    text = "Claude is better than GPT-4"
    mentions = extract_mentions(text)

    assert len(mentions) == 2
    assert {m.model_name for m in mentions} == {"Claude", "GPT-4"}


def test_extract_case_insensitive():
    mentions = extract_mentions("I prefer gpt-4 and claude")
    assert {m.model_name for m in mentions} == {"Claude", "GPT-4"}


def test_extract_flexible_separators():
    texts = ["GPT-4 is great", "gpt4 works well", "gpt 4 is fast", "GPT 4 version"]
    for text in texts:
        mentions = extract_mentions(text)
        assert len(mentions) == 1
        assert mentions[0].model_name == "GPT-4"


def test_deduplication():
    mentions = extract_mentions("Claude vs Claude, Claude wins")
    assert len(mentions) == 1
    assert mentions[0].model_name == "Claude"


def test_longest_match_first():
    mentions = extract_mentions("Claude 3 is newest")
    assert len(mentions) == 1
    assert mentions[0].model_name == "Claude 3"


def test_multiple_models_same_comment():
    text = "Claude, GPT-4, Llama 3, and Gemini compete in leaderboards"
    mentions = extract_mentions(text)
    assert {m.model_name for m in mentions} == {"Claude", "GPT-4", "Llama 3", "Gemini"}
