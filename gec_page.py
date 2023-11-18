from abc import ABC, abstractmethod
from fnmatch import fnmatch
from functools import singledispatchmethod

from areas import Metadata, Ballot, init_structure
from authentication import NationalInsuranceNumber
from political_party import CandidateLevel, init_candidates
from results import get_results
from voter import Voter


class Command(ABC):
    @abstractmethod
    def execute(self, data):
        ...

    @property
    def str_level_map(self):
        return {
            "president": CandidateLevel.PRESIDENT,
            "mp": CandidateLevel.MP,
            "mayor": CandidateLevel.MAYOR,
            "governor": CandidateLevel.GOVERNOR
        }

    def cast_vote(self, metadata, voter):
        ballot = Ballot.from_metadata(metadata)
        ballot.cast_votes(voter)
class JsonDataCommand(Command):
    def execute(self, data):
        print("Executing command for JSON data")
        metadata = Metadata(lga=data["LGA"], polling_station=data["PC"])
        voter = Voter(polling_station_name=data["PC"], voter_name=data["voter_name"], authentication_strategy=NationalInsuranceNumber(data["ID"]))
        voter.votes = {self.str_level_map.get(k): v for k, v in data["votes"].items()}
        self.cast_vote(metadata, voter)

class PdfDataCommand(Command):
    def execute(self, data):
        split_string = data.split(",")
        parsed_data = {}
        for pair in split_string:
            k, v = pair.split("=")
            parsed_data[k.strip()] = v
        votes = {}
        for key, value in parsed_data.items():
            if fnmatch(key, "*vote"):
                level = key.split("_")[0].strip()
                votes[self.str_level_map.get(level)] = value

        metadata = Metadata(lga=parsed_data["lga"], polling_station=parsed_data["pc"])
        voter = Voter(polling_station_name=parsed_data["pc"], voter_name=parsed_data["voter_name"], authentication_strategy=NationalInsuranceNumber(parsed_data["voter_id"]))
        voter.votes = votes
        self.cast_vote(metadata, voter)


class Server:

    @singledispatchmethod
    def process(self, data):
        raise NotImplementedError("please create a method to handle your dtype")

    @process.register
    def _(self, data: dict):
        JsonDataCommand().execute(data)

    @process.register
    def _(self, data: str):
        PdfDataCommand().execute(data)



class ClientAPI:
    def json_request(self, voter_name: str, voter_id: str, pc: str, lga: str, votes: dict) -> dict:
        return {
            "voter_name": voter_name,
            "ID": voter_id,
            "PC": pc,
            "LGA": lga,
            "votes": votes
        }

    def str_request(self, str_data: str) -> str:
        return str_data

    def send_request(self, server: Server, packet):
        server.process(packet)

if __name__ == '__main__':
    init_structure()
    init_candidates()
    server = Server()
    client_api = ClientAPI()
    json_vote = client_api.json_request(voter_name="Jon Doe", voter_id="123456789", pc="PS1", lga="LGA1", votes={"president": "PP1"})
    str_vote = client_api.str_request("voter_name=John P, voter_id=123456789, pc=PS1, lga=LGA1, president_vote=PP1")
    print(json_vote)
    client_api.send_request(server, str_vote)
    print(get_results(CandidateLevel.PRESIDENT))