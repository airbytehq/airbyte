"""The documentation makes checkable claims. Check the ones a filesystem answers.

Documentation that is confidently wrong is worse than documentation that is
missing, and these particular claims drift: the spec gains settings, clamps get
retuned, pages get renamed out from under a link. None of that needs SAP, so it
is checked here rather than in `e2e/`, where it would only run when credentials
happen to be present.

The remaining claim -- that `docs/authorizations.md` lists every function module
ERPL calls -- does need a live system, and stays in `e2e/test_docs_are_accurate.py`.
"""

from __future__ import annotations

import pathlib
import re

import yaml

DOCS = pathlib.Path(__file__).resolve().parents[2] / "docs"
SPEC = yaml.safe_load((pathlib.Path(__file__).resolve().parents[1] / "source_sap" / "spec.yaml").read_text())


def _rfc_branch() -> dict:
    return next(
        b
        for b in SPEC["connectionSpecification"]["properties"]["protocol"]["oneOf"]
        if b["properties"]["mode"]["const"] == "rfc"
    )


class TestReferencePageMatchesTheSpec:
    def _limits(self) -> dict[str, str]:
        section = (DOCS / "reference.md").read_text().split("## Limits", 1)[1]
        rows = (
            line.strip("|").split("|") for line in section.splitlines() if line.startswith("|") and "---" not in line
        )
        return {r[0].strip("` "): r[1].strip() for r in rows if len(r) == 2}

    def test_every_protocol_mode_has_a_section(self):
        page = (DOCS / "reference.md").read_text()
        modes = {
            b["properties"]["mode"]["const"] for b in SPEC["connectionSpecification"]["properties"]["protocol"]["oneOf"]
        }
        missing = [m for m in modes if f"`{m}`" not in page]
        assert not missing, f"reference.md documents no section for: {missing}"

    def test_the_concurrency_range_matches(self):
        prop = SPEC["connectionSpecification"]["properties"]["concurrency"]
        assert self._limits()["concurrency"] == f"{prop['minimum']}–{prop['maximum']}"

    def test_the_partitions_range_matches(self):
        prop = _rfc_branch()["properties"]["partitions"]
        assert self._limits()["partitions"] == f"{prop['minimum']}–{prop['maximum']}"

    def test_the_documented_fetch_size_cap_matches_the_code(self):
        from source_sap.protocols.rfc import MAX_FETCH_SIZE

        assert f"{MAX_FETCH_SIZE:,}" in self._limits()["fetch_size"]

    def test_partitions_still_defaults_to_zero(self):
        # The performance document argues at length for this default.
        assert _rfc_branch()["properties"]["partitions"]["default"] == 0


class TestReferenceDocumentsEveryField:
    """`docs/reference.md` claims to list every field, and is maintained by hand.

    It had already drifted: `return_parameter` was documented but missing from
    the spec, and BICS filters, variants and display properties were supported
    by the driver but reachable from neither.
    """

    def _documented(self) -> dict[str | None, set[str]]:
        """Field names per page section, keyed by the protocol the section heads.

        Per section, not page-wide: `objects[].filter` would otherwise count as
        documented for `bics` purely because `filter` is backticked in the `rfc`
        section, and the page would be certified complete for a protocol that
        never mentions it.
        """
        modes = {
            branch["properties"]["mode"]["const"]
            for branch in SPEC["connectionSpecification"]["properties"]["protocol"]["oneOf"]
        }
        by_section: dict[str | None, set[str]] = {None: set()}
        section: str | None = None
        for line in (DOCS / "reference.md").read_text().splitlines():
            if line.startswith("## "):
                heading = re.match(r"## `([a-z_]+)`", line)
                section = heading.group(1) if heading and heading.group(1) in modes else None
            names = set(re.findall(r"`([a-z_]+(?:\[\]\.[a-z_]+)?)`", line))
            by_section.setdefault(section, set()).update(names)
            if section is None:
                # Connection and Limits apply to every protocol.
                for mode in modes:
                    by_section.setdefault(mode, set()).update(names)
        return by_section

    def _spec_fields(self) -> set[str]:
        fields = set()
        for branch in SPEC["connectionSpecification"]["properties"]["protocol"]["oneOf"]:
            for name in branch["properties"]:
                if name != "mode":
                    fields.add(name)
            items = (branch["properties"].get("objects") or {}).get("items", {})
            for name in items.get("properties", {}):
                fields.add(f"objects[].{name}")
        for name in SPEC["connectionSpecification"]["properties"]:
            if name != "protocol":
                fields.add(name)
        return fields

    def _spec_fields_by_mode(self) -> dict[str, set[str]]:
        shared = {n for n in SPEC["connectionSpecification"]["properties"] if n != "protocol"}
        by_mode = {}
        for branch in SPEC["connectionSpecification"]["properties"]["protocol"]["oneOf"]:
            fields = {n for n in branch["properties"] if n != "mode"}
            items = (branch["properties"].get("objects") or {}).get("items", {})
            fields.update(f"objects[].{n}" for n in items.get("properties", {}))
            by_mode[branch["properties"]["mode"]["const"]] = fields | shared
        return by_mode

    def test_every_spec_field_appears_in_the_reference(self):
        documented = self._documented()
        missing = []
        for mode, fields in self._spec_fields_by_mode().items():
            known = documented.get(mode, set()) | documented[None]
            for field in fields:
                if field not in known and field.split("].")[-1] not in known:
                    missing.append(f"{field} (under {mode})")
        assert not missing, "docs/reference.md says it lists every field but omits: " + ", ".join(sorted(missing))

    def _branch_fields(self) -> dict[str, set[str]]:
        """Field names per protocol mode, plus the shared connection fields."""
        shared = {name for name in SPEC["connectionSpecification"]["properties"] if name != "protocol"}
        by_mode = {}
        for branch in SPEC["connectionSpecification"]["properties"]["protocol"]["oneOf"]:
            fields = {name for name in branch["properties"] if name != "mode"}
            items = (branch["properties"].get("objects") or {}).get("items", {})
            fields.update(items.get("properties", {}))
            by_mode[branch["properties"]["mode"]["const"]] = fields | shared
        return by_mode

    def test_every_field_the_reference_names_exists_in_the_spec(self):
        """The other direction, and per protocol: a setting nobody can configure.

        `threads` was listed under the RFC limits and honoured by the RFC driver,
        but only the `odp_rfc` branch offered it -- so the page told RFC users
        about a knob their configuration form did not have. Pooling field names
        across the five branches hides exactly that, which is why this walks each
        branch separately: a page section headed `rfc` is checked against the
        `rfc` branch.
        """
        page = (DOCS / "reference.md").read_text()
        by_mode = self._branch_fields()
        unknown = []
        mode = None
        for line in page.splitlines():
            if line.startswith("## "):
                # "## `rfc` -- tables and CDS views", or a prose heading.
                heading = re.match(r"## `([a-z_]+)`", line)
                mode = heading.group(1) if heading and heading.group(1) in by_mode else None
            if not line.startswith("| `"):
                continue
            for name in re.findall(r"`([a-z_]+(?:\[\]\.[a-z_]+)?)`", line.split("|")[1]):
                leaf = name.split("].")[-1]
                # Outside a protocol section (Connection, Limits), a name qualified
                # with its mode -- "`threads` (rfc)" -- says which branch to check.
                qualified = re.search(rf"`{re.escape(name)}`\s*\((\w+)\)", line)
                scope = qualified.group(1) if qualified and qualified.group(1) in by_mode else mode
                known = by_mode[scope] if scope else set().union(*by_mode.values())
                if leaf not in known:
                    unknown.append(f"{leaf}" + (f" (under {scope})" if scope else ""))
        assert not unknown, (
            "docs/reference.md documents settings the spec does not offer there, so "
            "nobody can set them from the UI: " + ", ".join(sorted(set(unknown)))
        )


class TestInternalLinksResolve:
    def test_no_documentation_link_is_broken(self):
        root = DOCS.parent
        broken = []
        # Every tracked page, not just docs/: source-sap/README.md and the
        # connector's own docs/integrations page link across the tree too, and a
        # checker that skips them is a checker that says "no broken links" about
        # the files nobody checked.
        pages = list(root.glob("*.md")) + list(root.glob("docs/**/*.md")) + list(root.glob("source-sap/**/*.md"))
        for md in pages:
            if any(part in {".venv", "node_modules", ".crew", ".erpl", ".pytest_cache"} for part in md.parts):
                continue
            for label, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", md.read_text()):
                if target.startswith(("http", "#", "mailto:")):
                    continue
                if not (md.parent / target.split("#")[0]).resolve().exists():
                    broken.append(f"{md.relative_to(root)}: [{label}]({target})")
        assert not broken, "broken documentation links:\n  " + "\n  ".join(broken)
