# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Martin Kowalski

"""Manage bets on election outcomes.

Functionality:

Examples:

"""

import numpy as np
from numpy.typing import NDArray
from elecbet.polls import SimulationResults


class Bet:
    """Base class for all bet types.
    
    Concrete bet classes must implement `is_won(self, results)`, and should override
    `__str__(self)` for meaningful output in a betting slip.

    Attributes:
        odds: Positive odds.
        bookmaker: Name of the bookmaker.
    """

    def __init__(self, odds: float, bookmaker: str) -> None:
        if odds <= 0.0:
            raise ValueError("odds must be positive")
        self.odds: float = odds
        self.bookmaker: str = bookmaker

    def __str__(self) -> str:
        # Default string representation, override in derived classes
        return self.__class__.__name__

    def is_won(self, results: SimulationResults) -> NDArray[np.bool_]:
        """Evaluate the bet against simulation results.

        Args:
            results: Simulation results to evaluate the bet against.

        Returns:
            Boolean array indicating whether the bet is won in each simulation.
        """
        raise NotImplementedError


class HighestShare(Bet):
    """Bet that a specific party achieves the highest vote share.
    
    Attributes:
        party: Name of the party concerned.
    """

    def __init__(self, party: str, odds: float, bookmaker: str = '') -> None:
        Bet.__init__(self, odds, bookmaker)
        self.party: str = party

    def __str__(self) -> str:
        return f"winner {self.party}"

    def is_won(self, results: SimulationResults) -> NDArray[np.bool_]:
        """True for simulations where the party has the highest vote share.

        The case of an exact tie in vote share between parties is considered practically irrelevant
        and therefore no tie-breaking rule is applied.

        Args:
            results: Simulation results from `nsim` runs.

        Returns:
            Boolean array of length `nsim`.
        """
        if self.party not in results.parties:
            raise ValueError(f"party '{self.party}' not in simulation results")

        return results.shares.argmax(axis=1) == results.parties.index(self.party)


class InRange(Bet):
    """Bet that the total share of one or more parties lies within a specified range.

    Attributes:
        parties: List of party names whose shares are summed.
        low: Lower bound of the range (exclusive).
        high: Upper bound of the range (exclusive).
    """

    def __init__(self,
                 parties: list[str],
                 low: float,
                 high: float,
                 odds: float,
                 bookmaker: str = '') -> None:

        Bet.__init__(self, odds, bookmaker)
        self.parties: list[str] = parties

        if not 0.0 <= low <= 1.0:
            raise ValueError("low must be in [0.0, 1.0]")
        if not 0.0 <= high <= 1.0:
            raise ValueError("high must be in [0.0, 1.0]")
        if low >= high:
            raise ValueError("low must be less than high")
        self.low: float = low
        self.high: float = high

    def __str__(self) -> str:
        parties_str: str = self.parties[0] if len(self.parties) == 1 else f"sum({self.parties})"
        return f"{parties_str} in range ({self.low:.2%}, {self.high:.2%})"

    def is_won(self, results: SimulationResults) -> NDArray[np.bool_]:
        """Evaluate the bet against simulation results.
        
        True for simulations where the total share of the specified parties is strictly within the
        given range.

        Args:
            results: Simulation results from `nsim` runs.

        Returns:
            Boolean array of length `nsim`.
        """
        party_idx: list[int] = []
        for party in self.parties:
            if party not in results.parties:
                raise ValueError(f"party '{party}' not in simulation results")
            party_idx.append(results.parties.index(party))
        res_sums: NDArray = results.shares[:, party_idx].sum(axis=1)

        return (self.low < res_sums) & (res_sums < self.high)


class HeadToHead(Bet):
    """Bet that one party or group of parties achieves a higher total share than another.

    Attributes:
        stronger: List of one or more party names in the 'stronger' group.
        weaker: List of one or more party names in the 'weaker' group.
    """

    def __init__(self,
                 stronger: list[str],
                 weaker: list[str],
                 odds: float,
                 bookmaker: str = '') -> None:

        Bet.__init__(self, odds, bookmaker)

        self.stronger: list[str] = stronger
        self.weaker: list[str] = weaker

    def __str__(self) -> str:
        stronger_str: str = self.stronger[0] if len(self.stronger) == 1 else f"sum({self.stronger})"
        weaker_str: str = self.weaker[0] if len(self.weaker) == 1 else f"sum({self.weaker})"
        return f"{stronger_str} > {weaker_str}"

    def is_won(self, results: SimulationResults) -> NDArray[np.bool_]:
        """Evaluate the bet against simulation results.
        
        True for simulations where the total share of the `stronger` group exceeds that of the
        `weaker` group.

        Args:
            results: Simulation results from `nsim` runs.

        Returns:
            Boolean array of length `nsim`.
        """
        stronger_idx: list[int] = []
        for party in self.stronger:
            if party not in results.parties:
                raise ValueError(f"party '{party}' not in simulation results")
            stronger_idx.append(results.parties.index(party))
        weaker_idx: list[int] = []
        for party in self.weaker:
            if party not in results.parties:
                raise ValueError(f"party '{party}' not in simulation results")
            weaker_idx.append(results.parties.index(party))

        res_stronger: NDArray = results.shares[:, stronger_idx].sum(axis=1)
        res_weaker: NDArray = results.shares[:, weaker_idx].sum(axis=1)

        return res_stronger > res_weaker
