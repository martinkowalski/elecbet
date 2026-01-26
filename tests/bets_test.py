"""Test implementations of is_won in subclasses of bets.Bet."""

import numpy as np
from elecbet.polls import SimulationResults
from elecbet.bets import HighestShare

# pylint: disable=missing-docstring

def test_highest_share_is_won():
    bet = HighestShare('Party A', odds=2.0)
    results = SimulationResults(
        parties=['Party A', 'Party B', 'Party C'],
        shares=np.array([[0.4, 0.35, 0.25], [0.3, 0.5, 0.2]])
    )
    # The (artifical) case of duplicate highest shares is not tested
    outcome = bet.is_won(results)
    assert np.array_equal(outcome, np.array([True, False]))
