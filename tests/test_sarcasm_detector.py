from sarcasm_detector import detect_sarcasm, SarcasmDetector


def test_detect_yeah_right():
    result = detect_sarcasm("Yeah right, that's totally true")
    assert result.detected is True
    assert "yeah-right" in result.patterns_matched


def test_detect_oh_exclamation():
    for text in ["Oh great, another bug", "Oh wonderful, this broke", "Oh perfect, just what I needed"]:
        result = detect_sarcasm(text)
        assert result.detected is True
        assert "oh-exclamation" in result.patterns_matched


def test_detect_sure_buddy():
    for text in ["Sure buddy, that'll work", "Sure jan, keep telling yourself that", "Sure thing, and I'm the Pope"]:
        result = detect_sarcasm(text)
        assert result.detected is True
        assert "sure-buddy" in result.patterns_matched


def test_detect_multiple_punctuation():
    for text in ["Really?? No way!!", "Sure!!!", "What??!!??"]:
        result = detect_sarcasm(text)
        assert result.detected is True
        assert "multiple-punctuation" in result.patterns_matched


def test_no_sarcasm_in_normal_text():
    for text in ["This is actually great", "I really like Claude", "GPT-4 works well"]:
        result = detect_sarcasm(text)
        assert result.detected is False


def test_custom_patterns():
    detector = SarcasmDetector([(r"\byikes\b", "yikes")])
    result = detector.detect("Yikes, that's bad")
    assert result.detected is True
    assert "yikes" in result.patterns_matched


def test_empty_text():
    result = detect_sarcasm("")
    assert result.detected is False
    assert result.patterns_matched == []
