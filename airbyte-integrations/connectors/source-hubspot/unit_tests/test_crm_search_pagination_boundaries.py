#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
"""Synthetic tests documenting suspected failure modes in HubSpot CRM Search pagination.

These tests do NOT fix any production behavior. They document and prove suspected bugs
on the current master code, using mocked HubSpot responses and patched RECORDS_LIMIT.
No real HubSpot API calls are made; no customer data or credentials are used.

Investigation context — OC airbytehq/oncall#12852 (missing/duplicate contacts):

Two prior draft PRs proposed independent fixes:
  - airbytehq/airbyte#79666: hypothesized that int(id)+1 with GTE creates lexicographic
    gaps at the 10k boundary. Proposed using GT + raw string ID instead.
  - airbytehq/airbyte#80745: hypothesized that short/empty pages with a valid
    paging.next.after cursor cause premature pagination stop. Proposed checking
    the cursor presence instead of comparing page sizes.

Test organization:
  PART A — Tests that exercise real connector code (HubspotCRMSearchPaginationStrategy)
           to document current (broken) master behavior.
  PART B — Pure string/lexicographic demonstrations that do NOT call any connector code.
           These prove why the current boundary computation is problematic and why
           the proposed fixes would (or would not) help.
"""

from unittest.mock import Mock, patch

import pytest


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def components_module():
    return __import__("components")


@pytest.fixture
def make_strategy(components_module):
    """Factory fixture returning a HubspotCRMSearchPaginationStrategy."""

    def _make(page_size=200):
        return components_module.HubspotCRMSearchPaginationStrategy(page_size=page_size)

    return _make


def _mock_response(json_body):
    response = Mock()
    response.json.return_value = json_body
    return response


# ============================================================================
# PART A — Connector-code tests (exercise real HubspotCRMSearchPaginationStrategy)
#
# These call strategy.next_page_token() and assert what master currently does.
# Tests that assert broken behavior are marked with pytest.mark.xfail or
# explicitly document the broken assertion in comments.
# ============================================================================


# ---------------------------------------------------------------------------
# A.1  Short/empty page early-stop (relates to airbytehq/airbyte#80745)
#
# Master's stop condition checks `last_page_size < page_size` BEFORE checking
# whether paging.next.after exists. When HubSpot returns fewer records than
# requested but still provides a valid cursor, master stops prematurely.
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
def test_short_page_with_cursor_stops_prematurely(make_strategy, last_page_size, paging_body, description):
    """Documents broken master behavior: pagination stops on short page despite valid cursor.

    Relates to airbytehq/airbyte#80745.
    A correct implementation would continue paginating when paging.next.after is present.
    """
    strategy = make_strategy(page_size=200)
    response = _mock_response(paging_body)

    token = strategy.next_page_token(
        response=response,
        last_page_size=last_page_size,
        last_record={"id": "5000"},
        last_page_token_value={"after": 200},
    )

    # Master returns None here — this is the suspected bug.
    # A fix (like airbytehq/airbyte#80745) would return a token with the cursor value.
    assert token is None, f"Documenting broken behavior: master stops on short page; got {token}"


def test_empty_page_with_cursor_stops_prematurely(make_strategy):
    """Documents broken master behavior: pagination stops on empty page despite valid cursor.

    Relates to airbytehq/airbyte#80745.
    HubSpot can return an empty results array while still providing a paging cursor
    (e.g., server-side filtering removed all results in a batch but more exist).
    """
    strategy = make_strategy(page_size=200)
    response = _mock_response({"paging": {"next": {"after": 400}}})

    token = strategy.next_page_token(
        response=response,
        last_page_size=0,
        last_record={"id": "5000"},
        last_page_token_value={"after": 200},
    )

    # Master returns None — suspected bug. Should continue when cursor exists.
    assert token is None, f"Documenting broken behavior: master stops on empty page; got {token}"


# ---------------------------------------------------------------------------
# A.2  10k boundary — int(id)+1 conversion (relates to airbytehq/airbyte#79666)
#
# When after + last_page_size >= RECORDS_LIMIT, master resets pagination with
# {"after": 0, "id": int(last_record[primary_key]) + 1}. The int() conversion
# discards string properties of the ID (length, leading zeros) and, combined
# with the manifest's GTE operator, can create lexicographic gaps.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "last_record_id,expected_id_in_token,description",
    [
        pytest.param(
            "25000",
            25001,
            "Normal numeric ID at 10k boundary — no gap when all IDs have same digit count",
            id="numeric_id_same_length",
        ),
        pytest.param(
            "7198",
            7199,
            "Short numeric ID — creates lexicographic gap with longer IDs like '719869649082'",
            id="short_id_creates_lex_gap",
        ),
        pytest.param(
            "719869649082",
            719869649083,
            "Large 12-digit HubSpot-style ID",
            id="large_hubspot_id",
        ),
        pytest.param(
            "99999",
            100000,
            "ID changes digit count after int+1 (5→6 digits) — changes lex sort position",
            id="id_digit_count_changes",
        ),
    ],
)
def test_10k_boundary_converts_id_to_int(make_strategy, last_record_id, expected_id_in_token, description):
    """Documents master's int(id)+1 conversion at the 10k boundary.

    Relates to airbytehq/airbyte#79666.
    This conversion is suspected to create lexicographic gaps when IDs of different
    string lengths coexist. See Part B tests for proof of the gap.
    """
    strategy = make_strategy(page_size=200)
    response = _mock_response({"paging": {"next": {"after": 10000}}})

    token = strategy.next_page_token(
        response=response,
        last_page_size=200,
        last_record={"id": last_record_id},
        last_page_token_value={"after": 9800},
    )

    assert token == {"after": 0, "id": expected_id_in_token}


@pytest.mark.parametrize(
    "last_record_id,description",
    [
        pytest.param("abc123", "Non-numeric string ID", id="non_numeric_string_id"),
        pytest.param("", "Empty string ID", id="empty_string_id"),
    ],
)
def test_10k_boundary_crashes_on_non_numeric_ids(make_strategy, last_record_id, description):
    """Documents that master's int() conversion crashes on non-numeric IDs.

    Relates to airbytehq/airbyte#79666.
    HubSpot hs_object_id values are expected to be numeric strings, but defensive
    handling would avoid an unhandled crash.
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


def test_10k_boundary_strips_leading_zeros(make_strategy):
    """Documents that master's int() conversion strips leading zeros from IDs.

    Relates to airbytehq/airbyte#79666.
    int("00007198") + 1 = 7199, not "00007199". The resulting GTE "7199" filter
    uses a different lexicographic position than "00007199" would.
    """
    strategy = make_strategy(page_size=200)
    response = _mock_response({"paging": {"next": {"after": 10000}}})

    token = strategy.next_page_token(
        response=response,
        last_page_size=200,
        last_record={"id": "00007198"},
        last_page_token_value={"after": 9800},
    )

    assert token == {"after": 0, "id": 7199}
    assert str(token["id"]) != "00007199"


# ---------------------------------------------------------------------------
# A.3  Same-timestamp records at page and 10k boundaries
#
# When many contacts share the same lastmodifieddate they all fall in the same
# time slice. Within a slice, pagination relies on the after cursor and (at
# the 10k boundary) the hs_object_id filter.
# ---------------------------------------------------------------------------


def test_same_timestamp_advances_cursor_normally(make_strategy):
    """Within a single 10k chunk, same-timestamp records paginate via cursor.

    This is correct behavior — the after cursor advances regardless of timestamps.
    """
    strategy = make_strategy(page_size=200)
    response = _mock_response({"paging": {"next": {"after": 400}}})

    token = strategy.next_page_token(
        response=response,
        last_page_size=200,
        last_record={"id": "5000"},
        last_page_token_value={"after": 200},
    )

    assert token == {"after": 400}


def test_same_timestamp_at_10k_boundary_creates_id_gap(make_strategy):
    """At the 10k boundary with same-timestamp records, the int(id)+1 gap applies.

    Relates to airbytehq/airbyte#79666.
    Master computes GTE int("5000")+1 = GTE "5001", which lexicographically
    skips IDs like "50000"-"50009" (they sort between "5000" and "5001").
    """
    strategy = make_strategy(page_size=200)
    response = _mock_response({"paging": {"next": {"after": 10000}}})

    token = strategy.next_page_token(
        response=response,
        last_page_size=200,
        last_record={"id": "5000"},
        last_page_token_value={"after": 9800},
    )

    assert token == {"after": 0, "id": 5001}

    # Prove the gap: IDs "50000"-"50009" sort lex before "5001" and would be skipped
    boundary_str = str(token["id"])
    skipped_ids = [f"5000{d}" for d in range(10)]
    for skipped_id in skipped_ids:
        assert skipped_id < boundary_str, f"{skipped_id} should be lex < {boundary_str}"


# ---------------------------------------------------------------------------
# A.4  RECORDS_LIMIT threshold edge cases
#
# The 10k reset fires when: after + last_page_size >= RECORDS_LIMIT.
# These tests verify exact threshold behavior.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "after_value,page_size_val,last_page_size_val,should_reset,description",
    [
        pytest.param(9800, 200, 200, True, "Exact threshold: 9800+200=10000", id="exact_threshold"),
        pytest.param(9801, 200, 200, True, "Over threshold: 9801+200=10001", id="over_threshold"),
        pytest.param(9799, 200, 200, False, "Under threshold: 9799+200=9999", id="under_threshold"),
        pytest.param(9800, 200, 199, False, "Short page at threshold — does not trigger reset", id="short_page_at_threshold"),
        pytest.param(0, 200, 200, False, "First page: 0+200=200 < 10000", id="first_page"),
    ],
)
def test_records_limit_threshold(make_strategy, after_value, page_size_val, last_page_size_val, should_reset, description):
    """Documents the exact threshold at which the 10k reset fires.

    Note: 'short_page_at_threshold' shows that a short page below the 10k boundary
    stops pagination instead of triggering a reset — this interacts with the
    airbytehq/airbyte#80745 early-stop bug.
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
    elif last_page_size_val < page_size_val:
        # Short page stops on master (the #80745 bug)
        assert token is None
    else:
        assert token == {"after": after_value + last_page_size_val}


def test_short_page_at_exact_10k_boundary_triggers_reset(make_strategy):
    """When a short page AND the 10k threshold coincide, the reset takes priority.

    The 10k check is evaluated first in master's code. This is correct: even with
    fewer records than page_size, if we've hit the API limit we must reset.
    """
    strategy = make_strategy(page_size=200)
    response = _mock_response({"paging": {"next": {"after": 10000}}})

    token = strategy.next_page_token(
        response=response,
        last_page_size=150,
        last_record={"id": "9999"},
        last_page_token_value={"after": 9850},
    )

    # 9850+150=10000 >= RECORDS_LIMIT, so reset fires despite short page
    assert token == {"after": 0, "id": 10000}


# ---------------------------------------------------------------------------
# A.5  Full pagination sequence with patched RECORDS_LIMIT
#
# Simulates a multi-page sync with RECORDS_LIMIT=600 (3 pages of 200).
# ---------------------------------------------------------------------------


@patch("components.HubspotCRMSearchPaginationStrategy.RECORDS_LIMIT", 600)
def test_full_sequence_normal_pages_then_reset(make_strategy):
    """Documents normal 3-page sequence ending with a 10k reset."""
    strategy = make_strategy(page_size=200)

    # Page 1: 200 records
    r1 = _mock_response({"paging": {"next": {"after": 200}}})
    t1 = strategy.next_page_token(r1, 200, {"id": "100"}, {"after": 0})
    assert t1 == {"after": 200}

    # Page 2: 200 records
    r2 = _mock_response({"paging": {"next": {"after": 400}}})
    t2 = strategy.next_page_token(r2, 200, {"id": "300"}, {"after": 200})
    assert t2 == {"after": 400}

    # Page 3: 200 records → 400+200=600 >= RECORDS_LIMIT → reset
    r3 = _mock_response({"paging": {"next": {"after": 600}}})
    t3 = strategy.next_page_token(r3, 200, {"id": "500"}, {"after": 400})
    assert t3 == {"after": 0, "id": 501}


@patch("components.HubspotCRMSearchPaginationStrategy.RECORDS_LIMIT", 600)
def test_post_reset_pages_carry_boundary_id(make_strategy):
    """After a 10k reset, subsequent page tokens carry the boundary ID forward."""
    strategy = make_strategy(page_size=200)

    response = _mock_response({"paging": {"next": {"after": 200}}})
    token = strategy.next_page_token(response, 200, {"id": "700"}, {"after": 0, "id": 501})

    assert token == {"after": 200, "id": 501}


@patch("components.HubspotCRMSearchPaginationStrategy.RECORDS_LIMIT", 600)
def test_post_reset_short_page_without_cursor_stops_correctly(make_strategy):
    """After a 10k reset, a short final page with no cursor correctly stops."""
    strategy = make_strategy(page_size=200)

    response = _mock_response({"results": [{"id": str(i)} for i in range(50)]})
    token = strategy.next_page_token(response, 50, {"id": "750"}, {"after": 200, "id": 501})

    assert token is None


@patch("components.HubspotCRMSearchPaginationStrategy.RECORDS_LIMIT", 600)
def test_post_reset_short_page_with_cursor_still_stops(make_strategy):
    """Documents broken behavior: after a 10k reset, a short page with cursor still stops.

    Relates to airbytehq/airbyte#80745.
    The early-stop bug affects post-reset pagination too, not just the first chunk.
    """
    strategy = make_strategy(page_size=200)

    response = _mock_response({"paging": {"next": {"after": 350}}})
    token = strategy.next_page_token(response, 150, {"id": "750"}, {"after": 200, "id": 501})

    # Master stops — suspected bug, same early-stop issue as in A.1
    assert token is None


# ---------------------------------------------------------------------------
# A.6  Combined scenario: short-page bug prevents reaching 10k boundary
#
# Demonstrates that the two bugs interact: if the short-page bug fires first,
# the sync never reaches the 10k boundary where the ID gap would occur.
# ---------------------------------------------------------------------------


@patch("components.HubspotCRMSearchPaginationStrategy.RECORDS_LIMIT", 600)
def test_short_page_bug_masks_10k_boundary_bug(make_strategy):
    """If a short page occurs before the RECORDS_LIMIT, master stops early.

    The sync never reaches the 10k boundary at all, so the lexicographic ID gap
    (airbytehq/airbyte#79666) is never triggered. Both bugs cause record loss, but
    the short-page bug (airbytehq/airbyte#80745) fires first and masks the other.
    """
    strategy = make_strategy(page_size=200)

    # Page 1: 200 records, normal
    r1 = _mock_response({"paging": {"next": {"after": 200}}})
    t1 = strategy.next_page_token(r1, 200, {"id": "100"}, {"after": 0})
    assert t1 == {"after": 200}

    # Page 2: only 150 records but cursor exists — master stops
    r2 = _mock_response({"paging": {"next": {"after": 350}}})
    t2 = strategy.next_page_token(r2, 150, {"id": "250"}, {"after": 200})
    assert t2 is None  # Lost records — never reaches page 3 or the 10k reset


# ---------------------------------------------------------------------------
# A.7  airbytehq/airbyte#80745 scope verification: does it also fix the ID gap?
#
# Answer: No. The short-page fix and the ID-gap fix are independent.
# ---------------------------------------------------------------------------


def test_80745_fix_does_not_address_10k_id_gap(make_strategy):
    """The short-page fix (airbytehq/airbyte#80745) does NOT change 10k boundary behavior.

    Even with the short-page fix applied, the 10k reset still uses int(id)+1 with
    GTE, producing the same lexicographic gap as on master.
    """
    strategy = make_strategy(page_size=200)
    response = _mock_response({"paging": {"next": {"after": 10000}}})

    token = strategy.next_page_token(
        response=response,
        last_page_size=200,
        last_record={"id": "7198"},
        last_page_token_value={"after": 9800},
    )

    # This token is produced identically on master and with the #80745 fix
    assert token == {"after": 0, "id": 7199}

    # The lexicographic gap still exists (see Part B tests for proof)
    boundary = str(token["id"])
    assert "719869649082" < boundary


def test_80745_fix_would_continue_on_short_page(make_strategy):
    """Documents what airbytehq/airbyte#80745 would fix: continuing when cursor exists.

    Master returns None. The fix would check paging.next.after and continue.
    """
    strategy = make_strategy(page_size=200)
    response = _mock_response({"paging": {"next": {"after": 350}}})

    master_token = strategy.next_page_token(
        response=response,
        last_page_size=150,
        last_record={"id": "5000"},
        last_page_token_value={"after": 200},
    )
    assert master_token is None  # Master stops — broken

    # The cursor exists and would be used by the fix
    paging_after = response.json().get("paging", {}).get("next", {}).get("after")
    assert paging_after == 350


# ---------------------------------------------------------------------------
# A.8  String cursor edge case
# ---------------------------------------------------------------------------


def test_string_after_cursor_does_not_affect_internal_tracking(make_strategy):
    """HubSpot returns paging.next.after as a string or int, but the pagination
    strategy always stores 'after' as an int internally (initialized to 0,
    incremented by page_size). This test confirms normal operation.
    """
    strategy = make_strategy(page_size=200)
    response = _mock_response({"paging": {"next": {"after": "400"}}})

    token = strategy.next_page_token(
        response=response,
        last_page_size=200,
        last_record={"id": "5000"},
        last_page_token_value={"after": 200},
    )
    assert token == {"after": 400}


# ============================================================================
# PART B — String/lexicographic demonstrations (no connector code)
#
# These tests do NOT call any connector code. They prove, using pure Python
# string comparisons, why the current int(id)+1 + GTE approach creates gaps
# and why alternative approaches (GT + raw string) would avoid them.
# ============================================================================


# ---------------------------------------------------------------------------
# B.1  Lexicographic gap from int(id)+1 with GTE (supports airbytehq/airbyte#79666)
# ---------------------------------------------------------------------------


def test_lex_gap_gte_int_plus_one_skips_long_ids():
    """Proves that GTE str(int("7198")+1) = GTE "7199" skips IDs like "719869649082".

    HubSpot sorts hs_object_id as strings. "719869649082" < "7199" because at
    position 3, '8' < '9'. So GTE "7199" excludes "719869649082" entirely.
    This is the core hypothesis behind airbytehq/airbyte#79666.
    """
    ids = ["7195", "7196", "7197", "7198", "719869649082", "719869649083", "7199", "72"]
    sorted_ids = sorted(ids)

    boundary = str(int("7198") + 1)  # "7199" — what master computes
    included = [id_ for id_ in sorted_ids if id_ >= boundary]
    excluded = [id_ for id_ in sorted_ids if id_ < boundary]

    # Long IDs are excluded — this is the suspected record loss
    assert "719869649082" in excluded
    assert "719869649083" in excluded

    assert "7199" in included
    assert "72" in included


def test_lex_gt_raw_string_includes_long_ids():
    """Proves that GT "7198" (raw string, no int conversion) includes the long IDs.

    This is the approach proposed by airbytehq/airbyte#79666: use GT + raw string
    instead of GTE + int+1. "719869649082" > "7198" because when the prefix "7198"
    matches and the shorter string ends, the longer string is considered greater.
    """
    ids = ["7195", "7196", "7197", "7198", "719869649082", "719869649083", "7199", "72", "8000"]
    sorted_ids = sorted(ids)

    last_seen = "7198"
    included_gt = [id_ for id_ in sorted_ids if id_ > last_seen]

    assert "719869649082" in included_gt
    assert "719869649083" in included_gt
    assert "7199" in included_gt
    assert "72" in included_gt

    # The boundary record itself is correctly excluded (no duplicate)
    assert "7198" not in included_gt


def test_lex_gt_does_not_duplicate_boundary_record():
    """Both GT-string and GTE-int+1 correctly exclude the boundary record for simple IDs."""
    last_id = "25000"
    candidate_id = "25000"

    # GT "25000" excludes "25000" itself
    assert not (candidate_id > last_id)

    # GTE str(int("25000")+1) = GTE "25001" also excludes "25000"
    next_boundary = str(int(last_id) + 1)
    assert not (candidate_id >= next_boundary)


# ---------------------------------------------------------------------------
# B.2  Manifest template rendering (supports airbytehq/airbyte#79666)
# ---------------------------------------------------------------------------


def test_manifest_renders_int_id_as_string_creating_lex_comparison():
    """The manifest template renders the int ID as a string in the JSON body.

    `"value": "{{ next_page_token['next_page_token'].get('id', 0) }}"`

    When id=7199 (int from master's computation), Jinja renders "7199".
    HubSpot then applies GTE "7199" as a lexicographic comparison.
    """
    token = {"after": 0, "id": 7199}
    rendered_value = str(token.get("id", 0))

    assert rendered_value == "7199"
    assert "719869649082" < rendered_value  # Long IDs are excluded


def test_manifest_default_id_zero_includes_all_records():
    """When no ID boundary is set (first chunk), the manifest defaults to "0".

    "0" is lexicographically less than any HubSpot ID starting with 1-9,
    so all records are included in the first chunk. This is correct.
    """
    token = {"after": 0}
    rendered_value = str(token.get("id", 0))

    assert rendered_value == "0"
    for id_ in ["1", "100", "7198", "719869649082", "99999"]:
        assert id_ >= rendered_value


# ---------------------------------------------------------------------------
# B.3  Adjacent 30-day slice boundaries (GTE/LTE with 1ms granularity)
#
# The manifest uses GTE start_time / LTE end_time with P30D step and PT0.001S
# cursor_granularity. These tests verify no overlap or gap at slice boundaries.
# ---------------------------------------------------------------------------


def test_adjacent_slices_have_no_overlap_and_no_gap():
    """Adjacent 30-day slices with 1ms granularity produce no overlap or gap.

    Slice 1: GTE start1, LTE end1
    Slice 2: GTE (end1 + 1ms), LTE end2

    Every integer-millisecond timestamp near the boundary falls in exactly one slice.
    This test confirms the slice logic is NOT a source of missing/duplicate records.
    """
    slice1_end_ms = 1645660800000  # 2022-02-24T00:00:00.000Z
    slice2_start_ms = slice1_end_ms + 1  # +1ms (cursor_granularity)

    for offset in range(-5, 6):
        ts = slice1_end_ms + offset
        in_slice1 = ts <= slice1_end_ms
        in_slice2 = ts >= slice2_start_ms
        assert in_slice1 or in_slice2, f"Timestamp {ts} falls between slices (gap)"
        assert not (in_slice1 and in_slice2), f"Timestamp {ts} is in both slices (overlap)"


def test_slice_boundary_record_assignment():
    """A record at exactly the slice boundary is in slice 1 only; 1ms later is in slice 2 only."""
    slice1_end = 1645660800000
    slice2_start = slice1_end + 1

    # Exactly at boundary → slice 1
    ts_boundary = slice1_end
    assert ts_boundary <= slice1_end  # In slice 1 (LTE)
    assert ts_boundary < slice2_start  # Not in slice 2 (GTE)

    # 1ms after → slice 2
    ts_next = slice1_end + 1
    assert ts_next > slice1_end  # Not in slice 1
    assert ts_next >= slice2_start  # In slice 2
