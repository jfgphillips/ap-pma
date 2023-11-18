from political_party import CandidateLevel
from registries import AreaRegistry
from utils import level_area_mapping


def get_results(level: CandidateLevel):
    """
    Get election results for a specific CandidateLevel.

    Parameters:
        level (str): The CandidateLevel level for which election results are requested.

    Returns:
        dict: A dictionary containing election results for each eligible areia within the specified CandidateLevel.
              The keys are area instance names, and the values represent the result status:
              Options Include:
                NO_RESULT: No votes have been registered
                HUNG_RESULT: two parties have equal votes for specified area
                PPn: The name of the political party that won that election

    Example:
        >>> get_results(CandidateLevel.GOVERNOR)
        {'AA1': 'PP1', 'AA2': 'PP1', 'AA3': 'HUNG_RESULT'}

    :param level:
    :return:
    """
    area = level_area_mapping.get(level)
    area_instance_names = AreaRegistry.get_for_area(area.__name__)
    area_results = {}
    for area_name in area_instance_names:
        candidates = area(name=area_name).candidates
        results = {}
        for candidate_party, candidate in candidates.items():
            votes = candidate.votes
            results[candidate_party] = votes
        if not results:
            area_results[area_name] = "NO_RESULT"
            continue
        max_votes = max(results.values())
        parties_with_max_votes = [key for key, value in results.items() if value == max_votes]
        if len(parties_with_max_votes) == 1:
            area_results[area_name] = parties_with_max_votes[0]
        else:
            print(f"hung vote between following parties: {parties_with_max_votes}")
            area_results[area_name] = "HUNG_RESULT"

    return area_results
