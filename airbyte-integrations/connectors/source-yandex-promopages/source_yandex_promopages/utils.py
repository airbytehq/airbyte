from typing import Any, Iterable, List, Mapping


def find_report_candidates(
    parent_stream_slices: Iterable[Mapping[str, Any]]
) -> List[Mapping[str, Any]]:
    """
    Get report candidates.

    Each report candidate contains unique publisherId and
    list of campaignIds that belongs to this publisherId
    """
    parent_stream_slices = list(parent_stream_slices)
    # Get unique publisherIds
    publisher_ids = set()
    for stream_slice in parent_stream_slices:
        publisher_ids.add(stream_slice["parent"]["publisherId"])

    # Get campaignIds for each publisherId
    publisher_campaigns = {}
    for publisher_id in publisher_ids:
        publisher_campaigns[publisher_id] = []
        for stream_slice in parent_stream_slices:
            if stream_slice["parent"]["publisherId"] == publisher_id:
                publisher_campaigns[publisher_id].append(stream_slice["parent"]["id"])

    # Create report candidates
    report_candidates = []
    for publisher_id, campaign_ids in publisher_campaigns.items():
        report_candidates.append(
            {
                "publisherId": publisher_id,
                "campaignIds": campaign_ids,
            }
        )

    return report_candidates
