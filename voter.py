from dataclasses import field, dataclass
from typing import Dict

from authentication import AuthenticationStrategy
from political_party import CandidateLevel


@dataclass
class Voter:
    """
    A class representing a voter and their voting-related information.

    Parameters:
        polling_station_name (str): The name of the polling station (ensures voters cannot cast votes at unmatched polling stations).
        voter_name (str): The name of the voter.
        authentication_strategy (AuthenticationStrategy): An authentication strategy
            used to validate voter eligibility.
        _votes (Dict[CandidateLevel, str]): A dictionary storing the voter's votes, initialized as an empty dictionary.
            Keys represent the candidate levels, and values represent the chosen political party.

    Methods:
        __post_init__():
            Initializes the voter's unique identifier after object creation (used to keep a record of which voters have already cast votes - per candidate level).

        authenticate() -> bool:
            Authenticates the voter using the specified authentication strategy.

    Properties:
        votes (Dict[CandidateLevel, str]): A dictionary representing the voter's votes.
            Keys are candidate levels, and values are the chosen political party.

    Example:
        >>> authentication_strategy = ConcreteAuthenticationStrategy()
        >>> voter = Voter("StationA", "John Doe", authentication_strategy)
        >>> voter.authenticate()
        True
    """

    polling_station_name: str
    voter_name: str
    authentication_strategy: AuthenticationStrategy
    _votes: Dict[CandidateLevel, str] = field(default_factory=dict)

    def __post_init__(self):
        self.voter_id = id(self)

    def authenticate(self):
        if not self.authentication_strategy.authenticate():
            return False
        return True

    @property
    def votes(self):
        return self._votes

    @votes.setter
    def votes(self, votes):
        self._votes = votes
