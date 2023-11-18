from areas import LocalGovernmentArea, CountryArea, AdministrativeArea, Constituency
from political_party import CandidateLevel

level_area_mapping = {
    CandidateLevel.PRESIDENT: CountryArea,
    CandidateLevel.GOVERNOR: AdministrativeArea,
    CandidateLevel.MAYOR: LocalGovernmentArea,
    CandidateLevel.MP: Constituency,
}
