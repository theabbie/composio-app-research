import pytest

from agent.llm import LLMError, extract_json_object


def test_extract_plain_json() -> None:
    assert extract_json_object('{"a": 1}') == {"a": 1}


def test_extract_json_with_surrounding_text() -> None:
    text = 'Here you go:\n```json\n{"a": "brace } inside"}\n```\nthanks'
    assert extract_json_object(text) == {"a": "brace } inside"}


def test_extract_json_nested() -> None:
    text = '{"a": {"b": [1, 2, {"c": "d"}]}, "e": "}"}'
    assert extract_json_object(text)["a"]["b"][2] == {"c": "d"}


def test_extract_json_missing() -> None:
    with pytest.raises(LLMError):
        extract_json_object("no json at all")


def test_extract_json_unbalanced() -> None:
    with pytest.raises(LLMError):
        extract_json_object('{"a": 1')
