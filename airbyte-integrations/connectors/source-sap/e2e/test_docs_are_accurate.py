"""The one documentation claim that needs a real SAP system to check.

`docs/authorizations.md` is the list a Basis team grants S_RFC from, and only
ERPL loaded against a live system can say what function modules belong on it.
The claims a filesystem can settle live in `unit_tests/test_docs_are_accurate.py`,
so they run on every commit rather than only when credentials are present.
"""

from __future__ import annotations

import pathlib

import pytest

DOCS = pathlib.Path(__file__).resolve().parents[2] / "docs"


class TestAuthorizationsPageIsComplete:
    """`docs/authorizations.md` is handed to a Basis team to grant S_RFC from.

    A module the connector calls but the page omits is an authorization the team
    will not grant, and a sync that fails in production rather than here.
    """

    @pytest.mark.requires_creds
    def test_every_function_module_erpl_declares_is_documented(self, erpl_extensions):
        import duckdb

        con = duckdb.connect(config={"allow_unsigned_extensions": "true", "extension_directory": erpl_extensions})
        try:
            for extension in ("erpl_rfc", "erpl_bics", "erpl_odp"):
                con.load_extension(extension)
            declared = {
                row[0]
                for row in con.sql(
                    "SELECT DISTINCT rfc_function_module FROM sap_rfc_authorizations() "
                    "WHERE rfc_function_module NOT IN ('<user-specified>', '<none>')"
                ).fetchall()
            }
        finally:
            con.close()

        page = (DOCS / "authorizations.md").read_text()
        missing = sorted(module for module in declared if module not in page)
        assert not missing, (
            "docs/authorizations.md omits function modules the connector calls, so a "
            f"Basis team granting S_RFC from it would miss them: {', '.join(missing)}"
        )
        assert len(declared) > 20, "the declaration looks truncated"
