from areas import LocalGovernmentArea, CountryArea, AdministrativeArea, Constituency
from political_party import CandidateLevel


# a mapping used to pair candidate levels to area level classes
level_area_mapping = {
    CandidateLevel.PRESIDENT: CountryArea,
    CandidateLevel.GOVERNOR: AdministrativeArea,
    CandidateLevel.MAYOR: LocalGovernmentArea,
    CandidateLevel.MP: Constituency,
}
