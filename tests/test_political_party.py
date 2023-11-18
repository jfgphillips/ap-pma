from areas import init_structure
from political_party import Candidate, CandidateLevel, PoliticalParty


def test_candidates():
    init_structure()
    valid_candidate = Candidate(level=CandidateLevel.PRESIDENT, name="John Doe", area="Gwugwuru")
    same_level_candidate = Candidate(level=CandidateLevel.PRESIDENT, name="John P", area="Gwugwuru")
    non_existent_area = Candidate(level=CandidateLevel.MP, name="James B", area="DOESNT_EXIST")
    party = PoliticalParty(party_name="PP1")
    party.register(valid_candidate)
    try:
        party.register(same_level_candidate)
    except ValueError:
        print("validated we cannot add multiple candidates for one position")

    try:
        party.register(non_existent_area)
    except KeyError:
        print("validated we cannot register a candidate without a valid area")


if __name__ == "__main__":
    test_candidates()
