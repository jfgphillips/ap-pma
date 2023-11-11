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
    area: str
    name: str
    party = None
    votes = 0
