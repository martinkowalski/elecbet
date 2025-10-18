# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Martin Kowalski
# Portions of this file are based on code from the `adibender/coalitions` project,
# Copyright (c) 2016–2018 Andreas Bender, MIT License.

"""Manage and pool election polls, simulate election outcomes.

Functionality:
- Poll: Class that stores metadata and results of an election poll in a multi-party system.
- from_csv: Create polls from a CSV file.
- pool: Aggregate multiple polls into a single pooled poll.
- sim_election: Run a Monte Carlo simulation of election outcomes.

The methods implemented in this module, particularly `pool` and `sim_election`, are based
on the framework described in:
    Bauer, A., Bender, A., Klima, A. et al. KOALA: a new paradigm for election coverage.
    AStA Adv Stat Anal 104, 101-115 (2020). https://doi.org/10.1007/s10182-019-00352-6

Example:
    >>> from polls import Poll, from_csv, pool, sim_election
    >>> # Create
    >>> poll = Poll('2025-05-15', 800, {'party_a': 0.5, 'party_b': 0.4}, 'Institute A')
    >>> prev_polls = from_csv('path_to/poll_data.csv') # must contain party_a, party_b
    >>> polls = prev_polls + [poll]
    >>> # Pool
    >>> pooled_poll = pool(polls)
    >>> # Simulate
    >>> sim_results, parties = sim_election(pooled_poll, rounding_step=0.01)
"""

from collections.abc import Sequence
from csv import DictReader
from datetime import date, datetime
from typing import ClassVar, Any
import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]

class Poll:
    """Metadata and results of an election poll in a multi-party system.
    
    An election poll includes the attributes `sample_date`, `sample_size`, `pollster`, and
    `results`. `results` are fractional vote shares in the range [0.0, 1.0] mapped to party names.
    Optionally, multiple parties that are not reported individually can be included as party
    `Poll.OTHERS_KEY` (case-insensitive, for example 'others').
    
    The sum of all shares must be less than or equal to 1.0. If 'others' is provided, the sum of
    all shares must be (tolerant of rounding errors) 1.0. If 'others' is not provided, its share
    will be computed such that the sum of shares is equal to 1.0.

    `sample_size` usually represents the number of respondents. It must be positive, but it can
    also be a representative non-integer value.

    Properties:
    - parties (list[str]): List of party names derived from poll `results`.
    - shares (list[float]): List of party shares derived from poll `results`.

    Args:
        sample_date (str | datetime.date | datetime.datetime): Date or ISO string 'YYYY-MM-DD'.
        sample_size (float): A positive sample size.
        results (dict[str, float]): Poll results given as party: share pairs. Key matching 'others'
            (case-insensitive) represents the aggregate share of all other parties.
        pollster (str, optional): Name of the polling agency. Defaults to 'unspecified'.
    
    Raises:
        ValueError: If `sample_size` is non-positive, vote shares are invalid, total shares are out
            of bounds, or multiple definitions of party 'others' are provided.
    
    Examples:
        >>> p1 = Poll('2025-05-15', 800, {'Party a': 0.5, 'Party b': 0.4, 'others': 0.1}, 'InstX')
        >>> p2 = Poll(datetime.date(2025, 5, 15), 800, {'party_a': 0.5, 'party_b': 0.4})
        >>> p2.shares
        [0.5, 0.4, 0.1]
    """
    OTHERS_KEY: ClassVar[str] = 'others'
    _TOL: ClassVar[float] = 1e-6

    def __init__(self,
                 sample_date: str | date | datetime,
                 sample_size: float,
                 results: dict[str, float],
                 pollster: str = 'unspecified') -> None:

        self.sample_date: date = self._coerce_to_date(sample_date)
        if sample_size <= 0.0:
            raise ValueError("sample_size must be positive")
        self.sample_size = sample_size
        # Convert shares to ratios if given as percentages
        if any(share > 1.0 for share in results.values()):
            results = {party: share / 100.0 for party, share in results.items()}
        self._validate_results(results)
        self.results = self._normalize_results(results)
        self.pollster = pollster

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}("
                f"sample_date={self.sample_date!r}, "
                f"sample_size={self.sample_size!r}, "
                f"results={self.results!r}, "
                f"pollster={self.pollster!r})")

    def __str__(self) -> str:
        width: int = max(len(name) for name in self.results.keys()) + 2
        desc: str = f"{self.pollster}, {self.sample_date}, size = {self.sample_size:.2f}"
        for party, share in self.results.items():
            desc += f"\n{party:>{width}}: {share:.2%}"
        return desc

    @property
    def parties(self) -> list[str]:
        """Polled parties"""
        return list(self.results.keys())

    @property
    def shares(self) -> list[float]:
        """Party share ratios"""
        return list(self.results.values())

    @staticmethod
    def _coerce_to_date(sample_date: str | date | datetime) -> date:
        """Return given sample_date as datetime.date."""
        if isinstance(sample_date, datetime):
            sample_date = sample_date.date()
        elif not isinstance(sample_date, date): # -> sample_date should be a str
            sample_date = date.fromisoformat(sample_date)
        return sample_date

    @classmethod
    def _validate_results(cls, results: dict[str, float]) -> None:
        """Validate party names and shares in given results.
        The passed results must contain shares as ratios.
        
        Check:
        - At most one Poll.OTHERS_KEY in parties (case-insensitive)
        - 0 <= share <= 1
        - sum(shares) == 1 if OTHERS_KEY in parties
        - sum(shares) <= 1 if OTHERS_KEY not in parties

        Raise ValueError if a condition is not met.
        """
        # Validate individual share ratios
        for party, share in results.items():
            if not 0.0 <= share <= 1.0:
                raise ValueError(f"share ratios must be in the range [0.0, 1.0], "
                                 f"received '{party}': {share}")
        # Ensure parties in results are strings and check for multiple definitions of OTHERS_KEY
        given_others_key = ''
        for party in results:
            if not isinstance(party, str):
                raise ValueError(f"party names in results must be strings, received {party}")
            if cls.OTHERS_KEY.lower() == party.strip().lower():
                if given_others_key:
                    raise ValueError(f"multiple '{cls.OTHERS_KEY}' keys found (case "
                                     f"insensitive): {given_others_key}, {party}")
                given_others_key = party
        # Validate total shares given presence/absence of OTHERS_KEY
        sum_shares: float = sum(results.values())
        if given_others_key:
            if abs(1.0 - sum_shares) > cls._TOL:
                raise ValueError(f"If party '{given_others_key}' is included, share ratios from "
                                 f"results must sum up to 1.0.\nReceived a total of {sum_shares}.")
        else:
            if sum_shares > 1.0 + cls._TOL:
                raise ValueError("sum of share ratios must be <= 1.0, "
                                 f"received a total of {sum_shares}")

    @classmethod
    def _normalize_results(cls, results: dict[str, float]) -> dict[str, float]:
        """Normalize party names and shares in results and return as new dict.
        The passed results must contain shares as ratios.

        - Party names: Make sure Poll.OTHERS_KEY is included
        - Shares:
            1. Normalize shares to [0.0, 1.0] if given as percentages
            2. Make sure party Poll.OTHERS_KEY and its share ratio are included
            3. Rescale share ratios to a total of 1.0
        """
        # Detect if others_key is included (case-insensitive) in parties
        norm_parties: list[str] = []
        others_included = False
        for party in results:
            if cls.OTHERS_KEY.lower() == party.strip().lower():
                # Make sure others_key is included as Poll.OTHERS_KEY
                party = cls.OTHERS_KEY
                others_included = True
            norm_parties.append(party)

        norm_shares: list[float] = list(results.values())
        sum_shares: float = sum(norm_shares)
        if not others_included:
            # Compute share ratio of party Poll.OTHERS_KEY and append party and share
            others_share = 1.0 - sum_shares
            if others_share < cls._TOL:
                others_share = 0.0
            norm_shares.append(others_share)
            norm_parties.append(cls.OTHERS_KEY)
            sum_shares += others_share
        # Rescale share ratios to a total of 1.0
        norm_shares = [share / sum_shares for share in norm_shares]

        return dict(zip(norm_parties, norm_shares))


def from_csv(filepath: str, encoding='utf-8', **kwargs) -> list[Poll]:
    """Create polls from a CSV file.
    
    Each line in the CSV file contains data of a single poll. The header must specify the
    following metadata:
    - sample_date (required)
    - sample_size (required)
    - pollster (optional)

    All other columns are interpreted as party names and their corresponding vote shares.

    Example CSV file:
    ```
    pollster,sample_date,sample_size,party_a,party_b,others
    Institute_A,2025-02-10,800,0.60,0.30,0.10
    Institute_B,2025-02-15,600,0.55,0.25,0.20
    ```

    Args:
        filepath (str): Path to the CSV file.
        encoding (str, optional): Encoding of the CSV file. Defaults to 'utf-8'.
        **kwargs: Additional keyword arguments to pass to `csv.DictReader()`.

    Raises:
        ValueError: If the header is invalid, parties are missing, party names are duplicated, or
            share values are invalid.

    Returns:
        list[Poll]: List of created `Poll` objects.
    """
    polls: list[Poll] = []
    with open(filepath, encoding=encoding, newline='') as csvfile:
        reader = DictReader(csvfile, restval='', **kwargs)
        column_map = _parse_csv_header(reader.fieldnames) # canonical -> actual names
        # Read each line, try to convert values and create a Poll
        for line_no, row in enumerate(reader, 2):
            try:
                data: dict = _parse_csv_row(row, column_map)
                if not data:
                    continue
                polls.append(Poll(**data))
            except ValueError as e:
                raise ValueError(f"invalid data in line {line_no}: {e}") from e

    return polls

def _parse_csv_header(fieldnames: Sequence[str] | None) -> dict[str, Any]:
    """Validate CSV header and return a map of canonical keys to actual columns."""

    if fieldnames is None:
        raise ValueError('invalid header in CSV file')
    fieldnames = list(fieldnames)
    norm_names: list[str] = [name.lower().strip() for name in fieldnames]
    # Required metadata columns
    for key in ('sample_date', 'sample_size'):
        if key not in norm_names:
            raise ValueError(f"column '{key}' is missing in the CSV file")
    sample_date: str = fieldnames[norm_names.index('sample_date')]
    sample_size: str = fieldnames[norm_names.index('sample_size')]
    pollster: str = (fieldnames[norm_names.index('pollster')]
                     if 'pollster' in norm_names else '')
    meta: list[str] = [sample_date, sample_size]
    if pollster:
        meta.append(pollster)
    # All remaining fields must be names of parties
    parties: list[str] = [name for name in fieldnames if name not in meta]
    if len(parties) != len(set(name.strip() for name in parties)):
        raise ValueError("duplicate party names in the header of the CSV file")

    return {'sample_date': sample_date,
            'sample_size': sample_size,
            'pollster': pollster,
            'parties': parties}

def _parse_csv_row(row: dict[str, str], column_map: dict[str, Any]) -> dict[str, Any]:
    """Parse a CSV row into Poll kwargs."""

    if not any(val.strip() for val in row.values()):
        return {}
    # Metadata
    data: dict[str, Any] = {
        'sample_date': date.fromisoformat(row[column_map['sample_date']].strip()),
        'sample_size': float(row[column_map['sample_size']].strip())
    }
    if column_map['pollster']:
        pollster: str = row.get(column_map['pollster'], '').strip()
        if pollster:
            data['pollster'] = pollster
    # Party shares
    data['results'] = {party.strip(): float(row[party].strip()) for party in column_map['parties']}

    return data


def pool(polls: Sequence[Poll], pollster_corr: float = 0.5) -> Poll:
    """Aggregate multiple polls into a single pooled poll.

    All given polls must include the same parties. Furthermore, for meaningful results, the
    following conditions should be met:
    - All polls were conducted within a limited time span (for example, 14 days).
    - Polls come from different polling agencies.
    
    The pooling is done in the following steps (for more details, see the module-level reference):
    1. Compute the pooled shares as weighted average shares of each party across polls:  
        `total_size = sum(poll.sample_size for poll in polls)`  
        `pooled_shares[party] = sum(poll.results[party] * poll.sample_size / total_size
                                    for poll in polls)`
    2. Determine the leading party (with the highest average share) and its polled shares across
       all polls.
    3. Calculate the sizes (hypothetical vote counts) of the leading party across all `np` polls:  
        `leader_sizes[i] = polls[i].sample_size * pooled_shares[leader], i = 0, ..., np`
    4. Compute the effective sample size of the leading party, taking into account correlations
       between different polling agencies:  
        `eff_size_leader = _effective_samplesize(leader_sizes, leader_shares, pollster_corr)`
    5. Calculate the effective sample size of the pooled poll  
        `pooled_size = eff_size_leader / pooled_shares[leader]`
    6. Calculate the pooled sample date as the mean of all poll sample dates.
    7. Create and return the pooled poll
        `Poll(sample_date = pooled_date, sample_size = pooled_size, results = pooled_shares,
         pollster = 'pooled')`

    Args:
        polls (Sequence[Poll]): A list of polls, each containing the same parties.
        pollster_corr (float, optional): Assumed correlation between polls from different
            pollsters, passed to _effective_samplesize. Defaults to 0.5.

    Returns:
        Poll: The aggregated poll.
    """
    # Check polls
    if not polls:
        raise ValueError('polls must not be empty')
    if len(polls) == 1:
        return Poll(polls[0].sample_date, polls[0].sample_size,
                    polls[0].results, polls[0].pollster)

    # Check if all polls contain the same parties
    parties_0: set = set(polls[0].parties)
    for i in range(1, len(polls)):
        parties_i: set = set(polls[i].parties)
        if parties_i != parties_0:
            raise ValueError(f"Parties in\npolls[{i}]: {parties_i}\n are not equal to "
                             f"parties in\npolls[0]: {parties_0}.")

    # 1. Compute pooled shares of each party in polls
    total_size: float = sum(poll.sample_size for poll in polls)
    pooled_shares: dict[str, float] = {
        party: sum(poll.results[party] * poll.sample_size for poll in polls) / total_size
        for party in polls[0].results
    }
    # 2. Determine the leading party and its shares across all polls
    leader: str = max(pooled_shares, key=pooled_shares.get) # type: ignore
    leader_shares: list[float] = [poll.results[leader] for poll in polls]

    # 3. Calculate the sizes of the leading party across all polls. Note: This sizes are based on
    # based on the pooled share of the leading party, not its actual shares in the individual polls
    leader_sizes: list[float] = [poll.sample_size * pooled_shares[leader] for poll in polls]

    # 4. Calculate the effective sample size of the leading party
    eff_size_leader: float = _effective_samplesize(leader_sizes, leader_shares, pollster_corr)
    # 5. Calculate the effective sample size of the pooled poll
    pooled_size: float = eff_size_leader / pooled_shares[leader]

    # 6. Calculate the pooled sample date
    sample_dates: list[date] = [poll.sample_date for poll in polls]
    mean_ordinal: int = round(sum(dt.toordinal() for dt in sample_dates) / len(sample_dates))
    pooled_date: date = date.fromordinal(mean_ordinal)

    return Poll(pooled_date, pooled_size, pooled_shares, 'pooled')

def _effective_samplesize(one_party_sizes: list[float],
                          one_party_shares: list[float],
                          corr: float = 0.5,
                          survey_weights: list[float] | None = None) -> float:
    """Compute the effective sample size for a single party.

    This is the core function that calculates the effective sample size. It is not intended to be
    called directly by the user.

    This function is a port of `effective_samplesize` from `pooling.R` in the GitHub repository
    `adibender/coalitions` (MIT License, (c) 2016-2018 Andreas Bender). See also the
    module-level reference.

    Args:
        one_party_sizes (list[float]): A vector of sample sizes (number of votes) from different
            surveys (from different pollsters) for one single party.
        one_party_shares (list[float]): The relative shares of votes for the party of interest
            (each value in the range [0, 1]).
        corr (float, optional): Assumed correlation between surveys from different pollsters.
            Defaults to 0.5.
        survey_weights (list[float], optional): Additional weights for individual surveys.
            Defaults to None, in this case `survey_weights = one_party_sizes` will be assigned.

    Returns:
        float: The effective sample size.
    """
    # Convert to np.ndarrays for calculations
    # Variable names as used in the original function pooling.R
    size: FloatArray = np.array(one_party_sizes)
    share: FloatArray = np.array(one_party_shares)
    weights: FloatArray
    if survey_weights is None:
        weights = size
    else:
        weights = np.array(survey_weights)

    # Check values
    n_inst: int = size.size
    if n_inst < 1:
        raise ValueError("size must contain at least one element")
    if n_inst == 1: # return sample size if only one survey/pollster provided
        return size[0]
    if (size < 1).any():
        raise ValueError("size must contain only positive values")
    if (share < 0.0).any() or (share > 1.0).any():
        raise ValueError("values in share must be in the range [0.0, 1.0]")
    if share.size != n_inst:
        raise ValueError("share must contain the same number of elements as size")
    if corr < -1.0 or corr > 1.0:
        raise ValueError("corr must be in the range [-1.0, 1.0]")
    if weights.size != n_inst:
        raise ValueError("if provided, weights must contain the same number of elements as size")

    # Calculation
    sum_weights = weights.sum()
    p_total = (weights * share).sum() / sum_weights
    var_ind = p_total * (1.0 - p_total)
    # n_total = sum(size)   not required
    var_vec = share * (1 - share) / size
    sd_vec = np.sqrt(var_vec)
    n_comb = 0
    for i in range(n_inst - 1, 0, -1):
        n_comb += i
    cov_vec = np.full(n_comb, np.nan)
    n_cov_vec = cov_vec.copy()
    k = n_inst - 1
    count = 1
    while k > 0:
        cov_vec[(count - 1):(count + k - 1)] = corr * sd_vec[0:k] * sd_vec[(n_inst - k):n_inst]
        n_cov_vec[(count - 1):(count + k - 1)] = weights[0:k] * weights[(n_inst - k):n_inst]
        count += k
        k -= 1
    var_est = 1 / (weights.sum() ** 2) * (((weights ** 2) * var_vec).sum()
                                          + (2 * n_cov_vec * cov_vec).sum())
    n_eff = var_ind / var_est

    return float(n_eff)


def sim_election(poll: Poll, nsim: int,
                 rounding_step: float = 0.0) -> tuple[FloatArray, list[str]]:
    """Run a Monte Carlo simulation of election outcomes.

    Draw `nsim` samples of party vote shares for the `np` parties in `poll` using a Dirichlet
    distribution according to the KOALA model (see the module-level reference). Return simulation
    results as tuple `(results, parties)`. `results` is an np.ndarray of shape `(nsim, np)`,
    `parties` is a list of `np` party names. Thus, `results[i, j]` is the share of `parties[j]` in
    simulation `i`.

    Poll results are often published as rounded values. To account for the loss of information, set
    `rounding_step > 0.0`, indicating that `poll.shares` are based on values rounded to multiples
    of `rounding_step` (for example, `rounding_step = 0.01` corresponds to rounding to whole
    percentage points).
    - If `rounding_step > 0.0`, in every simulation i.i.d. uniform noise in the range
      `[-rounding_step/2, +rounding_step/2]` is added to `poll.shares`. The perturbed shares are
      then clipped to the range [0, 1] and renormalized to sum to 1.0.
    - If `rounding_step <= 0`, no perturbation is applied and all results are drawn based on the
      same base shares (`poll.shares`).

    Args:
        poll (Poll): The poll providing the input data for the simulation. Typically created by
            aggregating multiple polls using `pool(polls)`.
        nsim (int): Number of independent election outcomes (party shares) to create.
        rounding_step (float, optional): Increment to which the shares of the input `poll` (or
            those of its underlying aggregated polls) have been rounded. A non-positive value
            disables rounding compensation. Defaults to 0.0.

    Returns:
        tuple[FloatArray, list[str]]: Simulation `results` (shape `(nsim, np)`) and names of
            `parties` (length `np`). `results[i, j]` is the share of `parties[j]` in
            simulation `i`.
    """
    base_shares: FloatArray = np.array(poll.shares)
    alpha: FloatArray
    rng = np.random.default_rng()

    if rounding_step <= 0.0: # no rounding compensation
        alpha = base_shares * poll.sample_size + 0.5
        return rng.dirichlet(alpha, size=nsim), poll.parties

    # rounding_step > 0.0 => apply rounding compensation
    # Ensure that below not all noisy_shares can become 0.0 after clipping
    delta: float = rounding_step / 2
    if (base_shares <= delta).all():
        raise ValueError(f"rounding_step/2 = {delta} >= all shares in the given poll")
    # Add noise and renormalize shares
    noisy_shares: FloatArray = base_shares + rng.uniform(-delta, delta,
                                                           size=(nsim, base_shares.size))
    noisy_shares = noisy_shares.clip(0.0, 1.0)
    noisy_shares /= noisy_shares.sum(axis=1, keepdims=True)
    alpha = noisy_shares * poll.sample_size + 0.5
    # Because rng.dirichlet accepts only a single alpha vector, use rng.gamma to generate
    # dirichlet distributed results from per-sample alpha (matrix)
    # (see https://en.wikipedia.org/wiki/Dirichlet_distribution for details)
    gam_draws: FloatArray = rng.gamma(alpha)

    return gam_draws / gam_draws.sum(axis=1, keepdims=True), poll.parties
