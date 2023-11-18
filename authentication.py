from abc import ABC, abstractmethod
from dataclasses import dataclass


class AuthenticationError(Exception):
    pass


class AuthenticationStrategy(ABC):
    """
    A strategy pattern used for different authentication methods.
    """
    @abstractmethod
    def authenticate(self):
        pass


@dataclass
class VoterIDCard(AuthenticationStrategy):
    id_card_no: int

    def authenticate(self):
        if len(str(self.id_card_no)) != 13:
            print("authentication failed")
            return False
        print("authentication succeeded")
        return True


@dataclass
class NationalInsuranceNumber(AuthenticationStrategy):
    ni_number: str

    def authenticate(self):
        if len(self.ni_number) != 9:
            print("authentication failed")
            return False
        print("authentication succeeded")
        return True


class FactoryMethod:
    @abstractmethod
    def create(self, *args, **kwargs):
        ...
