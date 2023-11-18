from dataclasses import field, dataclass
from typing import Dict

from authentication import AuthenticationStrategy
from political_party import CandidateLevel


@dataclass
class Voter:
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


