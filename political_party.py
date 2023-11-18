import enum
from dataclasses import dataclass, field


@enum.unique
class CandidateLevel(enum.Enum):
    """The eligible candidate levels for GEC elections"""

    PRESIDENT = enum.auto()
    GOVERNOR = enum.auto()
    MAYOR = enum.auto()
    MP = enum.auto()


@dataclass
class Candidate:
    """
    A class representing the necessary attributes for a candidate
    Parameters:
        level (CandidateLevel): The election level the candidate is registered for
        area (str): The area instance name the candidate wants to register to
        name (str): the name of the candidate
        party (str): the political party the candidate is registered for (set by an instance of PoliticalParty)
        votes (int): the number of votes the candidate has received (incremented by the PollingStation.vote method)
    """

    level: CandidateLevel
    area: str
    name: str
    party: str = field(init=False, default=None)
    votes: int = field(init=False, default=0)


@dataclass
class PoliticalParty:
    """
    A class used to create and administer political party operations

    Parameters:
        party_name (str): The name of the political party.

    Attributes:
        party_name (str): The name of the political party.
        candidate_registry_instance (CandidateRegistry): An instance of CandidateRegistry
            used to persist party information.

    Methods:
        __post_init__():
            Initializes the CandidateRegistry instance for the political party after object creation.

        register(candidate: Candidate):
            Registers a candidate with the political party and adds them to the CandidateRegistry.

    Example:
        >>> party = PoliticalParty("PP1")
        >>> candidate = Candidate(level=CandidateLevel.PRESIDENT, name="John Doe", area="Gwugwuru")
        >>> party.register(candidate)
        >>> print(candidate.party)
        'PP1'
    """

    party_name: str

    def __post_init__(self):
        from registries import CandidateRegistry

        self.candidate_registry_instance = CandidateRegistry.get_or_create_registry_instance(party=self.party_name)

    def register(self, candidate: Candidate):
        """
        Registers a candidate with the political party and adds them to the CandidateRegistry.

        Parameters:
            candidate (Candidate): The candidate to be registered.

        Returns:
            None
        """
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
    print(True)


if __name__ == "__main__":
    init_candidates()
