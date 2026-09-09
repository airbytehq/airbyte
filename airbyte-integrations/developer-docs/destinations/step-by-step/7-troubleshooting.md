# Troubleshooting Reference

**Summary:** Quick reference guide for common errors encountered during connector development. Jump here when you hit a problem, find your error, and get back to coding.

---

## Understanding Test Contexts

**Why this section matters:** Tests pass but Docker fails? This section explains the three different DI contexts your connector runs in.

### The Three DI Contexts

Your connector runs in 3 different dependency injection contexts, each with different catalog loading and bean requirements:

### 1. Component Test Context

**Annotation:** `@MicronautTest(environments = ["component"])`

**What it is:**
- Unit-style tests for connector components
- Fast iteration (< 1 second per test)
- Isolated from real catalog parsing

**Catalog:** MockDestinationCatalog
- CDK provides MockDestinationCatalog bean
- Streams created dynamically by test code
- No JSON catalog parsing
- No TableCatalog auto-instantiation

**Database:** Testcontainers
- Fresh database per test class
- Automatic cleanup
- No manual setup needed

**Tests that run here:**
- TableOperationsSuite (Phases 2-5)
- ConnectorWiringSuite (Phase 8)

**What this catches:**
- Missing @Singleton annotations on Writer, AggregateFactory, Client
- Circular dependencies
- Database connection errors
- SQL syntax errors
- Business logic bugs

**What this DOESN'T catch:**
- Missing name generators (MockDestinationCatalog bypasses TableCatalog)
- Missing application-connector.yml (uses test config)
- Bean registration errors for TableCatalog dependencies

### 2. Integration Test Context

**No special annotation** - spawns actual connector process

**What it is:**
- Integration tests that spawn real connector subprocess
- Same execution path as Docker
- Full catalog parsing

**Catalog:** REAL catalog from JSON
- Parses JSON catalog file
- Auto-instantiates TableCatalog
- Requires name generators (Phase 6)
- Full DI graph validation

**Tests that run here:**
- SpecTest (Phase 1)
- CheckIntegrationTest (Phase 5)
- WriteInitializationTest (Phase 7)
- BasicFunctionalityIntegrationTest (Phases 8+)

**What this catches:**
- **Missing name generators** (TableCatalog fails to instantiate)
- **Missing WriteOperationV2** (write operation can't start)
- **Missing DatabaseInitialStatusGatherer bean** (Writer DI fails)
- All DI errors that would occur in Docker

**What this DOESN'T catch:**
- application-connector.yml errors (test uses test config)

### 3. Docker Runtime Context

**How it runs:** `docker run airbyte/destination-{db}:0.1.0 --write`

**What it is:**
- Production execution environment
- Real Airbyte platform invocation
- Full configuration from platform

**Catalog:** REAL catalog from platform
- Provided by Airbyte platform
- Auto-instantiates TableCatalog
- Requires name generators (Phase 6)

**Configuration:** application-connector.yml
- ⚠️ CRITICAL: Must exist in src/main/resources/
- Provides data-channel configuration
- Provides namespace-mapping-config-path
- Missing file = DI errors

**Common failure:** Tests pass, Docker fails
- Why: Tests use test config, Docker uses application-connector.yml
- Fix: Create application-connector.yml (Phase 0, Step 0.8)

### Test Progression Strategy

```
Phase 2-5: TableOperationsSuite (component tests)
  ↓ Validates: Database operations work
  ✓ Fast feedback

Phase 6: Name generators created
  ↓ Enables: TableCatalog instantiation

Phase 7: WriteInitializationTest (integration test)
  ↓ Validates: Write operation can initialize with REAL catalog
  ✓ Catches: Missing name generators, WriteOperationV2, bean registrations

Phase 8: ConnectorWiringSuite (component tests)
  ↓ Validates: Full write path with MOCK catalog
  ✓ Fast iteration on business logic

Phase 8+: BasicFunctionalityIntegrationTest
  ↓ Validates: End-to-end with REAL catalog
  ✓ Full connector functionality
```

**Best practice:** Run BOTH
```bash
# Fast iteration (component tests)
$ ./gradlew :destination-{db}:componentTest

# Full validation (integration tests)
$ ./gradlew :destination-{db}:integrationTest
```

---

## Common DI Errors & Fixes

**Quick troubleshooting guide for the most common Dependency Injection errors**

### Error: "Error instantiating TableCatalog" or "No bean of type [FinalTableNameGenerator]"

**What it means:**
- TableCatalog requires name generator beans
- Only happens with real catalog parsing

**Fix:** Create name generators (Phase 6)

**File:** `config/{DB}NameGenerators.kt`

```kotlin
@Singleton
class {DB}FinalTableNameGenerator(...) : FinalTableNameGenerator { ... }

@Singleton
class {DB}RawTableNameGenerator(...) : RawTableNameGenerator { ... }

@Singleton
class {DB}ColumnNameGenerator : ColumnNameGenerator { ... }
```

**Also register in BeanFactory:**
```kotlin
@Singleton
fun tempTableNameGenerator(...): TempTableNameGenerator { ... }
```

---

### Error: "No bean of type [DatabaseInitialStatusGatherer]"

**What it means:**
- Class exists but bean registration missing

**Fix:** Add bean registration (Phase 7, Step 7.3)

**File:** `{DB}BeanFactory.kt`

```kotlin
@Singleton
fun initialStatusGatherer(
    client: TableOperationsClient,
    tempTableNameGenerator: TempTableNameGenerator,
): DatabaseInitialStatusGatherer<DirectLoadInitialStatus> {
    return {DB}DirectLoadDatabaseInitialStatusGatherer(client, tempTableNameGenerator)
}
```

---

### Error: "A legal sync requires a declared @Singleton of a type that implements LoadStrategy"

**What it means:**
- Missing WriteOperationV2 bean

**Fix:** Create WriteOperationV2 (Phase 7, Step 7.1)

**File:** `cdk/WriteOperationV2.kt`

```kotlin
@Primary
@Singleton
@Requires(property = Operation.PROPERTY, value = "write")
class WriteOperationV2(private val d: DestinationLifecycle) : Operation {
    override fun execute() { d.run() }
}
```

---

### Error: "Failed to inject value for parameter [dataChannelMedium]"

**What it means:**
- Missing application-connector.yml
- **Only happens in Docker, NOT in tests**

**Fix:** Create application-connector.yml (Phase 0, Step 0.8)

**File:** `src/main/resources/application-connector.yml`

```yaml
airbyte:
  destination:
    core:
      data-channel:
        medium: STDIO
        format: JSONL
      mappers:
        namespace-mapping-config-path: ""
```

---

### Error: "lateinit property initialStatuses has not been initialized"

**What it means:**
- ConnectorWiringSuite creates dynamic test streams
- Writer needs defensive handling

**Fix:** Make Writer defensive (Phase 8, Step 8.5)

```kotlin
val initialStatus = if (::initialStatuses.isInitialized) {
    initialStatuses[stream] ?: DirectLoadInitialStatus(null, null)
} else {
    DirectLoadInitialStatus(null, null)
}
```

---

## When to Use This Guide

**Jump here when:**
- Tests pass but Docker fails → Check "Understanding Test Contexts"
- Getting DI errors → Check "Common DI Errors & Fixes"
- Not sure which test to run → Check "Test Progression Strategy"
- Need quick error lookup → Scan error titles

**Return to phase guides when:**
- Building new features
- Following step-by-step implementation
- Need detailed explanations

---

## Additional Resources

- [dataflow-cdk.md](../dataflow-cdk.md) - Architecture overview
- [implementation-reference.md](../implementation-reference.md) - Component reference
- [coding-standards.md](../coding-standards.md) - Best practices
