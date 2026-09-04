/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.write

import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.write.RegressionTestSuite
import io.airbyte.integrations.destination.redshift.config.RedshiftSpecification
import java.nio.file.Files
import java.nio.file.Path
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.ResourceLock

/**
 * Regression tests for the Redshift destination. Verifies that schema structure and table
 * identifiers remain stable across code changes.
 */
class RedshiftRegressionTest :
    RegressionTestSuite(
        configContents = Files.readString(Path.of(CONFIG_PATH)),
        configSpecClass = RedshiftSpecification::class.java,
        schemaDumperProvider = { RedshiftSchemaDumper(it) },
        opsClientProvider = { RedshiftTestConfigProvider.airbyteClientFrom(it) },
        tableIdentifierRegressionTestExpectedTableNames =
            listOf(
                // basic identifier: table_id_regression_test.table_id_regression_test
                TableName("table_id_regression_test", "table_id_regression_test"),
                // reserved words — Redshift does not mangle reserved words in identifiers
                TableName("table", "table"),
                TableName("column", "column"),
                TableName("create", "create"),
                TableName("delete", "delete"),
                // funky chars : é,./<>?'";[]\:{}|`~!@#$%^&*()_+-= \
                // After NFKD normalize + strip combining marks + replace non-alnum with _:
                // é -> e, all special chars -> _
                TableName("e________________________________", "e________________________________"),
                // starts with digit: 1foo -> _1foo
                TableName("_1foo", "_1foo"),
                // colliding namespaces: foo!, foo$, foo_ all normalize to foo_
                TableName("foo_", "table_id_regression_test"),
                TableName("foo_", "table_id_regression_test"),
                TableName("foo_", "table_id_regression_test"),
                // colliding names: foo!, foo$, foo_ all normalize to foo_
                TableName("table_id_regression_test", "foo_"),
                TableName("table_id_regression_test", "foo_"),
                TableName("table_id_regression_test", "foo_"),
                // upper/mixed case: lowercased by Redshift convention
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
