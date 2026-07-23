# Validation: Complete Test Checklist

**Purpose:** Verify your connector has all required test classes before submitting.

---

## Required Test Classes

| Class | Extends | Location | Guide |
|-------|---------|----------|-------|
| `{DB}SpecTest` | `SpecTest` | `test-integration/.../spec/` | 1 |
| `{DB}TestConfigFactory` | Factory | `test-integration/.../component/` | 2 |
| `{DB}TestTableOperationsClient` | `TestTableOperationsClient` | `test-integration/.../component/` | 2 |
| `{DB}TableOperationsTest` | `TableOperationsSuite` | `test-integration/.../component/` | 2 |
| `{DB}CheckTest` | `CheckIntegrationTest` | `test-integration/.../check/` | 2 |
| `{DB}WriteInitTest` | `WriteInitializationTest` | `test-integration/.../write/` | 3 |
| `{DB}WiringTest` | `ConnectorWiringSuite` | `test-integration/.../component/` | 4 |
| `{DB}TableSchemaEvolutionTest` | `TableSchemaEvolutionSuite` | `test-integration/.../component/` | 5 |
| `{DB}BasicFunctionalityTest` | `BasicFunctionalityIntegrationTest` | `test-integration/` | 6 |

**Total: 9 test classes**

---

## Validation Script

Run from your connector directory:

```bash
#!/bin/bash
DB="YourDatabase"  # e.g., "Clickhouse", "Postgres"

REQUIRED_CLASSES=(
  "${DB}SpecTest"
  "${DB}TestConfigFactory"
  "${DB}TestTableOperationsClient"
  "${DB}TableOperationsTest"
  "${DB}CheckTest"
  "${DB}WriteInitTest"
  "${DB}WiringTest"
  "${DB}TableSchemaEvolutionTest"
  "${DB}BasicFunctionalityTest"
)

echo "Checking for required test classes..."
MISSING=0

for class in "${REQUIRED_CLASSES[@]}"; do
  if grep -rq "class $class" src/test-integration/; then
    echo "✅ $class"
  else
    echo "❌ $class - MISSING"
    MISSING=$((MISSING + 1))
  fi
done

echo ""
if [ $MISSING -eq 0 ]; then
  echo "All test classes present!"
else
  echo "Missing $MISSING test class(es)"
  exit 1
fi
```

---

## Expected Test Methods

### TableOperationsSuite (5 tests)

```kotlin
@Test override fun `connect to database`()
@Test override fun `create and drop namespaces`()
@Test override fun `create and drop tables`()
@Test override fun `insert records`()
@Test override fun `count table rows`()
```

### ConnectorWiringSuite (4 tests)

```kotlin
@Test override fun `all beans are injectable`()
@Test override fun `writer setup completes`()
@Test override fun `can create append stream loader`()
@Test override fun `can write one record`()
```

### TableSchemaEvolutionSuite (12 tests)

```kotlin
@Test override fun `discover recognizes all data types`()
@Test override fun `computeSchema handles all data types`()
@Test override fun `noop diff`()
@Test override fun `changeset is correct when adding a column`()
@Test override fun `changeset is correct when dropping a column`()
@Test override fun `changeset is correct when changing a column's type`()
@Test override fun `apply changeset - handle sync mode append`()
@Test override fun `apply changeset - handle changing sync mode from append to dedup`()
@Test override fun `apply changeset - handle changing sync mode from dedup to append`()
@Test override fun `apply changeset - handle sync mode dedup`()
@Test override fun `change from string type to unknown type`()
@Test override fun `change from unknown type to string type`()
```

---

## Run All Tests

```bash
# Component tests (fast, uses Testcontainers)
./gradlew :destination-{db}:componentTest

# Integration tests (requires secrets/config.json)
./gradlew :destination-{db}:integrationTest

# Full validation
./gradlew :destination-{db}:check
```

### Expected Test Counts

| Test Suite | Expected Count |
|------------|----------------|
| componentTest | 21+ tests |
| integrationTest | 3+ tests |

---

## Reference Implementation

All test classes demonstrated in: `destination-clickhouse`

```
destination-clickhouse/src/test-integration/kotlin/io/airbyte/integrations/destination/clickhouse/
├── spec/
│   └── ClickhouseSpecTest.kt
├── check/
│   └── ClickhouseCheckTest.kt
├── write/
│   └── ClickhouseWriteInitTest.kt
└── component/
    ├── ClickhouseTestConfigFactory.kt
    ├── ClickhouseTestTableOperationsClient.kt
    ├── ClickhouseTableOperationsTest.kt
    ├── ClickhouseWiringTest.kt
    └── ClickhouseTableSchemaEvolutionTest.kt
```

---

## Checklist

Before submitting your connector, verify:

- [ ] All 9 test classes exist
- [ ] `componentTest` passes (21+ tests)
- [ ] `integrationTest` passes (3+ tests)
- [ ] No `TODO()` stubs remain in test classes
- [ ] All `@Test override fun` methods are uncommented/enabled
