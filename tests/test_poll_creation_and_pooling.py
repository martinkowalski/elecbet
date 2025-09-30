"""End-to-end test of poll creation and pooling"""

import pytest
from src.polls import from_csv, pool

def test_from_csv_and_pool():
    """Verify that polls are created correctly from CSV files and pooled as expected.

    Input and expected output data derived from `data/surveys_sample.rda` in
    `adibender/coalitions` (see also `tests/testthat/test-pooling.R`).
    """
    polls = from_csv('tests/sample_polls.csv')
    act = pool(polls)

    exp_list = from_csv('tests/pooled_poll.csv')
    exp = exp_list[0]

    assert act.results == pytest.approx(exp.results)
    assert act.sample_size == pytest.approx(exp.sample_size)
    assert act.sample_date == exp.sample_date
