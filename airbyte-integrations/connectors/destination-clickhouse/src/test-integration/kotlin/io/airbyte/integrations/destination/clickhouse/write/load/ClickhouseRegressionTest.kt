/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.write.load

import io.airbyte.cdk.load.test.util.destination_process.DestinationProcessFactory
import io.airbyte.cdk.load.write.RegressionTestSuite
import io.airbyte.integrations.destination.clickhouse.ClickhouseConfigUpdater
import io.airbyte.integrations.destination.clickhouse.ClickhouseContainerHelper
import io.airbyte.integrations.destination.clickhouse.Utils
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseSpecificationOss
import java.nio.file.Files
import java.nio.file.Path
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test

abstract class ClickhouseBaseRegressionTest(configPath: Path) :
    RegressionTestSuite(
        configContents = Files.readString(configPath),
        configSpecClass = ClickhouseSpecificationOss::class.java,
        configUpdater = ClickhouseConfigUpdater(),
        schemaDumper = ClickhouseSchemaDumper,
        destinationProcessFactory = DestinationProcessFactory.get(emptyList()),
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
