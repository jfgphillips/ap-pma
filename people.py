import enum
from dataclasses import dataclass
from enum import Enum


class PCO:
    pass

@enum.unique
class CandidateLevel(Enum):
    PRESIDENT = enum.auto()
    GOVERNOR = enum.auto()
    MAYOR = enum.auto()
    MP = enum.auto()

@dataclass
class Candidate:
    level: CandidateLevel
    name: str
    party = None
    votes = 0

@dataclass
class PoliticalParty:
    party_name: str
    candidates = []

    def register(self, candidate: Candidate):
        if not candidate.party:
            candidate.party = self.party_name
            self.candidates.append(candidate)

