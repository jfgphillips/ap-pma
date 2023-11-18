from registries import AreaRegistry
from utils import level_area_mapping


def get_results(level):
    area = level_area_mapping.get(level)
    area_instance_names = AreaRegistry.get_registries_for_area(area.__name__)
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
