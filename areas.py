from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Optional

from people import CandidateLevel, Candidate, PCO


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


@dataclass
class AbstractArea(ABC):
    name: str

    @property
    @abstractmethod
    def candidates(self):
        ...


class HierarchicalAreaNode(AbstractArea):
    def __post_init__(self):
        from registries import AreaRegistry

        self.area_registry_instance = AreaRegistry.get_registry(self.name, self.__class__.__name__)

    @property
    def candidates(self):
        from registries import CandidateRegistry

        return CandidateRegistry.get_for_instance(self.name)

    @abstractmethod
    def add_child(self, child: AbstractArea):
        ...


class TerminalAreaNode(AbstractArea):
    parent: LocalGovernmentArea

    def get_mp_candidates(self):
        return self.parent.constituency.candidates

    def get_mayor_candidates(self):
        return self.parent.candidates

    def get_governorship_candidates(self):
        return self.parent.administrative_area.candidates

    def get_presidential_candidates(self):
        return self.parent.administrative_area.country_area.candidates

    @property
    def candidates(self) -> Candidates:
        return Candidates(
            presidential_candidates=self.get_presidential_candidates(),
            governorship_candidates=self.get_governorship_candidates(),
            mayor_candidates=self.get_mayor_candidates(),
            mp_candidates=self.get_mp_candidates(),
        )


@dataclass
class CountryArea(HierarchicalAreaNode):
    def add_child(self, child: AdministrativeArea):
        if not child.country_area:
            child.country_area = self
            self.area_registry_instance.add_entry(child)
            print(f"AA: {child.name} has been successfully added to Country Area: {self.name}")
        else:
            print(f"AA: {child.name} already has a Country Area: {child.country_area}")


@dataclass
class AdministrativeArea(HierarchicalAreaNode):
    _country_area: Optional[CountryArea] = None

    @property
    def country_area(self):
        return self._country_area

    @country_area.setter
    def country_area(self, country_area: CountryArea):
        self._country_area = country_area

    def add_child(self, child: LocalGovernmentArea):
        if not child.administrative_area:
            child.administrative_area = self
            self.area_registry_instance.add_entry(child)
            print(f"lga: {child.name} has been successfully added to Administrative Area {self.name}")
        else:
            print(f"lga: {child.name} already has a Administrative Area: {child.administrative_area}")


@dataclass
class Constituency(HierarchicalAreaNode):
    def add_child(self, child: LocalGovernmentArea):
        if not child.constituency:
            child.constituency = self
            self.area_registry_instance.add_entry(child)
            print(f"lga: {child.name} has been successfully added to Constituency {self.name}")
        else:
            print(f"lga: {child.name} already has a Constituency: {child.constituency}")


@dataclass
class LocalGovernmentArea(HierarchicalAreaNode):
    _constituency: Optional[Constituency] = None
    _administrative_area: Optional[AdministrativeArea] = None

    @property
    def constituency(self):
        return self._constituency

    @constituency.setter
    def constituency(self, constituency: Constituency):
        self._constituency = constituency

    @property
    def administrative_area(self):
        return self._administrative_area

    @administrative_area.setter
    def administrative_area(self, administrative_area: AdministrativeArea):
        self._administrative_area = administrative_area

    def add_child(self, child: PollingStation):
        if not child.parent:
            child.parent = self
            self.area_registry_instance.add_entry(child)
            print(f"PS: {child.name} has been successfully added to LGA {self.name}")
        else:
            print(f"PS: {child.name} already has a LGA: {child.parent}")


@dataclass
class Metadata:
    lga: str
    polling_station: str


@dataclass
class Candidates:
    presidential_candidates: Dict[str, Candidate]
    governorship_candidates: Dict[str, Candidate]
    mayor_candidates: Dict[str, Candidate]
    mp_candidates: Dict[str, Candidate]

    @property
    def candidate_level_map(self):
        return {
            CandidateLevel.PRESIDENT: self.presidential_candidates,
            CandidateLevel.GOVERNOR: self.governorship_candidates,
            CandidateLevel.MAYOR: self.mayor_candidates,
            CandidateLevel.MP: self.mp_candidates,
        }


@dataclass
class Ballot:
    candidates: Candidates
    metadata: Metadata

    def get_voting_card(self):
        lines = ["Ballot Paper"]
        lines.append("  Presidential Candidates")
        for i, (party, p_candidate) in enumerate(self.candidates.presidential_candidates.items()):
            lines.append(f"    {i}: {p_candidate.party}, {p_candidate.name}")

        lines.append("\n  Governorship Candidates")
        for i, (party, g_candidate) in enumerate(self.candidates.governorship_candidates.items()):
            lines.append(f"    {i}: {g_candidate.party}, {g_candidate.name}")

        lines.append("\n  Mayorship Candidates")
        for i, (party, m_candidate) in enumerate(self.candidates.mayor_candidates.items()):
            lines.append(f"    {i}: {m_candidate.party}, {m_candidate.name}")

        lines.append("\n  Parliamentary Candidates")
        for i, (party, mp_candidate) in enumerate(self.candidates.mp_candidates.items()):
            lines.append(f"    {i}: {mp_candidate.party}, {mp_candidate.name}")

        lines.append("end")
        return "\n".join(lines)

    @property
    def polling_station(self):
        return PollingStation.from_metadata(self.metadata)

    def cast_votes(self, votes: Dict[CandidateLevel:str]):
        if not self.validate_votes(votes):
            return False
        self.polling_station.vote(votes)
        return True

    def validate_votes(self, votes):
        for level, candidate in votes.items():
            if candidate not in self.candidates.candidate_level_map[level].keys():
                return False
        return True

    @classmethod
    def from_metadata(cls, metadata):
        ps = PollingStation.from_metadata(metadata)
        ballot: cls = ps.get_ballot()
        return ballot


@dataclass
class PollingStation(TerminalAreaNode):
    pco: PCO
    parent: Optional[LocalGovernmentArea] = field(default=None)

    @classmethod
    def from_metadata(cls, metadata):
        from registries import AreaRegistry

        lgas = AreaRegistry.get_registry(metadata.lga, "LocalGovernmentArea").entries
        polling_station: cls = lgas.get(metadata.polling_station)
        return polling_station

    def get_metadata(self):
        metadata = Metadata(
            polling_station=self.name,
            lga=self.parent.name,
        )
        return metadata

    def get_ballot(self):
        metadata = self.get_metadata()

        return Ballot(candidates=self.candidates, metadata=metadata)

    def vote(self, votes):
        for candidate_level, candidate_party in votes.items():
            candidate = self.candidates.candidate_level_map.get(candidate_level)[candidate_party]
            candidate.votes += 1


area_level_map = {
    CandidateLevel.PRESIDENT: CountryArea.__name__,
    CandidateLevel.GOVERNOR: AdministrativeArea.__name__,
    CandidateLevel.MAYOR: LocalGovernmentArea.__name__,
    CandidateLevel.MP: Constituency.__name__,
}


if __name__ == "__main__":
    p_area = CountryArea("Gwugwuru")
    aas = {}
    for i in range(5):
        a_area = AdministrativeArea(f"AA{i}")
        p_area.add_child(a_area)
        aas[a_area.name] = a_area

    c_area = Constituency(f"CS1")
    c_area_2 = Constituency(f"CS2")
    a_area = aas["AA1"]
    lgas = {}
    for i in range(5):
        lg_area = LocalGovernmentArea(f"LGA{i}")
        a_area.add_child(lg_area)
        c_area.add_child(lg_area)
        lgas[lg_area.name] = lg_area

    a_area_2 = aas["AA2"]
    for i in range(5, 10, 1):
        lg_area = LocalGovernmentArea(f"LGA{i}")
        a_area_2.add_child(lg_area)
        c_area_2.add_child(lg_area)
        lgas[lg_area.name] = lg_area

    lg_area = lgas["LGA1"]
    pss = {}
    for i in range(5):
        ps = PollingStation(name=f"PS{i}", pco=PCO())
        lg_area.add_child(ps)
        pss[ps.name] = ps

    lg_area_2 = lgas["LGA5"]
    for i in range(5, 10, 1):
        ps = PollingStation(name=f"PS{i}", pco=PCO())
        lg_area_2.add_child(ps)

    candidate = Candidate(level=CandidateLevel.PRESIDENT, name="John Doe", area="Gwugwuru")
    candidate_2 = Candidate(level=CandidateLevel.MP, name="James B", area="CS1")
    candidate_3 = Candidate(level=CandidateLevel.MP, name="James B", area="DOESNT_EXIST")
    party = PoliticalParty(party_name="PP1")
    party.register(candidate)
    party.register(candidate_2)
    party.register(candidate_3)

    print(p_area.area_registry_instance.entries)
    PollingStation.from_metadata(ps.get_ballot().metadata)
    ballot = ps.get_ballot()
    votes = {CandidateLevel.PRESIDENT: "PP1"}
    for i in range(10):
        ballot.cast_votes(votes)

    print(p_area.candidates["PP1"].votes)
