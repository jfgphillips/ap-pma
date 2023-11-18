from areas import init_structure
from authentication import NationalInsuranceNumber
from political_party import CandidateLevel, init_candidates
from results import get_results
from voter import Voter


def cast_votes():
    polling_stations = init_structure()
    init_candidates()
    ballot = polling_stations["PS1"].get_ballot()
    ballot_2 = polling_stations["PS2"].get_ballot()
    ballot_3 = polling_stations["PS5"].get_ballot()

    voter = Voter(
        polling_station_name="PS1",
        voter_name="John Doe",
        authentication_strategy=NationalInsuranceNumber(ni_number="123456789"),
    )
    voter_0_1 = Voter(
        polling_station_name="PS1",
        voter_name="John B",
        authentication_strategy=NationalInsuranceNumber(ni_number="123456789"),
    )
    voter_1 = Voter(
        polling_station_name="PS2",
        voter_name="John P",
        authentication_strategy=NationalInsuranceNumber(ni_number="123456791"),
    )
    voter_2 = Voter(
        polling_station_name="PS5",
        voter_name="John A",
        authentication_strategy=NationalInsuranceNumber(ni_number="153456791"),
    )

    voter.votes = {CandidateLevel.PRESIDENT: "PP1"}
    voter_0_1.votes = {CandidateLevel.PRESIDENT: "PP1"}
    voter_1.votes = {CandidateLevel.PRESIDENT: "PP2"}
    voter_2.votes = {CandidateLevel.MP: "PP1"}

    ballot.cast_votes(voter=voter)

    ballot.cast_votes(voter=voter_0_1)
    ballot_2.cast_votes(voter=voter_1)
    ballot_3.cast_votes(voter=voter_2)


if __name__ == "__main__":
    cast_votes()
    print(get_results(CandidateLevel.PRESIDENT))
    print(get_results(CandidateLevel.MP))
