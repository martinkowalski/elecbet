from src.polls import Poll, pool, from_csv
import pytest

def test_poll():
    pl = Poll('2025-05-15', 800, {'party_a': 0.5, 'party_b': 0.4})
    assert pl.results[Poll.OTHERS_KEY] == pytest.approx(0.1, abs=Poll.TOL)

def test_poll_invalid_shares():
    with pytest.raises(ValueError):
        Poll('2025-05-15', 800, {'a': 0.5, 'b': 0.6})

def test_pool():
    # Sample and pooled CSVs were derived from `data/surveys_sample.rda` in
    # `adibender/coalitions` (see also `tests/testthat/test-pooling.R`).
    polls = from_csv('tests/sample_polls.csv')
    act = pool(polls)

    exp_list = from_csv('tests/pooled_poll.csv')
    exp = exp_list[0]

    assert act.results == pytest.approx(exp.results, abs=Poll.TOL)
    assert act.sample_size == pytest.approx(exp.sample_size, abs=Poll.TOL)
    assert act.sample_date == exp.sample_date
    