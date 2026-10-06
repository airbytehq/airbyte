"""Verify that Peec's offset paging neither drops nor repeats rows.

`report_paginator` walks /reports/* with limit+offset and stops on a short page.
Offset paging is only sound when the server applies a total order: if two rows can
swap places between requests, a row sitting on a page boundary can be served twice
or skipped. `order_by` accepts only metric columns (never brand/domain/url), so we
cannot pin the order from our side -- it has to be measured.

What the measurement found (2026-08, /reports/urls, 37,844 rows):

  * Peec does NOT expose a total order. Two consecutive walks at the same page size
    return the same rows in a DIFFERENT sequence, so row position is meaningless.
  * Even so, every walk returns exactly the same multiset of rows. Walked at page
    sizes 10000 / 7000 / 5000 -- which put the page boundaries in different places
    -- and twice more at 10000: 0 rows lost and 0 rows repeated, every time.

So paging here is safe empirically, not by construction. This script asserts the
invariant that matters -- the multiset of rows must not depend on the page size --
and deliberately does NOT assert row positions, which are known to vary. If Peec
ever starts losing or repeating rows across a boundary, this fails.

It talks to the real API, so it lives here rather than in unit_tests/: the mock in
unit_tests/test_manifest.py defines its own ordering and can say nothing about Peec's.

    export PEEC_API_KEY=<your key>
    python3 integration_tests/check_paging_stability.py            # last full month
    python3 integration_tests/check_paging_stability.py 2026-08    # a specific month

Exits non-zero if any walk disagrees.
"""

import calendar
import collections
import datetime as dt
import json
import os
import sys
import urllib.request

URL_BASE = "https://api.peec.ai/customer/v1"
SHIPPED_PAGE_SIZE = 10000
PAGE_SIZES = (10000, 7000, 5000)
OVER_MAX = 15000


def month_bounds(month):
    y, m = (int(x) for x in month.split("-"))
    return "%s-01" % month, "%s-%02d" % (month, calendar.monthrange(y, m)[1])


def fetch(api_key, path, start, end, limit, offset):
    body = json.dumps({
        "dimensions": ["month", "model_channel_id"],
        "start_date": start, "end_date": end,
        "limit": limit, "offset": offset,
    }).encode()
    req = urllib.request.Request(
        URL_BASE + path, data=body, method="POST",
        headers={"x-api-key": api_key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)["data"]


def walk(api_key, path, start, end, page_size):
    rows, offset = [], 0
    while True:
        page = fetch(api_key, path, start, end, page_size, offset)
        rows += page
        if len(page) < page_size:
            return rows
        offset += page_size


def multiset(rows):
    return collections.Counter(json.dumps(r, sort_keys=True) for r in rows)


def describe(blob):
    d = json.loads(blob)
    return "%s | %s | retrievals=%s" % (
        (d.get("url") or d.get("domain") or "")[:60],
        (d.get("model_channel") or {}).get("id"), d.get("retrievals"))


def main():
    api_key = os.environ.get("PEEC_API_KEY")
    if not api_key:
        sys.exit("PEEC_API_KEY is not set (see the module docstring)")

    month = sys.argv[1] if len(sys.argv) > 1 else (
        dt.date.today().replace(day=1) - dt.timedelta(days=1)).strftime("%Y-%m")
    start, end = month_bounds(month)
    path = "/reports/urls"
    print("month %s  (%s .. %s)  endpoint %s" % (month, start, end, path))

    failures = []

    print("\n-- the shipped page_size must be the API maximum --")
    try:
        fetch(api_key, path, start, end, SHIPPED_PAGE_SIZE, 0)
        print("  limit=%-6d accepted" % SHIPPED_PAGE_SIZE)
    except Exception as exc:
        failures.append("limit=%d rejected (%s)" % (SHIPPED_PAGE_SIZE, exc))
    try:
        fetch(api_key, path, start, end, OVER_MAX, 0)
        failures.append("limit=%d was accepted -- the maximum rose, raise page_size" % OVER_MAX)
        print("  limit=%-6d accepted (unexpected)" % OVER_MAX)
    except Exception as exc:
        print("  limit=%-6d rejected (%s) -> %d is still the ceiling"
              % (OVER_MAX, exc, SHIPPED_PAGE_SIZE))

    print("\n-- the same rows must come back at every page size --")
    walks = {}
    for ps in PAGE_SIZES:
        rows = walk(api_key, path, start, end, ps)
        walks[ps] = rows
        print("  page_size=%-6d rows=%-7d retrievals=%d"
              % (ps, len(rows), sum(r.get("retrievals") or 0 for r in rows)))

    ref_ps = PAGE_SIZES[0]
    ref = multiset(walks[ref_ps])
    for ps in PAGE_SIZES[1:]:
        cur = multiset(walks[ps])
        missing, extra = ref - cur, cur - ref
        if missing or extra:
            failures.append("page_size=%d differs from %d: %d row(s) missing, %d extra"
                            % (ps, ref_ps, sum(missing.values()), sum(extra.values())))
            for b, n in list(missing.items())[:3]:
                print("    MISSING x%d: %s" % (n, describe(b)))
            for b, n in list(extra.items())[:3]:
                print("    EXTRA   x%d: %s" % (n, describe(b)))
        else:
            print("  page_size=%-6d identical multiset to page_size=%d" % (ps, ref_ps))

    print("\n-- and at the same page size, twice running --")
    again = walk(api_key, path, start, end, ref_ps)
    if multiset(again) != ref:
        failures.append("two walks at page_size=%d returned different rows" % ref_ps)
    else:
        same_order = [json.dumps(r, sort_keys=True) for r in again] == \
                     [json.dumps(r, sort_keys=True) for r in walks[ref_ps]]
        print("  identical multiset: yes")
        print("  identical order   : %s  (not asserted -- Peec exposes no total order)"
              % ("yes" if same_order else "no"))

    dup = {k: n for k, n in collections.Counter(
        (r.get("month"), r.get("url"), (r.get("model_channel") or {}).get("id"))
        for r in walks[ref_ps]).items() if n > 1}
    print("\n-- the API's own grain (not a paging fault) --")
    print("  %d key(s) appear more than once, %d extra row(s); these must be SUMmed, not deduped"
          % (len(dup), sum(n - 1 for n in dup.values())))

    if failures:
        print("\nFAIL")
        for f in failures:
            print("  -", f)
        sys.exit(1)
    print("\nOK: paging returns the same rows regardless of page size -- nothing lost, nothing repeated.")


if __name__ == "__main__":
    main()
