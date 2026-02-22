"""Test implementations of is_won in subclasses of bets.Bet."""

import numpy as np
from elecbet.polls import SimulationResults
import elecbet.bets as bets

# pylint: disable=missing-docstring

def test_highest_share_is_won():
    bet = bets.HighestShare('Party A', odds=2.0)
    results = SimulationResults(
        parties=['Party A', 'Party B', 'Party C'],
        shares=np.array([[0.4, 0.35, 0.25], [0.3, 0.5, 0.2]])
    )
    # The artifical case of duplicate highest shares is not considered
    outcome = bet.is_won(results)
    assert np.array_equal(outcome, np.array([True, False]))

def test_in_range_1_party_is_won():
    bet = bets.InRange(['Party A'], low=0.3, high=0.5, odds=2.0)
    results = SimulationResults(
        parties=['Party A', 'Party B'],
        shares=np.array([[0.4, 0.6], [0.2, 0.8], [0.6, 0.4]])
    )
    outcome = bet.is_won(results)
    assert np.array_equal(outcome, np.array([True, False, False]))

def test_in_range_party_group_is_won():
    bet = bets.InRange(['Party A', 'Party B'], low=0.5, high=0.7, odds=2.0)
    results = SimulationResults(
        parties=['Party A', 'Party B', 'Party C'],
        shares=np.array(
            [[0.40, 0.20, 0.40],
             [0.40, 0.40, 0.20],
             [0.20, 0.20, 0.60],
             [0.30, 0.2001, 0.4999],
             [0.30, 0.1999, 0.5001]]
        )
    )
    outcome = bet.is_won(results)
    assert np.array_equal(outcome, np.array([True, False, False, True, False]))

def test_head_to_head_2_parties_is_won():
    bet = bets.HeadToHead(['Party A'], ['Party B'], odds=2.0)
    results = SimulationResults(
        parties=['Party A', 'Party B', 'Party C'],
        shares=np.array([[0.4, 0.35, 0.25], [0.3, 0.5, 0.2], [0.4, 0.4, 0.2]])
    )
    outcome = bet.is_won(results)
    assert np.array_equal(outcome, np.array([True, False, False]))

def test_head_to_head_2_party_groups_is_won():
    bet = bets.HeadToHead(['Party A', 'Party B'], ['Party C', 'Party D'], odds=2.0)
    results = SimulationResults(
        parties=['Party A', 'Party B', 'Party C', 'Party D', 'Party E'],
        shares=np.array(
            [[0.25, 0.20, 0.20, 0.15, 0.20],
             [0.20, 0.15, 0.25, 0.20, 0.20]]
        )
    )
    # The artifical case of duplicate sums of shares is not tested
    outcome = bet.is_won(results)
    assert np.array_equal(outcome, np.array([True, False, False]))
