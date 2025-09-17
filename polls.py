"""Manage and pool election polls."""

# TODO Docstring for pool, summarize steps, mention KOALA papers
# TODO Set up an appropriate repo structure including tests, test data and docs
# TODO Add literature or lit. index to docs
# TODO Add test data and end-to-end test for pool based on coalitions repo data

from collections.abc import Sequence
from csv import DictReader
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, ClassVar
import numpy as np

@dataclass
class Poll():
    """A single election poll.
    
    An election poll is defined by its poll date, sample size, pollster, and party results. Party
    results are fractional vote shares in [0.0, 1.0] mapped to party names. Optionally, multiple
    parties that are not broken down further can be included as party Poll.OTHERS_KEY (case-
    insensitive, for example 'others'). The sum of all shares must be less or equal to 1.0.
    If 'others' is provided, the sum of all shares must be (tolerant of rounding errors) 1.0.
    If 'others' is not provided, its share will be computed such that the sum of shares is equal
    to 1.0.

    Examples:
    Poll('2025-05-15', 800, 'Institute A', {party_a: 0.5, party_b: 0.4, others: 0.1})
    Poll(datetime.date(2025, 5, 15), 800, {party_a: 0.5, party_b: 0.4})
    
    Args:
        sample_date (str, datetime.date, datetime.datetime): date or ISO string 'YYYY-MM-DD'
        sample_size (float): positive sample size
        results (dict[str, float]): Party shares as dict. Key matching 'others' (case-insensitive)
            denotes the bucket for other parties.
        pollster (str, optional): Name of the pollster. Defaults to 'unspecified'.
    
    Raises:
        ValueError: If sample size is non-positive, vote shares are invalid, total shares are out
        of bounds, or multiple definitions of party 'others'.
    """
    OTHERS_KEY: ClassVar[str] = 'others'
    TOL: ClassVar[float] = 1e-6

    sample_date: date
    sample_size: float
    results: dict[str, float] = field(init=False)
    pollster: Optional[str] = None

    def __init__(self,
                 sample_date: str | date | datetime,
                 sample_size: float,
                 shares: dict[str, float],
                 pollster: Optional[str] = None):

        if pollster is None:
            pollster = 'unspecified'
        self.pollster = pollster

        # Convert poll_date
        if isinstance(sample_date, str):
            sample_date = date.fromisoformat(sample_date)
        elif isinstance(sample_date, datetime):
            sample_date = sample_date.date()
        self.sample_date = sample_date

        # Validate sample_size
        if sample_size <= 0.0:
            raise ValueError("sample_size must be positive")
        self.sample_size = sample_size

        # Validate party shares and identify OTHERS_KEY
        sum_shares = 0.0
        others_included = False
        others_key = ''
        for party, share in shares.items():
            # Validate each individual share
            if not 0.0 <= share <= 1.0:
                raise ValueError(
                    "Sharess must be in the range [0.0, 1.0], received '{party}': {share}"
                )
            sum_shares += share
            # Look for OTHERS_KEY (case-insensitive)
            if party.casefold() == Poll.OTHERS_KEY.casefold():
                if others_included:
                    raise ValueError(f"Multiple '{Poll.OTHERS_KEY}' keys found (case "
                                     f"insensitive): {others_key, party}")
                others_included = True
                others_key = party

        # Validate total shares given presence/absence of OTHERS_KEY
        if others_included:
            if not abs(1.0 - sum_shares) < Poll.TOL:
                raise ValueError(
                    f"If party '{others_key}' is included, shares in results must sum up\n"
                    f"to 1.0. Received a total of {sum_shares}."
                )
            others_share: float = shares.pop(others_key) # included below again
        else:
            if not 0.0 < sum_shares <= 1.0 + Poll.TOL:
                raise ValueError("Sum of shares in results must be in the range (0.0, 1.0], "
                                f"received a total of {sum_shares}.")
            others_share = max(1 - sum_shares, 0.0)
            sum_shares += others_share

        # Make sure others_share is included under OTHERS_KEY
        shares[Poll.OTHERS_KEY] = others_share

        if sum_shares > 1.0: # rescale to enforce sum of 1.0 (compensation of rounding errors)
            shares = {party: share / sum_shares for party, share in shares.items()}

        self.results = shares


def from_csv(filepath: str, encoding='utf-8') -> list[Poll]:
    """Create a list of polls from a CSV file.
    
    The CSV file defines one poll per line and must contain the following fieldnames in the header:
    `sample_date`, `sample_size`, and optionally `pollster`. All remaining fields are considered as
    party names.
    """

    polls: list[Poll] = []
    with open(filepath, encoding=encoding, newline='') as csvfile:
        reader = DictReader(csvfile)
        # Check (case insensitive) if the CSV file contains all required fields
        fieldnames: Optional[Sequence[str]] = reader.fieldnames
        if fieldnames is None:
            raise ValueError('invalid header in CSV file')
        act_fields: set[str] = {name.strip().casefold() for name in fieldnames}
        req_fields: set[str] = {'sample_date', 'sample_size'}
        msg_fields: set[str] = req_fields - act_fields
        if len(msg_fields) > 0:
            raise ValueError(f'columns {msg_fields} are missing in the CSV file')
        # Read each line, convert values and create a Poll
        for row in reader:
            row = {key.strip().casefold(): value for key, value in row.items()}
            # Metadata
            sample_date: str = row.pop('sample_date').strip()
            sample_size: float = float(row.pop('sample_size'))
            pollster: Optional[str] = row.pop('pollster', None)
            if pollster is not None:
                pollster = pollster.strip()
            # All remaining elements are considered to be party: share pairs
            shares: dict[str, float] = {party.strip(): float(share) for party, share in row.items()}
            polls.append(Poll(sample_date, sample_size, shares, pollster))

    return polls


def pool(polls: Sequence[Poll]) -> Poll:
    """Aggregate multiple polls into a single pooled poll.

    Args:
        polls (Sequence[Poll]): _description_

    Returns:
        Poll
    """
    if len(polls) == 0:
        raise ValueError('input arg is empty')

    # Party shares and the effective sample size of the pooled survey
    pooled_shares: dict[str, float] = _average_shares(polls)
    leader: str = max(pooled_shares, key=pooled_shares.get) # type: ignore
    lead_shares: list[float] = [poll.results[leader] for poll in polls]
    # Note: The list of sizes passed to _effective_samplesize is based on the pooled share of the
    # leading party, not its actual shares in the individual polls
    lead_sizes: list[float] = [poll.sample_size * pooled_shares[leader] for poll in polls]
    eff_size_leader: float = _effective_samplesize(lead_sizes, lead_shares)
    pooled_size: float = eff_size_leader / pooled_shares[leader]

    # Mean date of the polls
    poll_dates: list[date] = [poll.sample_date for poll in polls]
    mean_ordinal: int = round(sum(dt.toordinal() for dt in poll_dates) / len(poll_dates))
    pooled_date: date = date.fromordinal(mean_ordinal)

    return Poll(pooled_date, pooled_size, pooled_shares, 'pooled')


def _average_shares(polls: Sequence[Poll]) -> dict[str, float]:
    """Return the average share of each party across polls, weighted by sample size."""

    total_size: float = sum(poll.sample_size for poll in polls)
    return {party: sum(poll.results[party] * poll.sample_size for poll in polls) / total_size
            for party in polls[0].results}


def _effective_samplesize(one_party_sizes: list[float],
                          one_party_shares: list[float],
                          corr: float = 0.5,
                          weights_surveys: Optional[list[float]] = None) -> float:
    """Calculate the effective sample size.

    This is the core function that calculates the effective sample size. It is not intended to be
    called directly by the user.

    This function is a port of `effective_samplesize` from `pooling.R` in the GitHub repository
    `adibender/coalitions` (MIT License, (c) 2016-2018 Andreas Bender).

    Args:
        one_party_sizes (list[float]): A vector of sample sizes (number of votes) from different
            surveys (from different pollsters) for one single party.
        one_party_shares (list[float]): The relative shares of votes for the party of interest
            (each value in [0, 1]).
        corr (float, optional): Assumend correlation between surveys from different pollsters.
            Defaults to 0.5.
        weights_surveys (list[float], optional): Additional weights for individual surveys.
            Defaults to None.

    Returns:
        float: The effective sample size.
    """
    # Convert to np.ndarrays for caculations
    # Variable names as used in the original function pooling.R
    size = np.array(one_party_sizes)
    share = np.array(one_party_shares)
    if weights_surveys is None:
        weights = size
    else:
        weights = np.array(weights_surveys)

    # Check values
    n_inst: int = size.size
    if n_inst < 1:
        raise ValueError('size must contain at least one element')
    if n_inst == 1: # return sample size if only one survey/pollster provided
        return int(size[0])
    if (size < 1).any():
        raise ValueError('size must contain only positive values')
    if (share < 0.0).any() or (share > 1.0).any():
        raise ValueError('values in share must be in [0.0, 1.0]')
    if share.size != n_inst:
        raise ValueError('share must contain the same number of elements as size')
    if corr < -1.0 or corr > 1.0:
        raise ValueError('corr must be in the range [-1.0, 1.0]')
    if weights.size != n_inst:
        raise ValueError('if provided, weights must contain the same number of elements as size')

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

# Self-test code
if __name__ == '__main__':
    print('Create single polls:')
    poll1 = Poll('2025-03-05', 800, {'party_a': 0.53, 'party_b': 0.32}, 'Institute_A')
    print(poll1)
    poll2 = Poll('2025-03-06', 600, {'party_a': 0.6, 'Others': 0.4})
    print(poll2)
    print('\nCreate list of polls from CSV file:')
    poll_list = from_csv('surveys_sample2.csv')
    for poll in poll_list:
        print(poll)
    print('\nPool polls:')
    pooled = pool(poll_list)
    print(pooled)

