"""Test polls.Poll construction."""

import datetime as dt
import pytest
from src.polls import Poll

# pylint: disable=missing-docstring

def test_poll_from_share_ratios_with_others():
    poll = Poll('2025-05-15', 0.5, {'Party A': 0.4, 'Party B': 0.5, 'OthErS': 0.1})
    assert poll.sample_date == dt.date(2025, 5, 15)
    assert poll.sample_size == 0.5
    assert poll.results['Party A'] == pytest.approx(0.4)
    assert poll.results['Party B'] == pytest.approx(0.5)
    assert poll.results[Poll.OTHERS_KEY] == pytest.approx(0.1)

def test_poll_from_share_ratios_without_others():
    poll = Poll('2025-05-15', 800, {'a': 0.5, 'b': 0.4999}, 'X')
    assert poll.pollster == 'X'
    assert poll.parties == ['a', 'b', Poll.OTHERS_KEY]
    assert poll.shares == pytest.approx([0.5000, 0.4999, 0.0001])

def test_poll_from_share_percentages():
    poll = Poll('2025-05-15', 800, {'a': 0.5, 'b': 49.99}, 'X')
    assert poll.results == pytest.approx({'a': 0.5, 'b': 0.4999, 'others': 0.4501})

def test_raise_on_invalid_sample_size():
    with pytest.raises(ValueError, match="sample_size"):
        Poll('2025-05-15', 0, {'a': 0.4, 'b': 0.5})

def test_raise_on_negative_share_ratio():
    with pytest.raises(ValueError, match="must be in the range"):
        Poll('2025-05-15', 1000, {'a': -0.1, 'b': 0.5})

def test_raise_on_multiple_others_keys():
    with pytest.raises(ValueError, match=f"Multiple '{Poll.OTHERS_KEY}' keys"):
        Poll('2025-05-15', 1000, {'a': 0.5, 'others': 0.3, 'OTHERS': 0.2})

def test_total_share_ratios_exceed_one():
    with pytest.raises(ValueError, match="must be <= 1.0"):
        Poll('2025-05-15', 1000, {'a': 0.5000, 'b': 0.5001})

def test_total_share_ratios_with_others_not_one():
    others_key = 'Others'
    with pytest.raises(ValueError, match=f"If party '{others_key}' is included"):
        Poll('2025-05-15', 1000, {'a': 0.4, 'b': 0.4, others_key: 0.1999})

def test_total_share_percentages_exceed_100():
    with pytest.raises(ValueError, match="must be <= 1.0"):
        Poll('2025-05-15', 1000, {'a': 50.00, 'b': 50.01})

