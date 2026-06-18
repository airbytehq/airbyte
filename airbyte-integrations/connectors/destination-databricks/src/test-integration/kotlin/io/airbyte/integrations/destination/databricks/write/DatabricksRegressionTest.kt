/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.write

import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.write.RegressionTestSuite
import io.airbyte.integrations.destination.databricks.spec.DatabricksSpecification
import java.nio.file.Files
import java.nio.file.Path
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.ResourceLock

/**
 * Regression tests for the Databricks destination. Verifies that schema structure and table
 * identifiers remain stable across code changes.
 *
 * Databricks lowercases all object names (tables, schemas) and converts special characters to
 * underscores via [toDatabricksCompatibleName]. Column names preserve casing.
 */
class DatabricksRegressionTest :
    RegressionTestSuite(
        configContents = Files.readString(Path.of(CONFIG_PATH)),
        configSpecClass = DatabricksSpecification::class.java,
        schemaDumperProvider = { DatabricksSchemaDumper(it) },
        opsClientProvider = { DatabricksTestConfigProvider.airbyteClientFrom(it) },
        tableIdentifierRegressionTestExpectedTableNames =
            listOf(
                // basic identifier
                TableName("table_id_regression_test", "table_id_regression_test"),
                // reserved words -- Databricks does not mangle reserved words
                TableName("table", "table"),
                TableName("column", "column"),
                TableName("create", "create"),
                TableName("delete", "delete"),
                // funky chars: all special chars -> underscore, lowercased
                TableName("e________________________________", "e________________________________"),
                // starts with digit: 1foo -> _1foo (lowercased)
                TableName("_1foo", "_1foo"),
                // colliding namespaces: foo!, foo$, foo_ all normalize to foo_
                TableName("foo_", "table_id_regression_test"),
                TableName("foo_", "table_id_regression_test"),
                TableName("foo_", "table_id_regression_test"),
                // colliding names: foo!, foo$, foo_ all normalize to foo_
                TableName("table_id_regression_test", "foo_"),
                TableName("table_id_regression_test", "foo_"),
                TableName("table_id_regression_test", "foo_"),
                // upper/mixed case: lowercased by Databricks convention
                TableName("upper_case", "upper_case"),
                TableName("mixed_case", "mixed_case"),
            ),
    ) {

    @Test
    override fun testSchemaRegressionSimpleDedup() {
        super.testSchemaRegressionSimpleDedup()
    }

    @Test
    override fun testSchemaRegressionDedupReservedWords() {
        super.testSchemaRegressionDedupReservedWords()
    }

    @Test
    override fun testSchemaRegressionFunkyCharsPk() {
        super.testSchemaRegressionFunkyCharsPk()
    }

    @Test
    override fun testSchemaRegressionFunkyCharsCursor() {
        super.testSchemaRegressionFunkyCharsCursor()
    }

    @Test
    override fun testSchemaRegressionDedupCollidingNames() {
        super.testSchemaRegressionDedupCollidingNames()
    }

    @ResourceLock("tableIdentifierRegressionTest")
    @Test
    override fun testTableIdentifierRegressionAppend() {
        super.testTableIdentifierRegressionAppend()
    }
}
