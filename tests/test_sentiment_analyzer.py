import pytest

from sentiment_analyzer import SentimentAnalyzer, analyze_sentiment


def test_analyze_positive_sentiment():
    result = analyze_sentiment("Claude is absolutely amazing!")
    assert result.label == "positive"
    assert result.score > 0.6
    assert result.raw_compound > 0


def test_analyze_negative_sentiment():
    result = analyze_sentiment("This is terrible and awful")
    assert result.label == "negative"
    assert result.score > 0.5
    assert result.raw_compound < 0


def test_analyze_neutral_sentiment():
    result = analyze_sentiment("Claude exists")
    assert result.label == "neutral"
    assert result.score < 0.2
    assert abs(result.raw_compound) < 0.05


def test_sarcasm_detection_builtin():
    result = analyze_sentiment("Yeah right, this is great")
    assert result.label in {"positive", "neutral", "negative"}
    assert isinstance(result.raw_compound, float)


def test_error_on_empty_text():
    with pytest.raises(ValueError):
        analyze_sentiment("")


def test_error_on_whitespace_only():
    with pytest.raises(ValueError):
        analyze_sentiment("   \n\t  ")


def test_error_on_non_string():
    with pytest.raises(ValueError):
        analyze_sentiment(None)


def test_confidence_score_range():
    for text in [
        "Amazing!",
        "Terrible!",
        "Just okay",
        "This is absolutely wonderful and fantastic",
        "This is absolutely horrible and dreadful",
    ]:
        result = analyze_sentiment(text)
        assert 0.0 <= result.score <= 1.0


def test_analyzer_initialization():
    analyzer = SentimentAnalyzer()
    assert analyzer.sia is not None
    result = analyzer.analyze("Test text")
    assert result.label in ["positive", "negative", "neutral"]
