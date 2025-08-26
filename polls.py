"""Manage and pool election polls."""

from dataclasses import dataclass
from datetime import date
from typing import Optional
import numpy as np

OTHER_PARTIES_NAME = 'others'


@dataclass
class Poll():
    """A single election poll.
    
    An election poll conducted by a pollster is defined by its poll date, its sample size, and the
    results. The results consist of parties and their calculated vote shares. Optionally, multiple
    parties that are not further broken down can be submitted as party 'others' (case-insensitive).
    The share of each party in the results can is passed as fraction in the range [0.0, 1.0]. The
    sum of all shares must be lower or equal than 1.0 (exactly 1.0 if results contain a party
    'others').
    
    Args:
        poll_date (str, date): _description_
        sample_size (int): _description_
        results (dict[str, int | float]): _description_
        pollster (str): _description_
    
    Raises:
        ValueError: _description_
        ValueError: _description_
    """

    poll_date: str | date
    sample_size: int
    results: dict[str, int | float]
    pollster: str = ''

    def __post_init__(self):
        # Convert date if received as str
        if not isinstance(self.poll_date, date):
            self.poll_date = date.fromisoformat(self.poll_date)
        # Check sample_size
        if self.sample_size < 1:
            raise ValueError('sample_size must be a positive integer value')
        self.sample_size = round(self.sample_size)
        # Check shares
        sum_shares = 0.0
        others_included = False
        for party, share in self.results.items():
            if not 0.0 <= share <= 1.0:
                raise ValueError(
                    'Shares in results must be in the range [0.0, 1.0], '
                    f'received {party}: {share}.'
                )
            sum_shares += share
            if party.lower() == OTHER_PARTIES_NAME.lower():
                others_included = True
        if not 0.0 < sum_shares <= 1:
            raise ValueError(
                'Sum of shares in results must be in the range (0.0, 1.0],\n'
                f'received a total of {sum_shares}.'
            )
        if others_included:
            if sum_shares != 1.0:
                raise ValueError(
                    f"Shares in results must sum up to exactly 1.0 if party "
                    f"'{OTHER_PARTIES_NAME}' is included,\nreceived a total of {sum_shares}."
                )
        else:
            self.results[OTHER_PARTIES_NAME] = 1.0 - sum_shares


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

    return round(n_eff)
