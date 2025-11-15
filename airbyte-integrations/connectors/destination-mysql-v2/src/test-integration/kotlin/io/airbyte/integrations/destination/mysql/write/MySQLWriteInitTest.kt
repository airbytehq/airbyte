package io.airbyte.integrations.destination.mysql.write

import io.airbyte.cdk.load.write.WriteInitializationTest
import io.airbyte.integrations.destination.mysql.spec.MySQLSpecification
import java.nio.file.Path

/**
 * Validates write operation can initialize with real catalog.
 * Catches missing beans that ConnectorWiringSuite (with mock catalog) doesn't test.
 *
 * This test spawns a real write process (same as Docker) and validates:
 * - TableCatalog can be instantiated (requires name generators from Phase 6)
 * - Write operation can be created (requires WriteOperationV2 from Phase 7.1)
 * - All write infrastructure beans exist (DatabaseInitialStatusGatherer, ColumnNameMapper, etc.)
 *
 * Does NOT validate data writing - that's Phase 8 (ConnectorWiringSuite)
 */
class MySQLWriteInitTest : WriteInitializationTest<MySQLSpecification>(
    configContents = Path.of("secrets/test-instance.json").toFile().readText(),
    configSpecClass = MySQLSpecification::class.java,
)
