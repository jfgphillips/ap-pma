from __future__ import annotations

import enum
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional

from people import PCO, CandidateLevel, Candidate, PoliticalParty
from abc import ABC, abstractmethod

@dataclass
class BaseArea:
    name: str
    def __post_init__(self):
        self.area_registry_instance = AreaRegistry.get_registry(self.name, self.__class__.__name__)
        self.candidate_registry_instance = CandidateRegistry.get_registry(self.name, self.__class__.__name__)

@dataclass
class AreaRegistryInstance:
    def __init__(self):
        self.children = {}

class CandidateRegistryInstance:
    def __init__(self):
        self.candidates = {}


class AreaRegistry:
    _instances = {}

    @staticmethod
    def get_registry(registry_name, area) -> AreaRegistryInstance:
        if area not in AreaRegistry._instances:
            AreaRegistry._instances[area] = {}
        if registry_name not in AreaRegistry._instances[area]:
            AreaRegistry._instances[area][registry_name] = AreaRegistryInstance()

        return AreaRegistry._instances[area][registry_name]

class CandidateRegistry:
    _instances: Dict[str, Dict[str, CandidateRegistryInstance]] = {}

    @staticmethod
    def get_registry(registry_name, area) -> CandidateRegistryInstance:
        if area not in CandidateRegistry._instances:
            CandidateRegistry._instances[area] = {}
        if registry_name not in CandidateRegistry._instances[area]:
            CandidateRegistry._instances[area][registry_name] = CandidateRegistryInstance()

        return CandidateRegistry._instances[area][registry_name]



@dataclass
class CountryArea(BaseArea):

    def add(self, child: AdministrativeArea):
        if not child.country_area:
            child.country_area = self
            self.area_registry_instance.children[child.name] = child
            print(f"AA: {child.name} has been successfully added to Country Area: {self.name}")
        else:
            print(f"AA: {child.name} already has a Country Area: {child.country_area}")

    def add_candidate(self, candidate: Candidate):
        if candidate.level != CandidateLevel.PRESIDENT:
            return
        if candidate.party in self.candidate_registry_instance.candidates:
            return
        self.candidate_registry_instance.candidates[candidate.party] = candidate

@dataclass
class AdministrativeArea(BaseArea):
    country_area = None

    def add(self, child: LocalGovernmentArea):
        if not child.administrative_area:
            child.administrative_area = self
            self.area_registry_instance.children[child.name] = child
            print(f"lga: {child.name} has been successfully added to Administrative Area {self.name}")
        else:
            print(f"lga: {child.name} already has a Administrative Area: {child.administrative_area}")

    def add_candidate(self, candidate: Candidate):
        if candidate.level != CandidateLevel.GOVERNOR:
            return
        if candidate.party in self.candidate_registry_instance.candidates:
            return
        self.candidate_registry_instance.candidates[candidate.party] = candidate

@dataclass
class Constituency(BaseArea):
    country_area = None

    def add(self, child: LocalGovernmentArea):
        if not child.constituency:
            child.constituency = self
            self.area_registry_instance.children[child.name] = child
            print(f"lga: {child.name} has been successfully added to Constituency {self.name}")
        else:
            print(f"lga: {child.name} already has a Constituency: {child.constituency}")

    def add_candidate(self, candidate: Candidate):
        if candidate.level != CandidateLevel.MP:
            return
        if candidate.party in self.candidate_registry_instance.candidates:
            return
        self.candidate_registry_instance.candidates[candidate.party] = candidate

@dataclass
class LocalGovernmentArea(BaseArea):
    constituency = None
    administrative_area = None

    def add(self, child: PollingStation):
        if not child.local_government_area:
            child.local_government_area = self
            self.area_registry_instance.children[child.name] = child
            print(f"PS: {child.name} has been successfully added to LGA {self.name}")
        else:
            print(f"PS: {child.name} already has a LGA: {child.local_government_area}")

    def add_candidate(self, candidate:Candidate):
        if candidate.level != CandidateLevel.MAYOR:
            return
        if candidate.party in self.candidate_registry_instance.candidates:
            return
        self.candidate_registry_instance.candidates[candidate.party] = candidate


@dataclass
class Metadata:
    lga: str
    polling_station: str



@dataclass
class Ballot:
    presidential_candidates: Dict[str, Candidate]
    governorship_candidates: Dict[str, Candidate]
    mayor_candidates: Dict[str, Candidate]
    mp_candidates: Dict[str, Candidate]
    metadata: Metadata



    def get_voting_card(self):
        lines = ["Ballot Paper"]
        lines.append("  Presidential Candidates\n")
        for i, (party, p_candidate) in enumerate(self.presidential_candidates.items()):
            lines.append(f"    {i}: {p_candidate.candidate_party}, {p_candidate.candidate_name}")

        lines.append("  Governorship Candidates\n")
        for i, (party, g_candidate) in enumerate(self.governorship_candidates.items()):
            lines.append(f"    {i}: {g_candidate.candidate_party}, {g_candidate.candidate_name}")

        lines.append("  Mayorship Candidates\n")
        for i, (party, m_candidate) in enumerate(self.mayor_candidates.items()):
            lines.append(f"    {i}: {m_candidate.candidate_party}, {m_candidate.candidate_name}")

        lines.append("  Parliamentary Candidates\n")
        for i, (party, mp_candidate) in enumerate(self.mp_candidates.items()):
            lines.append(f"    {i}: {mp_candidate.candidate_party}, {mp_candidate.candidate_name}")

        lines.append("end")
        return "\n".join(lines)

    @property
    def polling_station(self):
        return PollingStation.from_metadata(self.metadata)

    def cast_votes(self, votes: Dict[CandidateLevel: str]):
        if not self.validate_votes(votes):
            return False
        self.polling_station.vote(votes)
        return True

    @property
    def candidate_mappings(self):
        return  {
            CandidateLevel.PRESIDENT: self.presidential_candidates,
            CandidateLevel.GOVERNOR: self.governorship_candidates,
            CandidateLevel.MAYOR: self.mayor_candidates,
            CandidateLevel.MP: self.mp_candidates
        }

    def validate_votes(self, votes):
        for level, candidate in votes.items():
            if candidate not in self.candidate_mappings[level].keys():
                return False
        return True


    @classmethod
    def from_metadata(cls, metadata):
        ps = PollingStation.from_metadata(metadata)
        ballot: cls = ps.get_ballot()
        return ballot


@dataclass
class PollingStation:
    name: str
    pco: PCO
    local_government_area: Optional[LocalGovernmentArea] = field(default=None)

    @classmethod
    def from_metadata(cls, metadata):
        lgas = AreaRegistry.get_registry(metadata.lga, "LocalGovernmentArea").children
        polling_station: cls = lgas.get(metadata.polling_station)
        return polling_station


    def get_ballot(self):
        presidential_candidates = self.get_presidential_candidates()
        governorship_candidates = self.get_governorship_candidates()
        mayor_candidates = self.get_mayor_candidates()
        mp_candidates = self.get_mp_candidates()
        metadata = self.get_metadata()

        return Ballot(presidential_candidates, governorship_candidates, mayor_candidates, mp_candidates, metadata=metadata)

    def get_mp_candidates(self):
        return self.local_government_area.constituency.candidate_registry_instance.candidates

    def get_mayor_candidates(self):
        return self.local_government_area.candidate_registry_instance.candidates

    def get_governorship_candidates(self):
        return self.local_government_area.administrative_area.candidate_registry_instance.candidates

    def get_presidential_candidates(self):
        return self.local_government_area.administrative_area.country_area.candidate_registry_instance.candidates

    def get_metadata(self):
        metadata = Metadata(
            polling_station=self.name,
            lga=self.local_government_area.name,
        )
        return metadata

    @property
    def candidate_mappings(self):
        return {
            CandidateLevel.PRESIDENT: self.get_presidential_candidates(),
            CandidateLevel.GOVERNOR: self.get_governorship_candidates(),
            CandidateLevel.MAYOR: self.get_mayor_candidates(),
            CandidateLevel.MP: self.get_mp_candidates()
        }

    def vote(self, votes):
        for candidate_level, candidate_party in votes.items():
            candidate = self.candidate_mappings.get(candidate_level)[candidate_party]
            candidate.votes += 1




if __name__ == '__main__':
    p_area = CountryArea("Gwugwuru")
    aas = {}
    for i in range(5):
        a_area = AdministrativeArea(f"AA{i}")
        p_area.add(a_area)
        aas[a_area.name] = a_area

    c_area = Constituency(f"CS1")
    c_area_2 = Constituency(f"CS2")
    a_area = aas["AA1"]
    lgas = {}
    for i in range(5):
        lg_area = LocalGovernmentArea(f"LGA{i}")
        a_area.add(lg_area)
        c_area.add(lg_area)
        lgas[lg_area.name] = lg_area

    a_area_2 = aas["AA2"]
    for i in range(5, 10, 1):
        lg_area = LocalGovernmentArea(f"LGA{i}")
        a_area_2.add(lg_area)
        c_area_2.add(lg_area)
        lgas[lg_area.name] = lg_area


    lg_area = lgas["LGA1"]
    pss = {}
    for i in range(5):
        ps = PollingStation(name=f"PS{i}", pco=PCO())
        lg_area.add(ps)
        pss[ps.name] = ps

    lg_area_2 = lgas["LGA5"]
    for i in range(5, 10, 1):
        ps = PollingStation(name=f"PS{i}", pco=PCO())
        lg_area_2.add(ps)



    candidate = Candidate(level=CandidateLevel.PRESIDENT, name="John Doe")
    candidate_2 = Candidate(level=CandidateLevel.MP, name="James B")
    party = PoliticalParty(party_name="PP1")
    party.register(candidate)
    party.register(candidate_2)

    p_area.add_candidate(candidate)
    c_area.add_candidate(candidate_2)


    print(p_area.area_registry_instance.children)
    PollingStation.from_metadata(ps.get_ballot().metadata)
    ballot = ps.get_ballot()
    votes = {CandidateLevel.PRESIDENT: "PP1"}
    for i in range(10):
        ballot.cast_votes(votes)

    print(p_area.candidate_registry_instance.candidates["PP1"].votes)



