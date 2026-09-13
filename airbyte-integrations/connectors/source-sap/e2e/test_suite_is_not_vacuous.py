"""Guard against the e2e suite passing because everything skipped.

Skipping is correct when there is no SAP system. Reporting green when the suite
was *supposed* to run against one is not -- that is how incremental/state
conformance quietly stops being tested.
"""

from __future__ import annotations

import os

import pytest


def test_the_suite_ran_against_a_real_system_when_ci_said_it_would():
    if os.environ.get("ERPL_E2E_REQUIRED") != "1":
        pytest.skip("ERPL_E2E_REQUIRED is not set; skipping is allowed here.")

    required = {
        "ERPL_EXTENSION_DIR": "the baked ERPL extensions",
        "ERPL_SAP_ASHOST": "the SAP application server",
        "ERPL_SAP_PASSWORD": "the SAP password",
        "ERPL_SAP_BASE_URL": "the SAP Gateway base URL",
        "ERPL_SAP_ODP_CONTEXT": "the ODP context",
        "ERPL_SAP_ODP_NAME": "the ODP provider",
        "ERPL_SAP_ODP_ODATA_URL": "the ODP OData entity set",
        "ERPL_SAP_BICS_CUBE": "the BW InfoProvider",
    }
    missing = {name: what for name, what in required.items() if not os.environ.get(name)}
    assert not missing, (
        "ERPL_E2E_REQUIRED=1 promises a full e2e run, but these are unset, so the "
        "corresponding tests would skip and the suite would report green:\n  "
        + "\n  ".join(f"{name} ({what})" for name, what in sorted(missing.items()))
    )
