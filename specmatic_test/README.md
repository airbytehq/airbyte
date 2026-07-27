# Stripe Connector — OpenAPI Contract Validation & Specmatic Integration Tests

This directory contains the tools, OpenAPI specifications, and scripts required to perform **automated OpenAPI contract validation** for the Airbyte Stripe source connector and to run **contract-driven integration tests** using a live **Specmatic** mock server.

> **Requirements**
>
> - Node.js 18+
> - Python 3.11+
> - Docker
> - Specmatic v2.50.1+

---

# Why?

The Stripe connector originally relied on **HttpMocker** and **requests-mock**, where every integration test used manually maintained JSON responses.

This approach introduced several limitations:

- Static mock responses become outdated as the Stripe API evolves.
- Contract drift between the connector and Stripe's API is difficult to detect.
- Mock responses require continuous manual maintenance.
- HTTP requests are not validated against the official OpenAPI contract.

This project introduces **[Specmatic](https://specmatic.io/)** to enable **contract-driven integration testing**, ensuring that both requests and responses conform to the Stripe OpenAPI specification.

---

# What Was Implemented?

## 1. OpenAPI Contract Validation

A dedicated validation runner executes the Stripe connector against a **Specmatic Mock Server**.

During execution, Specmatic validates:

- Outgoing connector requests
- Query parameters
- Response schemas
- Overall API contract compliance

```text
  Airbyte Connector
        │
        ▼
Specmatic Mock Server
        │
        ▼
Stripe OpenAPI Specification
        │
        ▼
After validation, Specmatic generates native **HTML** and **CTRF** reports under `build/reports/specmatic/`.

---

## 2. Specmatic-backed Integration Tests

Integration tests have been migrated from static **HttpMocker**-based mocks to **Specmatic**.

### Before

Instead of relying on hardcoded JSON files:

```text
HttpMocker
      │
      ▼
accounts.json
```

### After

Tests now communicate with a live **Specmatic Mock Server** generated from the Stripe OpenAPI specification.

```text
Stripe OpenAPI Specification
          │
          ▼
 Specmatic Mock Server
          │
          ▼
 Airbyte Stripe Connector
          │
          ▼
 Test Assertions
```

Every HTTP request sent by the connector is validated against the OpenAPI specification before Specmatic returns a contract-compliant response.

This significantly reduces mock maintenance while automatically detecting contract drift during integration testing.

## Migration Status

| Batch | Files | Status |
|---|---|---|
| **Batch 1** — Base Issuing, Risk & Fee streams | `test_application_fees.py` | ✅ Migrated |
| | `test_authorizations.py` | ✅ Migrated |
| | `test_cards.py` | ✅ Migrated |
| | `test_early_fraud_warnings.py` | ✅ Migrated |
| | `test_events.py` | ✅ Migrated |
| **Batch 2** — Standard Payment & Balance streams | `test_payment_methods.py` | ✅ Migrated |
| | `test_payout_balance_transactions.py` | ✅ Migrated |
| | `test_reviews.py` | ✅ Migrated |
| | `test_setup_attempts.py` | ✅ Migrated |
| | `test_transactions.py` | ✅ Migrated |
| **POC** | `test_accounts.py` | ✅ Migrated (original POC) |
| **Batch 3** — 100% Specmatic Mock Usage Coverage | `test_charges_specmatic.py` | ✅ Added |
| | `test_customers_specmatic.py` | ✅ Added |
| | `test_invoices_specmatic.py` | ✅ Added |
| | `test_payment_intents_specmatic.py` | ✅ Added |
| | `test_prices_specmatic.py` | ✅ Added |
| | `test_products_specmatic.py` | ✅ Added |
| | `test_refunds_specmatic.py` | ✅ Added |

** All migrated tests pass. Batch 3 achieves 100% Specmatic Mock Usage Report coverage for all 8 endpoints in `stripe-official.json`.**

---

## Key Migration Patterns

### 1. Zero-Hardcoding Specmatic Contract Test (Default)
Tests dynamically configure the connector `url_base` to point to the local Specmatic mock server and validate record reads without hardcoding JSON response payloads:

```python
@freezegun.freeze_time(_NOW_IMPORT.isoformat())
class ChargesSpecmaticFullRefreshTest(SpecmaticIntegrationTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Dynamically route connector HTTP requests to the Specmatic mock server
        _CONFIG["url_base"] = cls.config["url_base"]

    def test_specmatic_contract_read(self) -> None:
        """Zero-Hardcoding contract test against Specmatic OpenAPI mock server."""
        now, start_date = get_dates()
        self.source = get_source(_CONFIG, _NO_STATE)
        output = self._read(_config(now).with_start_date(start_date))
        self.assert_contract_read_success(output)
```

### 2. Contract Success Assertion (`assert_contract_read_success`)
Verifies that stream reads execute cleanly against the Specmatic mock server with zero contract schema or execution errors:

```python
self.assert_contract_read_success(actual_messages)
```

---

## Setup & Files

| File | Description |
|---|---|
| `specs/stripe-official.json` | Official Stripe OpenAPI spec used by the Specmatic mock server |
| `specmatic.yaml` | Specmatic configuration referencing `stripe-official.json` for MOCK mode |
| `docker-compose.yml` | Container orchestrator config to run the Specmatic mock server in a clean, unified sandbox |

| Test Infrastructure | Location |
|---|---|
| `SpecmaticIntegrationTestCase` | `unit_tests/specmatic/base_test.py` |
| Specmatic server manager | `unit_tests/specmatic/server.py` |
| Migration validation runner | `unit_tests/run_validation.py` |

---

## How to Run Integration Tests Locally

### Prerequisites

```bash
npm install -g specmatic@2.50.1
```

### Run a single migrated test file

**Windows (PowerShell) — from `unit_tests/` directory:**
```powershell
cd airbyte-integrations/connectors/source-stripe/unit_tests
.\.venv\Scripts\python.exe -m pytest -v integration/test_events.py
```

**macOS / Linux — from `unit_tests/` directory:**
```bash
cd airbyte-integrations/connectors/source-stripe/unit_tests
./.venv/bin/python -m pytest -v integration/test_events.py
```

### Run ONLY Specmatic integration tests (100% Mock Usage Coverage)

**Windows (PowerShell) — Dynamic One-Liner (from repository root):**
```powershell
$s = (Get-ChildItem airbyte-integrations/connectors/source-stripe/unit_tests/integration/test_*_specmatic.py).FullName; .\airbyte-integrations\connectors\source-stripe\unit_tests\.venv\Scripts\pytest.exe airbyte-integrations/connectors/source-stripe/unit_tests/integration/test_accounts.py $s
```

**Windows (PowerShell) — Explicit File List:**
```powershell
.\airbyte-integrations\connectors\source-stripe\unit_tests\.venv\Scripts\pytest.exe `
  airbyte-integrations/connectors/source-stripe/unit_tests/integration/test_accounts.py `
  airbyte-integrations/connectors/source-stripe/unit_tests/integration/test_charges_specmatic.py `
  airbyte-integrations/connectors/source-stripe/unit_tests/integration/test_customers_specmatic.py `
  airbyte-integrations/connectors/source-stripe/unit_tests/integration/test_invoices_specmatic.py `
  airbyte-integrations/connectors/source-stripe/unit_tests/integration/test_payment_intents_specmatic.py `
  airbyte-integrations/connectors/source-stripe/unit_tests/integration/test_prices_specmatic.py `
  airbyte-integrations/connectors/source-stripe/unit_tests/integration/test_products_specmatic.py `
  airbyte-integrations/connectors/source-stripe/unit_tests/integration/test_refunds_specmatic.py
```

**macOS / Linux — from repository root:**
```bash
cd airbyte-integrations/connectors/source-stripe/unit_tests
./.venv/bin/python -m pytest -v integration/test_accounts.py integration/*_specmatic.py
```

### Run all migrated Batch 1 + Batch 2 tests

**Windows (PowerShell):**
```powershell
cd airbyte-integrations/connectors/source-stripe/unit_tests
.\.venv\Scripts\python.exe -m pytest -v `
  integration/test_accounts.py `
  integration/test_application_fees.py `
  integration/test_authorizations.py `
  integration/test_cards.py `
  integration/test_early_fraud_warnings.py `
  integration/test_events.py `
  integration/test_payment_methods.py `
  integration/test_payout_balance_transactions.py `
  integration/test_reviews.py `
  integration/test_setup_attempts.py `
  integration/test_transactions.py
```

**macOS / Linux:**
```bash
cd airbyte-integrations/connectors/source-stripe/unit_tests
./.venv/bin/python -m pytest -v \
  integration/test_accounts.py \
  integration/test_application_fees.py \
  integration/test_authorizations.py \
  integration/test_cards.py \
  integration/test_early_fraud_warnings.py \
  integration/test_events.py \
  integration/test_payment_methods.py \
  integration/test_payout_balance_transactions.py \
  integration/test_reviews.py \
  integration/test_setup_attempts.py \
  integration/test_transactions.py
```

---

## How to Run Contract Validation Locally

### 1. Run against the Official Stripe Specification

1. Start the Specmatic mock server from the repo root:

   **Using Specmatic CLI (Direct):**
   ```bash
   specmatic mock --port 9000
   ```

   **Using Docker Compose:**
   ```bash
   docker compose -f specmatic_test/docker-compose.yml up specmatic-mock
   ```
2. Run the validation runner:
   - **macOS / Linux:**
     ```bash
     docker run --rm \
       --add-host=host.docker.internal:host-gateway \
       -v "$(pwd):/workspace" \
       python:3.11-slim \
       sh -c "pip install pytest freezegun pytest-mock requests-mock mock airbyte-cdk==6.61.6 requests pyyaml jsonschema && python /workspace/airbyte-integrations/connectors/source-stripe/unit_tests/run_validation.py --spec-path /workspace/specmatic_test/specs/stripe-official.json --report-output /workspace/specmatic_test/official_report.md --host host.docker.internal"
     ```
   - **Windows (PowerShell):**
     ```powershell
     docker run --rm `
       --add-host=host.docker.internal:host-gateway `
       -v "${PWD}:/workspace" `
       python:3.11-slim `
       sh -c "pip install pytest freezegun pytest-mock requests-mock mock airbyte-cdk==6.61.6 requests pyyaml jsonschema && python /workspace/airbyte-integrations/connectors/source-stripe/unit_tests/run_validation.py --spec-path /workspace/specmatic_test/specs/stripe-official.json --host host.docker.internal"
     ```
3. Inspect the native HTML and CTRF reports generated in `build/reports/specmatic/`.

### 2. Validate Specification and Examples Locally

To validate that inline or external examples and the API specification conform to OpenAPI schemas, run Specmatic's built-in validation command:

```bash
specmatic examples validate --lenient --spec-file specmatic_test/specs/stripe-official.json
```

> [!NOTE]
> The `--lenient` flag is required because the official Stripe specification contains duplicate query parameter entries which otherwise cause strict parser validation to fail.
