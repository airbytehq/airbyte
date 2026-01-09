/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.cdk.load.test.util.FakeConfigurationUpdater
import io.airbyte.cdk.load.test.util.SchemaDumper
import io.airbyte.cdk.load.test.util.destination_process.DestinationProcessFactory
import io.airbyte.cdk.load.write.RegressionTestFixtures.Companion.FUNKY_CHARS_IDENTIFIER
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.TestInfo

abstract class RegressionTestSuite(
    val configContents: String,
    val configSpecClass: Class<out ConfigurationSpecification>,
    val configUpdater: ConfigurationUpdater = FakeConfigurationUpdater,
    val schemaDumper: SchemaDumper? = null,
    val destinationProcessFactory: DestinationProcessFactory,
    val dataChannelMedium: DataChannelMedium,
    val dataChannelFormat: DataChannelFormat,
) {
    val goldenFileBasePath = "golden_files/${this::class.simpleName}"
    private lateinit var regressionTestFixtures: RegressionTestFixtures

    @BeforeEach
    fun setup(testInfo: TestInfo) {
        val updatedConfig: String = configUpdater.update(configContents)
        val parsedConfig: ConfigurationSpecification =
            ValidatedJsonUtils.parseOne(configSpecClass, updatedConfig)
        regressionTestFixtures =
            RegressionTestFixtures(
                schemaDumper,
                destinationProcessFactory,
                dataChannelMedium,
                dataChannelFormat,
                updatedConfig = updatedConfig,
                parsedConfig,
                goldenFileBasePath = goldenFileBasePath,
                testPrettyName = "${testInfo.testClass.get().simpleName}.${testInfo.displayName}"
            )
    }

    /** Regression test for table schemas (column names, types, etc.) in append mode. */
    open fun testSchemaRegressionAppend() {
        regressionTestFixtures.baseSchemaRegressionTest("append", Append)
    }

    /**
     * Regression test for table schemas (column names, types, etc.) in dedup mode, using simple
     * identifiers for the PK/cursor.
     */
    open fun testSchemaRegressionSimpleDedup() {
        regressionTestFixtures.baseSchemaRegressionTest(
            "dedup_simple",
            Dedupe(
                primaryKey = listOf(listOf("string")),
                cursor = listOf("number"),
            )
        )
    }

    /**
     * Regression test for table schemas (column names, types, etc.) in dedup mode, using SQL
     * reserved words for the PK/cursor.
     */
    open fun testSchemaRegressionDedupReservedWords() {
        regressionTestFixtures.baseSchemaRegressionTest(
            "dedup_reserved_word",
            Dedupe(
                primaryKey = listOf(listOf("column")),
                cursor = listOf("table"),
            )
        )
    }

    /**
     * Regression test for table schemas (column names, types, etc.) in dedup mode, using an
     * identifier with funky chars for the PK.
     */
    open fun testSchemaRegressionFunkyCharsPk() {
        regressionTestFixtures.baseSchemaRegressionTest(
            "dedup_funky_chars_pk",
            Dedupe(
                primaryKey = listOf(listOf(FUNKY_CHARS_IDENTIFIER)),
                cursor = listOf("string"),
            )
        )
    }

    /**
     * Regression test for table schemas (column names, types, etc.) in dedup mode, using an
     * identifier with funky chars for the PK.
     */
    open fun testSchemaRegressionFunkyCharsCursor() {
        regressionTestFixtures.baseSchemaRegressionTest(
            "dedup_funky_chars_cursor",
            Dedupe(
                primaryKey = listOf(listOf("string")),
                cursor = listOf(FUNKY_CHARS_IDENTIFIER),
            )
        )
    }

    /**
     * Regression test for table schemas (column names, types, etc.) in dedup mode, using colliding
     * identifiers for the PK/cursor.
     */
    open fun testSchemaRegressionDedupCollidingNames() {
        regressionTestFixtures.baseSchemaRegressionTest(
            "dedup_colliding_names",
            Dedupe(
                primaryKey = listOf(listOf("foo!")),
                cursor = listOf("foo$"),
            )
        )
    }
}
