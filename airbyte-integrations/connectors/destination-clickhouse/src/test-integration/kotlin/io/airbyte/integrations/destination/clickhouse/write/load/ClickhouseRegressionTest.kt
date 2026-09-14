/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.write.load

import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.write.RegressionTestSuite
import io.airbyte.integrations.destination.clickhouse.ClickhouseConfigUpdater
import io.airbyte.integrations.destination.clickhouse.ClickhouseContainerHelper
import io.airbyte.integrations.destination.clickhouse.Utils
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseSpecificationOss
import java.nio.file.Files
import java.nio.file.Path
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.ResourceLock

abstract class ClickhouseBaseRegressionTest(configPath: Path) :
    RegressionTestSuite(
        configContents = Files.readString(configPath),
        configSpecClass = ClickhouseSpecificationOss::class.java,
        configUpdater = ClickhouseConfigUpdater(),
        schemaDumperProvider = { ClickhouseSchemaDumper(it) },
        opsClientProvider = { Utils.getClickhouseAirbyteClient(it) },
        tableIdentifierRegressionTestExpectedTableNames =
            listOf(
                TableName("table_id_regression_test", "table_id_regression_test"),
                TableName("table", "table"),
                TableName("column", "column"),
                TableName("create", "create"),
                TableName("delete", "delete"),
                TableName("e________________________________", "e________________________________"),
                TableName("_1foo", "_1foo"),
                TableName("foo_", "table_id_regression_test"),
                // yes, these are the same table name. Clearly there's a bug in our collision
                // resolution logic.
                TableName("foo_", "table_id_regression_test_304"),
                TableName("foo_", "table_id_regression_test_304"),
                TableName("table_id_regression_test", "foo_"),
                TableName("table_id_regression_test", "foo__1b6"),
                TableName("table_id_regression_test", "foo__e5f"),
                TableName("UPPER_CASE", "UPPER_CASE"),
                TableName("Mixed_Case", "Mixed_Case"),
            ),
    ) {
    @Test
    override fun testSchemaRegressionAppend() {
        super.testSchemaRegressionAppend()
    }

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

    @ResourceLock("tableIdentifierRegressionTest")
    @Test
    override fun testTableIdentifierRegressionDedup() {
        super.testTableIdentifierRegressionDedup()
    }

    companion object {
        @JvmStatic
        @BeforeAll
        fun beforeAll() {
            ClickhouseContainerHelper.start()
        }
    }
}

class ClickhouseJsonRegressionTest :
    ClickhouseBaseRegressionTest(
        Utils.getConfigPath("valid_connection.json"),
    )

class ClickhouseNonJsonRegressionTest :
    ClickhouseBaseRegressionTest(
        Utils.getConfigPath("valid_connection_no_json.json"),
    )
