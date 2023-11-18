from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Optional
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
    _entries: Dict[str, AbstractArea] = field(default_factory=dict)

    @property
    def entries(self):
        return self._entries

    def add_entry(self, area: AbstractArea):
        self.entries[area.name] = area


@dataclass
class CandidateRegistryInstance(BaseRegistryInstance):
    _entries: Dict[str, Candidate] = field(default_factory=dict)

    @property
    def entries(self) -> dict:
        return self._entries

    def add_entry(self, candidate: Candidate):
        if candidate.area in self.entries.keys():
            raise ValueError(
                f"cannot add candidate as there is already a candidate registered {self.entries.get(candidate.area)}"
            )
        if not AreaRegistry.is_registry(level_area_mapping.get(candidate.level).__name__, candidate.area):
            raise KeyError(f"No area instance exists for area {candidate.area}, create this please")
        self.entries[candidate.area] = candidate


class AreaRegistry:
    _instances: Dict[str, Dict[str, AreaRegistryInstance]] = {}

    @staticmethod
    def get_or_create_registry_instance(registry_name, area) -> AreaRegistryInstance:
        if area not in AreaRegistry._instances:
            AreaRegistry._instances[area] = {}
        if registry_name not in AreaRegistry._instances[area]:
            AreaRegistry._instances[area][registry_name] = AreaRegistryInstance()

        return AreaRegistry._instances[area][registry_name]

    @staticmethod
    def is_registry(area, registry_name):
        return bool(AreaRegistry._instances.get(area, {}).get(registry_name))

    @staticmethod
    def get_registries_for_area(area) -> Optional[list]:
        return list(AreaRegistry._instances.get(area).keys())

class CandidateRegistry:
    _instances: Dict[str, CandidateRegistryInstance] = {}

    @staticmethod
    def get_registry(party) -> CandidateRegistryInstance:
        if party not in CandidateRegistry._instances:
            CandidateRegistry._instances[party] = CandidateRegistryInstance()
        return CandidateRegistry._instances[party]

    @staticmethod
    def get_for_area(instance_name) -> Dict[str, Candidate]:
        candidates = {}
        for party, area_map in CandidateRegistry._instances.items():
            candidate = area_map.entries.get(instance_name)
            if not candidate:
                continue
            candidates[party] = candidate
        return candidates

