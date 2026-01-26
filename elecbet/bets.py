# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Martin Kowalski

"""Manage bets on election outcomes.

Functionality:

Examples:

"""

from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray
from polls import SimulationResults


class Bet:
    """Base class defining the required functionality of concrete bets.
    
    All derived concrete bet classes must implement the following methods:
    - is_won(self, result)

    A derived concrete bet class should implement a _to_string method for a meaningful output in the
    betting slip.
    """

    def __init__(self, odds: float, bookmaker: str) -> None:
        if odds <= 0.0:
            raise ValueError("odds must be positive")
        self.odds: float = odds
        self.bookmaker: str = bookmaker

    def __str__(self) -> str:
        """Should be overwritten by derived classes."""
        return self.__class__.__name__

    def is_won(self, results: SimulationResults) -> NDArray[np.bool_]:
        """_summary_

        Args:
            results (SimulationResults): _description_

        Returns:
            NDArray[np.bool]: _description_
        """
        raise NotImplementedError


class HighestShare(Bet):
    """_summary_

    Args:
        Bet (_type_): _description_
    """

    def __init__(self, party: str, odds: float, bookmaker: str = '') -> None:
        Bet.__init__(self, odds, bookmaker)
        self.party: str = party

    def _str__(self) -> str:
        return f"winner {self.party}"

    def is_won(self, results: SimulationResults) -> NDArray[np.bool_]:
        """_summary_

        Args:
            results (SimulationResults): _description_

        Returns:
            NDArray[np.bool_]: _description_
        """
        if self.party not in results.parties:
            raise ValueError(f"party '{self.party}' not in simulation results")

        return results.shares.argmax(axis=0) == results.parties.index(self.party)


class InRange(Bet):
    """_summary_

    Args:
        Bet (_type_): _description_
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
        """_summary_

        Args:
            results (SimulationResults): _description_

        Returns:
            NDArray[np.bool_]: _description_
        """
        party_idx: list[int] = []
        for party in self.parties:
            if party not in results.parties:
                raise ValueError(f"party '{party}' not in simulation results")
            party_idx.append(results.parties.index(party))
        res_sums: NDArray = results.shares[:, party_idx].sum(axis=0)

        return (self.low < res_sums) & (res_sums < self.high)


class HeadToHead(Bet):
    """_summary_

    Args:
        Bet (_type_): _description_
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
        """_summary_

        Args:
            results (SimulationResults): _description_

        Returns:
            NDArray[np.bool_]: _description_
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

        res_stronger: NDArray = results.shares[:, stronger_idx].sum(axis=0)
        res_weaker: NDArray = results.shares[:, weaker_idx].sum(axis=0)

        return res_stronger > res_weaker
