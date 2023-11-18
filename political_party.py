import enum
from dataclasses import dataclass



@enum.unique
class CandidateLevel(enum.Enum):
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

@dataclass
class PoliticalParty:
    party_name: str

    def __post_init__(self):
        from registries import CandidateRegistry

        self.candidate_registry_instance = CandidateRegistry.get_registry(party=self.party_name)

    def register(self, candidate: Candidate):
        if not candidate.party:
            candidate.party = self.party_name
            self.candidate_registry_instance.add_entry(candidate)


def init_candidates():
    candidate = Candidate(level=CandidateLevel.PRESIDENT, name="John Doe", area="Gwugwuru")
    candidate_1 = Candidate(level=CandidateLevel.MP, name="James B", area="CS2")
    candidate_2 = Candidate(level=CandidateLevel.PRESIDENT, name="Tim D", area="Gwugwuru")
    party = PoliticalParty(party_name="PP1")
    party_2 = PoliticalParty(party_name="PP2")
    party.register(candidate)
    party.register(candidate_1)
    party_2.register(candidate_2)


