from areas import init_structure
from authentication import NationalInsuranceNumber, AuthenticationError
from political_party import CandidateLevel, init_candidates
from voter import Voter


def test_votes():
    polling_stations = init_structure()
    init_candidates()
    ballot = polling_stations["PS1"].get_ballot()


    voter = Voter(polling_station_name="PS1", voter_name="John Doe", authentication_strategy=NationalInsuranceNumber(ni_number="123456789"))
    voter_1 = Voter(polling_station_name="PS2", voter_name="John P", authentication_strategy=NationalInsuranceNumber(ni_number="123456791"))
    invalid_voter = Voter(polling_station_name="PS1", voter_name="John B", authentication_strategy=NationalInsuranceNumber(ni_number="1234567910000"))

    voter.votes = {CandidateLevel.PRESIDENT: "PP1"}
    voter_1.votes = {CandidateLevel.PRESIDENT: "PP2"}

    # Valid Vote
    ballot.cast_votes(voter=voter)

    # double vote
    try:
        ballot.cast_votes(voter=voter)
    except ValueError as e:
        print(f"successfully prevented a double vote: {e}")
    try:
        ballot.cast_votes(voter=voter_1)
    except ValueError as e:
        print(f"successfully captured voter at wrong polling station: {e}")

    try:
        ballot.cast_votes(voter=invalid_voter)
    except AuthenticationError as e:
        print(f"successfully prevented unauthenticated voter from voting: {e}")

if __name__ == '__main__':
    test_votes()