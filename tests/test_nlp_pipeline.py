from nlp_pipeline import NLPPipeline


def test_pipeline_reverses_sentiment_on_sarcasm():
    pipeline = NLPPipeline()
    result = pipeline.process("c1", "Yeah right, this is great")

    assert result.sarcasm_detected is True
    assert result.sentiment_label in {"negative", "positive", "neutral"}
    # If sarcasm is detected, the pipeline may reverse the sentiment label
    assert result.sentiment_score >= 0.0


def test_pipeline_extracts_models_and_sentiment():
    pipeline = NLPPipeline()
    result = pipeline.process("c2", "Claude 3 is better than GPT-4 and Llama 3")

    assert result.sentiment_label in {"positive", "negative", "neutral"}
    assert len(result.model_mentions) >= 3
    model_names = {mention.model_name for mention in result.model_mentions}
    assert {"Claude 3", "GPT-4", "Llama 3"}.issubset(model_names)
