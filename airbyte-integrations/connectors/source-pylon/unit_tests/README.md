# Pylon synthetic tests

## Fixture provenance

The JSON records in `resource/http/response/` are synthetic. Their source is the
Pylon OpenAPI snapshot identified by `_provenance.json` in that directory:

- URL: <https://api.usepylon.com/openapi.json>
- Fetch date: `2026-11-04`
- SHA256: `d2cc304c18073042c147d29cd893426d80a13f912e6626635fefd7b1377376bc`

Values were generated recursively from each endpoint's successful response
`data.items` schema. `_provenance.json` maps streams to endpoint paths. No API
examples, customer records, or real credentials were used. Tests adapt those
records to construct pages, time boundaries, parent relationships, and failures.
The snapshot is not checked in; the hash identifies the exact source bytes, not
the current live OpenAPI document.

## Running the tests

Install the dependencies in `pyproject.toml` in a Python 3.10–3.12 environment.
The suite pins `airbyte-cdk` to `7.45.1`. From this directory, run:

```sh
PYTHONPATH=. python -m pytest -ra --tb=short
```

The coverage gate is 90% for `components.py`, not for the CDK or the manifest.
To print the all-streams table and write its per-stream properties to JUnit:

```sh
PYTHONPATH=. python -m pytest mock_server/test_all_streams.py --no-cov -s --junitxml=all-streams.xml
```

## Coverage by area

| Area | Tests | Cases |
| --- | --- | --- |
| List endpoints | `mock_server/test_list_streams.py` | All 11 list streams, empty responses, pagination, deactivated users, check, discover |
| Issues | `mock_server/test_issues.py` | Inclusive filters, incremental state, two-pass reads, empty reads, 30-day seam bounds and unique record IDs |
| Interruption/resume | `mock_server/test_issues.py` | Non-retryable failure in the second window after a checkpoint; resume from emitted state and verify record multiplicities and final state |
| Child streams | `mock_server/test_child_streams.py` | Parent-key projection for all three children, missing parent keys in responses, empty parent sets |
| Errors | `test_error_handler.py`, `mock_server/test_error_handling.py` | Actionable authentication, region, permission and organization errors; generic and non-JSON failures; no silent 404 skips |
| Retry headers | `test_error_handler.py`, `mock_server/test_rate_limit_budget.py` | Retry-After alone, X-Retry-After alone, both, neither, excessive waits, retry exhaustion and recovery |
| API budget | `mock_server/test_rate_limit_budget.py` | All 15 endpoint allowances, rolling windows, response-driven exhaustion, method/path isolation, US/EU matching, concurrency cap |
| Regions | `mock_server/test_regions.py` | US/EU list, issues, child and check requests; missing-region default, host selection and wrong-region errors |
| Schema conformance | `test_schema_conformance.py` | All 15 synthetic fixtures against connector schemas, nullable fields, required fields and timestamp formats |
| Spec and acceptance config | `test_spec.py`, `test_acceptance_config.py` | Config validation, region/order/defaults, bypass reasons, spec and discover with HTTP and socket access blocked |
| All-streams smoke | `mock_server/test_all_streams.py` | One read selecting all 15 streams; at least one record each; printed table and JUnit properties |
| Components | `test_components.py` | Custom pagination logic |

### Acceptance tooling

From the connector directory, `airbyte-cdk connector test .` reads
`acceptance-test-config.yml`. In `.github/workflows/connector-ci-checks.yml`,
**Run Integration Tests** invokes `poe test-integration-tests`, which runs this
command. **Run Standard Tests (in-process)** invokes `poe test-standard-tests`.

The CDK calls the discover config section `discovery`. Spec and discovery use
`integration_tests/sample_config.json`, which contains an obviously fake token.
Discover uses inline schemas and does not need network access. Credential-based
sections have individual bypass reasons pointing to the mock-server tests because
there is no sandbox account. CDK 7.45.1 does not collect an `incremental` section;
its explicit bypass remains in the config, and the mock suite tests incremental
reads and resume. The standard suite's published-spec backward-compatibility test
does need registry network access, independently of offline spec and discover.

## Assumptions not provable from Pylon docs

- **Thread parent echo:** the OpenAPI marks `issue_threads.issue_id` required.
  Tests also remove it from synthetic responses to prove the connector projects
  the parent ID defensively. They do not establish that a live response omits it.
- **Deleted parents and 404:** the documented unknown-path meaning does not
  establish a deleted-parent contract. Child 404 tests prove failure rather than
  silent skipping, not how Pylon behaves if a parent disappears during a sync.
- **Retry timing:** the [rate-limit documentation](https://docs.usepylon.com/pylon-docs/developer/api/rate-limits.md)
  and OpenAPI 429 response headers document both retry headers. Retry-After is
  the wait before the next request can succeed; X-Retry-After is the longer wait
  until the full per-minute allowance is restored. The latter is a conservative
  fallback, not proof that every 429 contains it or that capacity cannot return
  sooner. Tests establish connector precedence and limits, not live timing.
  CDK 7.45.1 rejects header waits greater than or equal to the configured 120-second
  maximum. The [errors documentation](https://docs.usepylon.com/pylon-docs/developer/api/errors.md)
  links `rate_limited` to the rate-limit documentation.
- **EU behavior:** [authentication docs](https://docs.usepylon.com/pylon-docs/developer/api/authentication.md)
  and OpenAPI list the EU host. EU verification is mock-only; no EU account or
  token was used. Identical live behavior across hosts is not established here.
- **Legacy token region:** docs identify `pylon_api_eu_` and `pylon_api_` prefixes
  but do not establish the region of older unprefixed tokens. Select the tenant's
  region rather than inferring it from the absence of a prefix.
- **Child ID uniqueness:** existing primary keys use child `id` alone. Tests do
  not prove global child-ID uniqueness across parents; synthetic parent-key
  projection does not validate that API-wide uniqueness assumption.
- **Time and replay:** seam tests cover whole-second timestamps and disjoint
  windows within one read. Resume is inclusive of the checkpoint second, so the
  record exactly at that checkpoint is intentionally emitted again; the test
  permits only that replay, with no other duplicate or lost IDs. This is not an
  exactly-once guarantee. Fractional-second boundary behavior, late updates, and
  consistency while paginating are not established by these fixtures.
- **Budget scope:** fake-clock tests prove per-endpoint limits in one connector
  instance, not coordination with other API clients sharing an organization's
  allowance. Live service traffic and timing have not been tested.
- **Schema scope:** validation proves compatibility with the connector schemas
  for synthetic inputs. It does not prove that every live record or undocumented
  field has the same shape, or that role-restricted accounts expose every stream.
