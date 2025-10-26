"""End-to-end tests for the polls module.

Validate:
- `sample_polls.csv` -> `from_csv` -> `pool` -> compare with `pooled_sample.csv`
- `pooled_sample.csv` -> `from_csv` -> `sim_election` -> compare resulting covariance matrix
    with `pooled_sample_sim_elect_cov.csv`
"""
import numpy as np
import pytest
from elecbet.polls import from_csv, pool, sim_election

def test_from_csv_and_pool():
    """Verify that polls are created correctly from CSV files and pooled as expected.

    Input and expected output data derived from `data/surveys_sample.rda` in
    `adibender/coalitions` (see also `tests/testthat/test-pooling.R`).
    """
    polls = from_csv('tests/testdata/sample_polls.csv')
    act = pool(polls)

    exp_list = from_csv('tests/testdata/pooled_sample.csv')
    exp = exp_list[0]

    assert act.results == pytest.approx(exp.results)
    assert act.sample_size == pytest.approx(exp.sample_size)
    assert act.sample_date == exp.sample_date

def test_sim_election():
    """Test simulation of elections by comparison with reference results.
    
    The credibility of sim_election is determined by comparing party share means and covariance
    with reference values. These were obtained from the MATLAB version of elecbet. Both simulations
    are based on `pooled_sample.csv` pooling results and carried out with the following parameters:
    `nsim = 1_000_000`, `rounding_step = 0.01`.

    Note:
    This is not a full proof of correctness as the reference values are not independently verfied.
    The test only ensures sim_election runs without syntax or major calculation errors.
    """
    # Load reference data
    # Mean values
    ref_file = 'tests/testdata/pooled_sample_sim_elect_mean.csv'
    exp_parties_mean = np.loadtxt(ref_file, delimiter=',', max_rows=1, dtype=str)
    exp_mean = np.loadtxt(ref_file, delimiter=',', skiprows=1)
    # Covariance matrix
    ref_file = 'tests/testdata/pooled_sample_sim_elect_cov.csv'
    exp_parties_cov = np.loadtxt(ref_file, delimiter=',', max_rows=1, dtype=str)
    exp_cov = np.loadtxt(ref_file, delimiter=',', skiprows=1)

    # Simulate elections
    poll = from_csv('tests/testdata/pooled_sample.csv')
    sim_results = sim_election(poll[0], 1_000_000, rounding_step=0.01)

    # Compare with reference values
    # Mean values
    sim_parties = sim_results.parties
    idx_mapping = [sim_parties.index(party) for party in exp_parties_mean]
    reord_shares = sim_results.shares[:, idx_mapping]
    act_mean = np.mean(reord_shares, axis=0)
    assert act_mean == pytest.approx(exp_mean, rel=1e-2)
    # Covariance matrix
    idx_mapping = [sim_parties.index(party) for party in exp_parties_cov]
    reord_shares = sim_results.shares[:, idx_mapping]
    # Covariance obtained from sim_results
    act_cov = np.cov(reord_shares.T)
    assert act_cov == pytest.approx(exp_cov, rel=1e-1)
