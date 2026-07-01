#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
"""Synthetic tests for HubSpot CRM Search pagination boundary behavior.

These tests exercise the HubspotCRMSearchPaginationStrategy at the unit level,
verifying behavior at 10k boundaries, short/empty pages, string IDs, and
adjacent time-slice boundaries. The RECORDS_LIMIT is patched down to small
values so no real HubSpot API is required.

Investigation context:
- OC #12852: HubSpot contacts missing/duplicate records
- PR #79666 hypothesis: int() conversion + GTE creates lexicographic gaps
- PR #80745 hypothesis: short-page early-stop ignores paging.next.after
"""

from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def components_module():
    return __import__("components")


@pytest.fixture
def make_strategy(components_module):
    """Factory fixture returning a pagination strategy with configurable page_size."""

    def _make(page_size=200):
        return components_module.HubspotCRMSearchPaginationStrategy(page_size=page_size)

    return _make


def _mock_response(json_body):
    response = Mock()
    response.json.return_value = json_body
    return response


# ---------------------------------------------------------------------------
# Group 1: Short page + paging.next.after present (master early-stop bug)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "last_page_size,paging_body,description",
    [
        pytest.param(
            150,
            {"paging": {"next": {"after": 350}}},
            "HubSpot returns fewer records than page_size but cursor exists",
            id="short_page_with_after_cursor",
        ),
        pytest.param(
            1,
            {"paging": {"next": {"after": 201}}},
            "HubSpot returns single record but cursor exists",
            id="single_record_page_with_after_cursor",
        ),
        pytest.param(
            199,
            {"paging": {"next": {"after": 399}}},
            "Off-by-one: page_size - 1 records but cursor exists",
            id="off_by_one_short_page_with_cursor",
        ),
    ],
)
def test_master_stops_early_on_short_page_with_after(make_strategy, last_page_size, paging_body, description):
    """On master, pagination stops when last_page_size < page_size even if paging.next.after exists.

    This demonstrates the bug that PR #80745 addresses: HubSpot sometimes returns
    fewer records than requested while still providing a valid next cursor.
    Master incorrectly interprets this as end-of-results.
    """
    strategy = make_strategy(page_size=200)
    response = _mock_response(paging_body)

    token = strategy.next_page_token(
        response=response,
        last_page_size=last_page_size,
        last_record={"id": "5000"},
        last_page_token_value={"after": 200},
    )

    # Master returns None here -- this is the bug
    assert token is None, f"Expected master to stop (return None) on short page; got {token}"


# ---------------------------------------------------------------------------
# Group 2: Empty page + paging.next.after present (master early-stop bug)
# ---------------------------------------------------------------------------


def test_master_stops_on_empty_page_with_after(make_strategy):
    """On master, pagination stops when last_page_size == 0 even if paging.next.after exists.

    HubSpot can return an empty results array while still providing a paging cursor.
    This is an edge case where server-side filtering removes all results in a batch
    but more records exist beyond the cursor.
    """
    strategy = make_strategy(page_size=200)
    response = _mock_response({"paging": {"next": {"after": 400}}})

    token = strategy.next_page_token(
        response=response,
        last_page_size=0,
        last_record={"id": "5000"},
        last_page_token_value={"after": 200},
    )

    # Master returns None here -- this is the bug
    assert token is None, f"Expected master to stop (return None) on empty page; got {token}"


# ---------------------------------------------------------------------------
# Group 3: 10k/reset behavior with synthetic IDs (int conversion bug)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "last_record_id,expected_id_in_token,description",
    [
        pytest.param(
            "25000",
            25001,
            "Normal numeric ID at 10k boundary",
            id="numeric_id_10k_boundary",
        ),
        pytest.param(
            "7198",
            7199,
            "Short numeric ID that causes lexicographic gap with long IDs",
            id="short_id_lexicographic_gap",
        ),
        pytest.param(
            "719869649082",
            719869649083,
            "Large 12-digit HubSpot-style ID",
            id="large_hubspot_id_12_digit",
        ),
        pytest.param(
            "99999",
            100000,
            "ID that changes length after int+1 (5 digits -> 6 digits)",
            id="id_length_changes_after_increment",
        ),
    ],
)
def test_10k_boundary_uses_int_conversion(make_strategy, last_record_id, expected_id_in_token, description):
    """At the 10k boundary, master converts last ID to int and adds 1.

    This verifies the current master behavior: int(last_record_id) + 1.
    Combined with the manifest's GTE operator, this creates potential gaps
    when IDs of different string lengths coexist in lexicographic sort order.
    """
    strategy = make_strategy(page_size=200)
    # Simulate reaching the 10k limit: after=9800, last_page_size=200 => 9800+200=10000
    response = _mock_response({"paging": {"next": {"after": 10000}}})

    token = strategy.next_page_token(
        response=response,
        last_page_size=200,
        last_record={"id": last_record_id},
        last_page_token_value={"after": 9800},
    )

    assert token == {"after": 0, "id": expected_id_in_token}


# ---------------------------------------------------------------------------
# Group 4: Reset behavior with string / large HubSpot-style IDs
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "last_record_id,description",
    [
        pytest.param("abc123", "Non-numeric string ID", id="non_numeric_string_id"),
        pytest.param("", "Empty string ID", id="empty_string_id"),
    ],
)
def test_10k_boundary_fails_on_non_numeric_ids(make_strategy, last_record_id, description):
    """Master's int() conversion raises ValueError/TypeError for non-numeric IDs.

    If HubSpot ever returns a non-numeric hs_object_id (unlikely but defensive),
    master would crash at the 10k boundary.
    """
    strategy = make_strategy(page_size=200)
    response = _mock_response({"paging": {"next": {"after": 10000}}})

    with pytest.raises((ValueError, TypeError)):
        strategy.next_page_token(
            response=response,
            last_page_size=200,
            last_record={"id": last_record_id},
            last_page_token_value={"after": 9800},
        )


def test_10k_boundary_zero_padded_id_loses_leading_zeros(make_strategy):
    """Master's int() conversion strips leading zeros, changing sort position.

    "00007198" -> int -> 7199 -> in manifest "GTE 7199"
    But lexicographic "GTE 7199" skips records like "00007199" because
    "0" < "7" in ASCII.
    """
    strategy = make_strategy(page_size=200)
    response = _mock_response({"paging": {"next": {"after": 10000}}})

    # This doesn't crash (leading zeros are valid for int conversion in Python)
    # but it loses the leading zeros
    token = strategy.next_page_token(
        response=response,
        last_page_size=200,
        last_record={"id": "00007198"},
        last_page_token_value={"after": 9800},
    )

    # int("00007198") + 1 = 7199, NOT "00007199"
    assert token == {"after": 0, "id": 7199}
    # The string representation "7199" sorts differently than "00007199" lexicographically
    assert str(token["id"]) != "00007199"


# ---------------------------------------------------------------------------
# Group 5: Lexicographic gap demonstration
# ---------------------------------------------------------------------------


def test_lexicographic_gap_short_vs_long_ids():
    """Demonstrates the core lexicographic gap from PR #79666's hypothesis.

    HubSpot sorts hs_object_id as strings (lexicographic). When the connector
    computes int("7198") + 1 = 7199 and uses GTE "7199", records with IDs
    lexicographically between "7198" and "7199" are skipped.

    Key insight: "7199" > "719869649082" lexicographically at position 3
    because '9' > '8'. So GTE "7199" excludes "719869649082".
    """
    # Simulate HubSpot's lexicographic sort
    ids = ["7195", "7196", "7197", "7198", "719869649082", "719869649083", "7199", "72"]
    sorted_ids = sorted(ids)  # Lexicographic sort

    # After int("7198") + 1 = 7199, GTE "7199" means we skip everything < "7199" lex
    boundary = "7199"
    included = [id_ for id_ in sorted_ids if id_ >= boundary]
    excluded = [id_ for id_ in sorted_ids if id_ < boundary]

    # "719869649082" and "719869649083" are lexicographically < "7199"
    # because at position 3: '8' < '9'. So they get EXCLUDED (skipped).
    assert "719869649082" in excluded, "Long ID should be excluded by GTE '7199'"
    assert "719869649083" in excluded, "Long ID should be excluded by GTE '7199'"

    # Only "7199" and "72" are included (and anything > "7199" lex)
    assert "7199" in included
    assert "72" in included


def test_gt_string_id_would_fix_lexicographic_gap():
    """Demonstrates that PR #79666's approach (GT + raw string) avoids the gap.

    If instead of GTE int(id)+1 we use GT raw_string_id, the boundary becomes
    GT "7198" which correctly includes "719869649082" (since "719869649082" > "7198"
    lexicographically at position 3: '8' == '8', position 4: '6' ... wait.

    Actually let's verify: "7198" vs "719869649082"
    Position 0: '7' == '7'
    Position 1: '1' == '1'
    Position 2: '9' == '9'
    Position 3: '8' vs '8' -- equal
    Position 4: end of "7198" vs '6' in "719869649082"
    In string comparison, shorter string "7198" < "719869649082" because
    when one string ends, it's considered less than the other.
    So "719869649082" > "7198" lexicographically.
    Therefore GT "7198" correctly includes "719869649082".
    """
    ids = ["7195", "7196", "7197", "7198", "719869649082", "719869649083", "7199", "72"]
    sorted_ids = sorted(ids)

    # GT "7198" (PR #79666 approach): include everything strictly greater
    boundary = "7198"
    included_gt = [id_ for id_ in sorted_ids if id_ > boundary]

    # "719869649082" > "7198" lexicographically (longer string when prefix matches)
    assert "719869649082" in included_gt, "GT '7198' should include long ID"
    assert "719869649083" in included_gt, "GT '7198' should include long ID"
    assert "7199" in included_gt, "GT '7198' should include '7199'"
    assert "72" in included_gt, "GT '7198' should include '72'"

    # "7198" itself is excluded (GT, not GTE)
    assert "7198" not in included_gt


# ---------------------------------------------------------------------------
# Group 6: Same-timestamp records at page boundary
# ---------------------------------------------------------------------------


def test_same_timestamp_records_not_deduplicated_at_page_boundary(make_strategy):
    """If many contacts share the same lastmodifieddate, they all appear in the
    same time slice. Within that slice, pagination is by hs_object_id + after cursor.

    This test verifies that normal pagination (within a single 10k chunk) correctly
    advances the after cursor regardless of timestamps.
    """
    strategy = make_strategy(page_size=200)

    # All 200 records have the same timestamp (simulated by using same ID prefix)
    # Normal page: after=200, next page should be after=400
    response = _mock_response({"paging": {"next": {"after": 400}}})

    token = strategy.next_page_token(
        response=response,
        last_page_size=200,
        last_record={"id": "5000"},
        last_page_token_value={"after": 200},
    )

    assert token == {"after": 400}


def test_same_timestamp_across_10k_boundary(make_strategy):
    """When many records share a timestamp and span the 10k boundary,
    the boundary reset uses the last ID. Records with the same timestamp
    but different IDs need the ID filter to not create gaps.
    """
    strategy = make_strategy(page_size=200)
    response = _mock_response({"paging": {"next": {"after": 10000}}})

    # 200 records all with same timestamp, last one has id "5000"
    token = strategy.next_page_token(
        response=response,
        last_page_size=200,
        last_record={"id": "5000"},
        last_page_token_value={"after": 9800},
    )

    # Master computes: GTE int("5000")+1 = GTE 5001
    # This means record "5000" is correctly excluded (not duplicated)
    # But "50000" through "50009" are lexicographically between "5000" and "5001"
    # so they would be SKIPPED
    assert token == {"after": 0, "id": 5001}

    # Demonstrate the gap:
    boundary_str = str(token["id"])  # "5001"
    # Records that would be skipped with GTE "5001":
    skipped_ids = ["50000", "50001", "50002", "50003", "50004", "50005", "50006", "50007", "50008", "50009"]
    for skipped_id in skipped_ids:
        assert skipped_id < boundary_str, f"{skipped_id} should be lex < {boundary_str} but isn't"


# ---------------------------------------------------------------------------
# Group 7: Adjacent 30-day slice boundary behavior (GTE/LTE filters)
# ---------------------------------------------------------------------------


def test_adjacent_slice_inclusive_boundaries_create_overlap():
    """The manifest uses GTE start_time and LTE end_time for date filters.

    With P30D step and PT0.001S granularity, adjacent slices have:
    - Slice 1: GTE start1, LTE end1
    - Slice 2: GTE start2, LTE end2
    where start2 = end1 + 1ms (cursor_granularity)

    Records at exactly end1 timestamp appear in slice 1 only (not slice 2).
    This means NO overlap for correctly-ticking cursors.
    But if cursor_granularity is 1ms and timestamps are rounded to seconds,
    there could be a 999ms gap.
    """
    # Simulate slice boundaries (in milliseconds as HubSpot uses)
    slice1_end = 1645660800000  # 2022-02-24T00:00:00.000Z
    slice2_start = slice1_end + 1  # 1ms later (cursor_granularity = PT0.001S)

    # A record with timestamp exactly at slice1_end is in slice 1 (LTE)
    record_ts = slice1_end
    assert record_ts <= slice1_end  # In slice 1
    assert record_ts < slice2_start  # NOT in slice 2 (GTE slice2_start)

    # A record 1ms after is in slice 2 only
    record_ts_next = slice1_end + 1
    assert record_ts_next > slice1_end  # NOT in slice 1 (wait, LTE includes it... no)
    # Actually LTE slice1_end means <= slice1_end, so record at slice1_end+1 is excluded from slice 1
    assert record_ts_next > slice1_end  # Excluded from slice 1
    assert record_ts_next >= slice2_start  # Included in slice 2


def test_slice_boundary_does_not_lose_records_between_slices():
    """Verify that with 1ms granularity, no timestamp falls between adjacent slices.

    cursor_granularity = PT0.001S = 1ms
    If slice 1 ends at T and slice 2 starts at T+1ms, any integer-ms timestamp
    is in exactly one slice.
    """
    slice1_end_ms = 1645660800000
    slice2_start_ms = slice1_end_ms + 1  # +1ms

    # All possible integer-millisecond timestamps near the boundary
    for offset in range(-5, 6):
        ts = slice1_end_ms + offset
        in_slice1 = ts <= slice1_end_ms
        in_slice2 = ts >= slice2_start_ms
        # Every timestamp should be in at least one slice
        assert in_slice1 or in_slice2, f"Timestamp {ts} falls between slices"
        # No timestamp should be in BOTH slices (no duplicates)
        assert not (in_slice1 and in_slice2), f"Timestamp {ts} is in both slices"


# ---------------------------------------------------------------------------
# Group 8: Simulated full pagination sequence (patched RECORDS_LIMIT)
# ---------------------------------------------------------------------------


@patch("components.HubspotCRMSearchPaginationStrategy.RECORDS_LIMIT", 600)
def test_full_pagination_sequence_with_patched_limit(make_strategy):
    """Simulate a 3-page pagination sequence with RECORDS_LIMIT=600.

    Pages: 200, 200, 200 = 600 records total.
    After page 3: after=400+200=600 >= RECORDS_LIMIT(600), so 10k reset fires.
    """
    strategy = make_strategy(page_size=200)

    # Page 1: after=0, 200 records
    response1 = _mock_response({"paging": {"next": {"after": 200}}})
    token1 = strategy.next_page_token(
        response=response1,
        last_page_size=200,
        last_record={"id": "100"},
        last_page_token_value={"after": 0},
    )
    assert token1 == {"after": 200}, "Page 1 should advance to after=200"

    # Page 2: after=200, 200 records
    response2 = _mock_response({"paging": {"next": {"after": 400}}})
    token2 = strategy.next_page_token(
        response=response2,
        last_page_size=200,
        last_record={"id": "300"},
        last_page_token_value={"after": 200},
    )
    assert token2 == {"after": 400}, "Page 2 should advance to after=400"

    # Page 3: after=400, 200 records -> 400+200=600 >= 600 (RECORDS_LIMIT)
    response3 = _mock_response({"paging": {"next": {"after": 600}}})
    token3 = strategy.next_page_token(
        response=response3,
        last_page_size=200,
        last_record={"id": "500"},
        last_page_token_value={"after": 400},
    )
    # Should trigger 10k reset: int("500") + 1 = 501
    assert token3 == {"after": 0, "id": 501}, "Page 3 should trigger 10k reset"


@patch("components.HubspotCRMSearchPaginationStrategy.RECORDS_LIMIT", 600)
def test_pagination_after_10k_reset_carries_id(make_strategy):
    """After 10k reset, subsequent pages carry the boundary ID in the token."""
    strategy = make_strategy(page_size=200)

    # After reset: token is {"after": 0, "id": 501}
    # Next page returns 200 records
    response = _mock_response({"paging": {"next": {"after": 200}}})
    token = strategy.next_page_token(
        response=response,
        last_page_size=200,
        last_record={"id": "700"},
        last_page_token_value={"after": 0, "id": 501},
    )

    # Should carry the id forward and advance after
    assert token == {"after": 200, "id": 501}


@patch("components.HubspotCRMSearchPaginationStrategy.RECORDS_LIMIT", 600)
def test_short_page_in_second_chunk_stops_pagination(make_strategy):
    """In the second chunk (after 10k reset), a short final page stops pagination.

    This is correct behavior IF HubSpot does not provide paging.next.after.
    """
    strategy = make_strategy(page_size=200)

    # In second chunk, last page has only 50 records and no paging cursor
    response = _mock_response({"results": [{"id": str(i)} for i in range(50)]})
    token = strategy.next_page_token(
        response=response,
        last_page_size=50,
        last_record={"id": "750"},
        last_page_token_value={"after": 200, "id": 501},
    )

    assert token is None, "Short page without paging cursor should stop"


@patch("components.HubspotCRMSearchPaginationStrategy.RECORDS_LIMIT", 600)
def test_short_page_in_second_chunk_with_after_still_stops_on_master(make_strategy):
    """In the second chunk, a short page WITH paging.next.after still stops on master.

    This is the #80745 bug manifesting in subsequent chunks too.
    """
    strategy = make_strategy(page_size=200)

    # Short page (150 records) but paging.next.after exists
    response = _mock_response({"paging": {"next": {"after": 350}}})
    token = strategy.next_page_token(
        response=response,
        last_page_size=150,
        last_record={"id": "750"},
        last_page_token_value={"after": 200, "id": 501},
    )

    # Master still stops early
    assert token is None, "Master stops on short page even with cursor in second chunk"


# ---------------------------------------------------------------------------
# Group 9: Verify #79666 hypothesis - would GT + string fix the gap?
# ---------------------------------------------------------------------------


def test_pr79666_fix_simulation_gt_string_preserves_order():
    """Simulate what #79666 proposes: use GT + raw string ID instead of GTE + int+1.

    Given sorted IDs (HubSpot lexicographic): ["7195", "7196", ..., "7198", "719869649082", ...]
    After processing up to "7198", PR #79666 would emit GT "7198".
    All IDs > "7198" lexicographically are included in the next chunk.
    """
    # HubSpot lexicographic sort order
    all_ids = sorted(["7195", "7196", "7197", "7198", "719869649082", "719869649083", "7199", "72", "8000"])

    # PR #79666 approach: GT last_seen_id (no int conversion)
    last_seen = "7198"
    next_chunk_79666 = [id_ for id_ in all_ids if id_ > last_seen]

    # Master approach: GTE str(int(last_seen) + 1)
    master_boundary = str(int(last_seen) + 1)  # "7199"
    next_chunk_master = [id_ for id_ in all_ids if id_ >= master_boundary]

    # PR #79666 includes the long IDs that master skips
    assert "719869649082" in next_chunk_79666
    assert "719869649083" in next_chunk_79666

    # Master skips them
    assert "719869649082" not in next_chunk_master
    assert "719869649083" not in next_chunk_master

    # PR #79666 does not duplicate "7198"
    assert "7198" not in next_chunk_79666


def test_pr79666_fix_no_duplicate_at_boundary():
    """GT operator ensures the boundary record is not re-fetched (no duplicate)."""
    last_id = "25000"
    candidate_id = "25000"

    # GT "25000" excludes "25000" itself
    assert not (candidate_id > last_id)

    # GTE int("25000")+1 = GTE "25001" also excludes "25000"
    next_boundary = str(int(last_id) + 1)
    assert not (candidate_id >= next_boundary)

    # Both approaches avoid duplicating the boundary record for simple numeric IDs


# ---------------------------------------------------------------------------
# Group 10: Verify #80745 hypothesis - covers short/empty page but not ID gap
# ---------------------------------------------------------------------------


def test_pr80745_fix_would_continue_on_short_page(make_strategy):
    """PR #80745 replaces the page_size check with explicit paging.next.after check.

    Simulated fix behavior: if response has paging.next.after, continue regardless
    of last_page_size.
    """
    strategy = make_strategy(page_size=200)
    response = _mock_response({"paging": {"next": {"after": 350}}})

    # PR #80745 behavior (simulated): when paging.next.after exists, return next token
    # On master this returns None because last_page_size(150) < page_size(200)
    master_token = strategy.next_page_token(
        response=response,
        last_page_size=150,
        last_record={"id": "5000"},
        last_page_token_value={"after": 200},
    )
    assert master_token is None  # Master stops

    # What #80745 would produce: {"after": 350} (using the paging cursor directly)
    # This test documents the expected fix behavior
    paging_after = response.json().get("paging", {}).get("next", {}).get("after")
    assert paging_after == 350  # Cursor exists, should continue


def test_pr80745_does_not_fix_int_conversion_gap(make_strategy):
    """PR #80745's fix (continuing on short pages) does NOT address the
    lexicographic gap caused by int() conversion at the 10k boundary.

    Even with #80745, when the 10k boundary is reached, the ID filter
    still uses int(id)+1 with GTE, creating the same lexicographic gap.
    """
    strategy = make_strategy(page_size=200)
    response = _mock_response({"paging": {"next": {"after": 10000}}})

    # At 10k boundary, behavior is the same regardless of #80745
    token = strategy.next_page_token(
        response=response,
        last_page_size=200,
        last_record={"id": "7198"},
        last_page_token_value={"after": 9800},
    )

    # Both master and #80745 produce the same problematic token
    assert token == {"after": 0, "id": 7199}

    # The lexicographic gap still exists
    boundary = str(token["id"])  # "7199"
    assert "719869649082" < boundary  # Long IDs are LESS than "7199" lexicographically


# ---------------------------------------------------------------------------
# Group 11: Edge cases around the RECORDS_LIMIT threshold
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "after_value,page_size_val,last_page_size_val,should_reset,description",
    [
        pytest.param(9800, 200, 200, True, "Exact threshold: 9800+200=10000", id="exact_threshold"),
        pytest.param(9801, 200, 200, True, "Over threshold: 9801+200=10001", id="over_threshold"),
        pytest.param(9799, 200, 200, False, "Under threshold: 9799+200=9999", id="under_threshold"),
        pytest.param(9800, 200, 199, False, "Short page at threshold boundary", id="short_page_at_threshold"),
        pytest.param(0, 200, 200, False, "First page: 0+200=200 < 10000", id="first_page"),
    ],
)
def test_records_limit_threshold_behavior(make_strategy, after_value, page_size_val, last_page_size_val, should_reset, description):
    """Tests the exact RECORDS_LIMIT threshold condition.

    The reset fires when: last_page_token_value["after"] + last_page_size >= RECORDS_LIMIT
    """
    strategy = make_strategy(page_size=page_size_val)
    response = _mock_response({"paging": {"next": {"after": after_value + last_page_size_val}}})

    token = strategy.next_page_token(
        response=response,
        last_page_size=last_page_size_val,
        last_record={"id": "25000"},
        last_page_token_value={"after": after_value},
    )

    if should_reset:
        assert token == {"after": 0, "id": 25001}, f"Expected 10k reset; got {token}"
    else:
        if last_page_size_val < page_size_val:
            # Short page stops on master
            assert token is None
        else:
            # Normal advancement
            assert token == {"after": after_value + last_page_size_val}


# ---------------------------------------------------------------------------
# Group 12: Short page at exact 10k boundary -- order of condition checks
# ---------------------------------------------------------------------------


def test_short_page_at_exact_10k_boundary_triggers_reset_not_stop(make_strategy):
    """If last_page_size is short AND after+size >= RECORDS_LIMIT, 10k reset wins.

    The 10k check is evaluated FIRST in master's code, so even a short page
    at the boundary triggers reset rather than early-stop.
    """
    strategy = make_strategy(page_size=200)
    response = _mock_response({"paging": {"next": {"after": 10000}}})

    # Short page (150) but we're at the boundary: 9850+150=10000 >= 10000
    token = strategy.next_page_token(
        response=response,
        last_page_size=150,
        last_record={"id": "9999"},
        last_page_token_value={"after": 9850},
    )

    # 10k check fires first: 9850+150=10000 >= 10000
    assert token == {"after": 0, "id": 10000}


# ---------------------------------------------------------------------------
# Group 13: HubSpot string cursor (after as string) behavior
# ---------------------------------------------------------------------------


def test_string_after_cursor_in_page_token_value(make_strategy):
    """HubSpot sometimes returns 'after' as a string in paging.next.after.

    Master's code accesses last_page_token_value.get("after", 0) and adds
    last_page_size to it. If 'after' is stored as string from a previous
    iteration, this could cause a TypeError.

    Note: In practice, the pagination strategy always stores 'after' as int
    internally (since it initializes with {"after": 0} and adds page_size).
    But if a string leaks in, it would break.
    """
    strategy = make_strategy(page_size=200)
    response = _mock_response({"paging": {"next": {"after": "400"}}})

    # This works because last_page_token_value["after"] is always int in practice
    token = strategy.next_page_token(
        response=response,
        last_page_size=200,
        last_record={"id": "5000"},
        last_page_token_value={"after": 200},  # int, as stored internally
    )
    assert token == {"after": 400}


# ---------------------------------------------------------------------------
# Group 14: Combined scenario - demonstrates both bugs interacting
# ---------------------------------------------------------------------------


@patch("components.HubspotCRMSearchPaginationStrategy.RECORDS_LIMIT", 600)
def test_combined_short_page_before_limit_then_10k_reset(make_strategy):
    """Scenario where short page bug and 10k bug interact.

    If a short page occurs just before the RECORDS_LIMIT threshold,
    master stops early and never reaches the 10k boundary at all.
    This means records beyond the short page are lost without even
    hitting the lexicographic gap issue.
    """
    strategy = make_strategy(page_size=200)

    # Page 1: 200 records, normal
    r1 = _mock_response({"paging": {"next": {"after": 200}}})
    t1 = strategy.next_page_token(r1, 200, {"id": "100"}, {"after": 0})
    assert t1 == {"after": 200}

    # Page 2: only 150 records BUT has paging.next.after (short page bug)
    r2 = _mock_response({"paging": {"next": {"after": 350}}})
    t2 = strategy.next_page_token(r2, 150, {"id": "250"}, {"after": 200})
    # Master stops here even though there are more records
    assert t2 is None  # Lost records that would have been in remaining pages


# ---------------------------------------------------------------------------
# Group 15: Verify the interaction between hs_object_id filter and sort
# ---------------------------------------------------------------------------


def test_manifest_gte_filter_with_int_id_creates_string_comparison():
    """The manifest interpolates the ID value into a JSON request body.

    `"value": "{{ next_page_token['next_page_token'].get('id', 0) }}"`

    When id=7199 (int), Jinja renders it as "7199" (string in JSON).
    HubSpot's search API then applies GTE "7199" as a string comparison
    on the hs_object_id field, which creates the lexicographic gap.
    """
    # Simulate Jinja template rendering
    token = {"after": 0, "id": 7199}  # What master produces
    rendered_value = str(token.get("id", 0))  # How Jinja would render it

    assert rendered_value == "7199"

    # HubSpot applies this as: hs_object_id GTE "7199" (string comparison)
    # Records like "719869649082" fail this check because "719869649082" < "7199"
    assert "719869649082" < rendered_value


def test_manifest_id_zero_default_includes_all_records():
    """When no ID boundary is set (first chunk), the manifest uses get('id', 0).

    This renders as "0" which in lexicographic order is less than any
    digit-starting ID, so all records are included.
    """
    token = {"after": 0}  # No "id" key -- first chunk
    rendered_value = str(token.get("id", 0))

    assert rendered_value == "0"

    # "0" is lexicographically less than any HubSpot ID starting with 1-9
    sample_ids = ["1", "100", "7198", "719869649082", "99999"]
    for id_ in sample_ids:
        assert id_ >= rendered_value, f"ID {id_} should be >= '0'"
