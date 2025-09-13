"""Manage and pool election polls."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, ClassVar
from csv import DictReader
import numpy as np

@dataclass
class Poll():
    """A single election poll.
    
    An election poll is defined by its poll date, sample size, pollster, and party results. Party
    results are fractional vote shares in [0.0, 1.0]. Optionally, multiple parties that are not
    broken down further can be included as party Poll.OTHERS_KEY (case-insensitive, for example
    'others'). The sum of all shares must be less or equal to 1.0. If 'others' is provided, the
    sum of all shares must be (tolerant of rounding errors) 1.0 . If 'others' is not provided, its
    share will be computed such that the sum of shares is equal to 1.0.

    Examples:
    Poll('2025-05-15', 800, 'Institute A', party_a=0.5, party_b=0.4, others=0.1)
    Poll(datetime.date(2025, 5, 15), 800, party_a=0.5, party_b=0.4)
    
    Args:
        poll_date (str, datetime.date, datetime.datetime): date or ISO string 'YYYY-MM-DD'
        sample_size (int, float): positive sample size
        pollster (str, optional): Name of the pollster. Defaults to 'unspecified'.
        **results (float): Party shares as keyword args. Key matching 'others' (case-insensitive)
            denotes the bucket for other parties.
    
    Raises:
        ValueError: If sample size is non-positive, vote shares are invalid, or total shares are
            out of bounds, or multiple .
    """
    OTHERS_KEY: ClassVar[str] = 'others'
    TOL: ClassVar[float] = 1e-6

    poll_date: date
    sample_size: int | float
    pollster: str = 'unspecified'
    results: dict[str, float] = field(init=False)

    def __init__(self, poll_date: str | date | datetime, sample_size: int | float,
                 pollster: str = 'unspecified', **results: float):

        self.pollster = pollster

        # Convert poll_date
        if isinstance(poll_date, str):
            poll_date = date.fromisoformat(poll_date)
        elif isinstance(poll_date, datetime):
            poll_date = poll_date.date()
        self.poll_date = poll_date

        # Validate sample_size
        if sample_size <= 0:
            raise ValueError("sample_size must be positive")
        self.sample_size = sample_size

        # Validate party shares and identify OTHERS_KEY
        sum_shares = 0.0
        others_included = False
        others_key = ''
        for party, share in results.items():
            # Validate each individual share
            if not 0.0 <= share <= 1.0:
                raise ValueError("Shares in results must be in the range [0.0, 1.0], "
                                 f"received '{party}': {share}")
            sum_shares += share
            # Look for OTHERS_KEY (case-insensitive)
            if party.lower() == Poll.OTHERS_KEY.lower():
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
            others_share: float = results.pop(others_key) # included below again
        else:
            if not 0.0 < sum_shares <= 1.0 + Poll.TOL:
                raise ValueError("Sum of shares in results must be in the range (0.0, 1.0], "
                                f"received a total of {sum_shares}.")
            others_share = max(1 - sum_shares, 0.0)
            sum_shares += others_share

        # Make sure others_share is included under OTHERS_KEY
        results[Poll.OTHERS_KEY] = others_share

        if sum_shares > 1.0: # rescale to enforce sum of 1.0 (compensation of rounding errors)
            results = {party: share / sum_shares for party, share in results.items()}

        self.results = results


def from_csv(filepath: str, encoding='utf-8') -> list[Poll]:
    """Create a list of polls from a CSV file.

    Args:
        filepath (str): _description_
        encoding (str, optional): _description_. Defaults to 'utf-8'.

    Returns:
        list[Poll]: _description_
    """
    polls: list[Poll] = []
    with open(filepath, encoding=encoding, newline='') as csvfile:
        reader = DictReader(csvfile)
        for data in reader:
            # Convert string values from CSV file if possible to int or float
            for key, value in data.items():
                try:
                    data[key] = int(value)
                except ValueError:
                    try:
                        data[key] = float(value)
                    except ValueError:
                        data[key] = value
            polls.append(Poll(**data)) # type: ignore

    return polls


def pool_surveys(polls: list[Poll]) -> Poll:
    """_summary_

    Args:
        polls (list[Poll]): _description_

    Returns:
        Poll: _description_
    """


def _strongest_party_shares(results: list[dict[str, float]]) -> tuple[str, list[float]]:
    """_summary_

    Args:
        results (list[dict[str, float]]): _description_

    Returns:
        tuple[str, list[float]]: _description_
    """
    strongest = []
    for poll in results:
        strongest.append = max(poll, key=poll.get)
        



    return ('', [])



def _average_shares(results: list[dict[str, float]], sizes: list[int]) -> dict[str, float]:
    """_summary_

    Args:
        results (list[dict[str, float]]): _description_
        sizes (list[int]): _description_

    Returns:
        dict[str, float]: _description_
    """
    total: int = sum(sizes)
    avg_shares: dict[str, float] = {}
    for party in results[0].keys():
        avg_shares[party] = sum(results[i][party] * sizes[i]
                                for i in range(len(results))) / total

    return avg_shares


def _effective_samplesize(sizes_one_party: list[int],
                          shares_one_party: list[float],
                          corr: float = 0.5,
                          weights_surveys: Optional[list[int | float]] = None) -> int:
    """Calculate the effective sample size.

    This is the core function that calculates the effective sample size.
    It is usually not intended to be called directly by the user.

    This function is a port of `effective_samplesize` from `coalitions_pooling.R` in the repository
    `adibender/coalitions` (MIT License, (c) 2016-2018 Andreas Bender).

    Args:
        size (list[int]): A vector of sample sizes from different surveys (from different
            pollsters) for one party.
        share (list[float]): The relative shares of votes for the parties of interest (each value
            in the range [0, 1]).
        corr (float, optional): Assumend correlation between surveys from different pollsters.
            Defaults to 0.5.
        weights (list[int | float], optional): Additional weights for individual surveys.
            Defaults to None.

    Returns:
        int: The effective sample size.
    """
    # Convert to np.ndarrays for caculations
    size = np.array(sizes_one_party)
    share = np.array(shares_one_party)
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
        raise ValueError('Values in share must be in the range [0.0, 1.0]')
    if share.size != n_inst:
        raise ValueError('share must contain the same number of elements as size')
    if corr < -1.0 or corr > 1.0:
        raise ValueError('corr must be in the range [-1.0, 1.0]')
    if weights.size != n_inst:
        raise ValueError('If provided, weights must contain the same number of elements as size')

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
    
    #return round(n_eff)
    return n_eff

# Self-test code
if __name__ == '__main__':
    poll1 = Poll('2025-03-05', 800, 'Institute_A', party_a=0.53, party_b=0.32)
    print(poll1)
    poll2 = Poll('2025-03-06', 600, party_a=0.6, Others=0.4)
    print(poll2)
    poll_list = from_csv('surveys_sample.csv')
    for poll in poll_list:
        print(poll)
