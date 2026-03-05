import pytest

from app import parse_int_field


def test_parse_valid_int():
    assert parse_int_field('123', 'cat') == 123
    assert parse_int_field(456, 'cat') == 456


def test_parse_empty_or_none():
    assert parse_int_field('', 'cat') is None
    assert parse_int_field(None, 'cat') is None


def test_parse_invalid_string_returns_none():
    # Non-numeric values should not raise, but return None
    assert parse_int_field('watch', 'category') is None
    assert parse_int_field('12.3', 'category') is None
