from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Optional, List, Any
from areas import AbstractArea
from political_party import Candidate
from utils import level_area_mapping


class BaseRegistryInstance:
    _entries: dict

    @abstractmethod
    def add_entry(self, entry):
        ...


@dataclass
class AreaRegistryInstance(BaseRegistryInstance):
    """
    A class used to persist a nodes related areas within the electoral structure

    _entries: Key = the name of the area relation (leverages dict implementation to avoid relation duplication)
              Value = the area instance

    e.g.
    p_area = CountryArea("Gwugwuru")
    a_area = AdminisrativeArea("AA1")
    a_area_2 = AdministrativeArea("AA2")
    p_area.add_child(a_area)
    p_area.add_child(a_area_2)
    p_area.area_registry_instance
    {"AA1": AdministrativeArea(name="AA1"), "AA2": AdministrativeArea(name="AA2")}
    graph looks like:
              Gwugwuru
              /     \
            /        \
          AA1        AA2
    ...
    """

    _entries: Dict[str, AbstractArea] = field(default_factory=dict)

    @property
    def entries(self):
        return self._entries

    def add_entry(self, area: AbstractArea):
        """
        A method used to persist the graph interface of the area structure
        """
        self.entries[area.name] = area


@dataclass
class CandidateRegistryInstance(BaseRegistryInstance):
    """
    A class used to maintain a record of candidates assigned to particular areas.

    _entries: Key = area name (leverages dict implementation to ensure max one candidate per area)
              Value = Candidate object (leverages CandidateRegistry singleton to persist votes across polling stations)

    e.g.
    party = PoliticalParty("PP1")
    party_2 = PoliticalParty("PP2")
    candidate = Candidate(level=CandidateLevel.PRESIDENT, name="John Doe", area="Gwugwuru")
    candidate_2 = Candidate(level=CandidateLevel.PRESIDENT, name="Tim D", area="Gwugwuru")
    party.register(candidate)
    party_2.register(candidate_2)
    party.candidate_registry_instance
    {'Gwugwuru': Candidate(level=<CandidateLevel.PRESIDENT: 1>, area='Gwugwuru', name='John Doe', party='PP1', votes=0)}
    """

    _entries: Dict[str, Candidate] = field(default_factory=dict)

    @property
    def entries(self) -> dict:
        """a public property used to access the entries in this registry"""
        return self._entries

    def add_entry(self, candidate: Candidate):
        """
        A method used to add candidates to a political party registry
        Parameters:
            candidate (Candidate): the candidate to add to the candidate entries

        raises
            ValueError: if there is already a candidate registered for this political party in the same area
            KeyError: if no area exists for the candidate trying to register
        """
        if candidate.area in self.entries.keys():
            raise ValueError(
                f"cannot add candidate as there is already a candidate registered {self.entries.get(candidate.area)}"
            )
        if not AreaRegistry.is_registry(level_area_mapping.get(candidate.level).__name__, candidate.area):
            raise KeyError(f"No area instance exists for area {candidate.area}, create this please")
        self.entries[candidate.area] = candidate


class BaseRegistry:
    @staticmethod
    @abstractmethod
    def get_or_create_registry_instance(*args, **kwargs) -> BaseRegistryInstance:
        ...

    @staticmethod
    @abstractmethod
    def get_for_area(area_instance_name) -> Any:
        ...


class AreaRegistry(BaseRegistry):
    """
    A singleton factory method that persists AreaRegistryInstances (used to keep track of graph dependencies)

    _instances:
        dict where key is AreaClass.__name__ e.g.:
                'CountryArea', 'AdministrativeArea', 'Constituency', 'LocalGovernmentArea'
             and values:
                dict where key = AreaClass(name="AA1").name e.g.:
                    'AA0', 'AA1', 'AA2', 'AA3', 'AA4'

    """

    _instances: Dict[str, Dict[str, AreaRegistryInstance]] = {}

    @staticmethod
    def get_or_create_registry_instance(registry_name, area) -> AreaRegistryInstance:
        if area not in AreaRegistry._instances:
            AreaRegistry._instances[area] = {}
        if registry_name not in AreaRegistry._instances[area]:
            AreaRegistry._instances[area][registry_name] = AreaRegistryInstance()

        return AreaRegistry._instances[area][registry_name]

    @staticmethod
    def get_for_area(area_class_name) -> Optional[List[str]]:
        """
        a method used for getting the instance names for a given AreaClass.__name__
        Parameters
            area_instance_name: e.g. 'CountryArea'
        Returns
            A list of area instance names e.g. ["Gwugwuru"]
        """
        return list(AreaRegistry._instances.get(area_class_name).keys())

    @staticmethod
    def is_registry(area, registry_name):
        return bool(AreaRegistry._instances.get(area, {}).get(registry_name))


class CandidateRegistry(BaseRegistry):
    """
    A singleton factory method that persists CandidateRegistryInstances
    """

    _instances: Dict[str, CandidateRegistryInstance] = {}

    @staticmethod
    def get_or_create_registry_instance(party) -> CandidateRegistryInstance:
        if party not in CandidateRegistry._instances:
            CandidateRegistry._instances[party] = CandidateRegistryInstance()
        return CandidateRegistry._instances[party]

    @staticmethod
    def get_for_area(area_instance_name) -> Dict[str, Candidate]:
        """
        A static method used to retrieve the candidates assigned to an area instance

        Process:
        1. iterates through each political party
        2. searches each political party for the area instance in question
        3. appends matching candidates to the return dictionary

        Parameters:
            area_instance_name: e.g. AA1
        """
        candidates = {}
        for party, area_map in CandidateRegistry._instances.items():
            candidate = area_map.entries.get(area_instance_name)
            if not candidate:
                continue
            candidates[party] = candidate
        return candidates
