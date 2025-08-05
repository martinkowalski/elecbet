"""Manage and pool election polls."""

from dataclasses import dataclass
from datetime import date

PARTY_REST = 'rest'

@dataclass
class Poll():
    """A single election poll.
    
    An election poll conducted by a pollster is defined by its poll date, its sample size, and the
    results. The results consist of parties and their calculated vote shares. Optionally, multiple
    parties that are not further broken down can be submitted as party 'rest' (case-insensitive).
    The share of each party in the results can be passed
    * as fraction in the range [0.0, 1.0]. In this case the sum of all shares must be lower or
      equal than 1.0 (exactly 1.0 if results contain a party 'rest')
    * as percentage in the range [0.0, 100.0]. In this case the sum of all shares must be greater
      than 1.0 and lower or equal than 100.0 (exactly 100.0 if results contain a party 'rest')

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
        rest_included = False
        for party, share in self.results.items():
            if not (0.0 <= share <= 1.0):
                raise ValueError(
                    f'Shares in results must be in the range [0.0, 1.0], '
                    'received {party}: {share}.'
                )
            sum_shares += share
            if party.lower() == PARTY_REST.lower():
                rest_included = True
        if not (0.0 < sum_shares <= 1):
            raise ValueError(
                'Sum of shares in results must be in the range (0.0, 1.0],\n'
                f'received a total of {sum_shares}.')
        if rest_included:
            if sum_shares != 1.0:
                raise ValueError(
                    f"Shares in results must sum up to exactly 1.0 if party '{PARTY_REST}' "
                    f"is included,\nreceived a total of {sum_shares}."
                )
        else:
            self.results[PARTY_REST] = 1.0 - sum_shares
