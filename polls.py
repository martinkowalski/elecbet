"""Manage and pool election polls."""

from dataclasses import dataclass
from datetime import date

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
        # Check sum of shares
        sum_shares = sum(share for share in self.results.values())
        if sum_shares < 0 or sum_shares > 100:
            raise ValueError(
                'Sum of shares in results must be in the range [0.0, 100.0],\n'
                f'received a total of {sum_shares}.')
        rest_included = any(party.lower() == 'rest' for party in self.results)
        if sum_shares <= 1.0
        if rest_included and sum_shares != 100:
            raise ValueError(
                "Shares in results must sum up to exactly 100.0 if party 'rest' is included,\n"
                f"received a total of {sum_shares}."
            )
        elif 
        if sum_shares <= 1.0: # shares accidentally passed als fractions <= 1.0?
            print(
                'Warning: Shares are expected to be passed as percentages in the range [0.0, 100.0].\n'
                f'A total value of only {sum_shares} was received.'
            )
        if not rest_included:
            self.results['rest']
    
        
        
        
