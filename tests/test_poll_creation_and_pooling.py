"""End-to-end test of poll creation and pooling"""

import numpy as np
import pytest
from src.polls import from_csv, pool, sim_election

def test_from_csv_and_pool():
    """Verify that polls are created correctly from CSV files and pooled as expected.

    Input and expected output data derived from `data/surveys_sample.rda` in
    `adibender/coalitions` (see also `tests/testthat/test-pooling.R`).
    """
    polls = from_csv('tests/sample_polls.csv')
    act = pool(polls)

    exp_list = from_csv('tests/pooled_sample.csv')
    exp = exp_list[0]

    assert act.results == pytest.approx(exp.results)
    assert act.sample_size == pytest.approx(exp.sample_size)
    assert act.sample_date == exp.sample_date

def test_sim_election():
    """Test simulation of elections based on pooled_sample.csv pooling results.
    
    The correctness of the simulation is determined by comparing the covariance matrix resulting
    from the simulation result.
    """
    # Load validation data
    val_data_file = 'tests/pooled_sample_simulation_covariance.csv'
    exp_parties = np.loadtxt(val_data_file, delimiter=',', max_rows=1, dtype=str)
    exp_cov = np.loadtxt(val_data_file, delimiter=',', skiprows=1)
    # Simulate elections from pooled sample
    poll = from_csv('tests/pooled_sample.csv')
    sim_results, sim_parties = sim_election(poll[0], 1_000_000, rounding_step=0.01)
    # Reorder sim_results to match the order of exp_parties
    idx_mapping = [sim_parties.index(party) for party in exp_parties]
    reord_results = sim_results[:, idx_mapping]
    act_cov = np.cov(reord_results.T)
    assert act_cov == pytest.approx(exp_cov, rel=1e-1)
    # TODO add comparison of mean values
    # TODO find names for csv data files
