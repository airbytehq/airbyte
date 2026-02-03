/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.cdk.load.test.util.FakeConfigurationUpdater
import io.airbyte.cdk.load.test.util.SchemaDumper
import io.airbyte.cdk.load.test.util.destination_process.DestinationProcessFactory
import io.airbyte.cdk.load.write.RegressionTestFixtures.Companion.FUNKY_CHARS_IDENTIFIER
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.TestInfo

/**
 * These tests verify that the connector does not change behavior between versions. The "schema
 * regression" tests watch for changes in table schemas (column names+types, etc.). The "table
 * identifier" tests watch for changes in the actual table names (i.e. schema name, table name,
 * etc.). These tests follow the same pattern as the "component tests"; you must manually override
 * each test case and annotate it with `@Test` to opt into the test.
 *
 * The schema regression tests operate automatically, in that they will dump the table schemas to
 * the `src/test-integration/resources/golden_files/...` path.
 *
 * If you're migrating a connector to the bulk CDK, you can run the regression tests against the
 * previous version of the connector, to populate its previous behavior. Simply override the
 * [destinationProcessFactoryOverride] parameter:
 * ```kotlin
 * destinationProcessFactoryOverride = DockerizedDestinationFactory("airbyte/destination-foo", "previous_version")
 * ```
 * Just remember to revert this change before releasing your connector. The tests will always fail
 * if this value is set, to prevent you from forgetting to unset it.
 *
 * The table identifier tests require developers to manually populate the
 * [tableIdentifierRegressionTestExpectedTableNames] field. These tests are also quite finnicky;
 * that they don't like to be run concurrently. Concurrent test runs (including across multiple PRs)
 * may cause spurious successes _and_ failures.
 */
abstract class RegressionTestSuite(
    val configContents: String,
    val configSpecClass: Class<out ConfigurationSpecification>,
    val configUpdater: ConfigurationUpdater = FakeConfigurationUpdater,
    val schemaDumperProvider: ((ConfigurationSpecification) -> SchemaDumper)? = null,
    val opsClientProvider: ((ConfigurationSpecification) -> TableOperationsClient)? = null,
    val destinationProcessFactoryOverride: DestinationProcessFactory? = null,
    /**
     * If you provide a nonnull [opsClientProvider], you MUST also provide a list of expected
     * [TableName]s. See [RegressionTestFixtures.tableIdentifierRegressionInputStreamDescriptors]
     * for the list of input stream descriptors.
     */
    val tableIdentifierRegressionTestExpectedTableNames: List<TableName> = emptyList(),
) {
    val destinationProcessFactory =
        destinationProcessFactoryOverride ?: DestinationProcessFactory.get(emptyList())

    val goldenFileBasePath = "golden_files/${this::class.simpleName}"
    private lateinit var regressionTestFixtures: RegressionTestFixtures

    @BeforeEach
    fun setup(testInfo: TestInfo) {
        val updatedConfig: String = configUpdater.update(configContents)
        val parsedConfig: ConfigurationSpecification =
            ValidatedJsonUtils.parseOne(configSpecClass, updatedConfig)
        regressionTestFixtures =
            RegressionTestFixtures(
                schemaDumperProvider,
                opsClientProvider,
                destinationProcessFactory,
                updatedConfig = updatedConfig,
                parsedConfig,
                goldenFileBasePath = goldenFileBasePath,
                testPrettyName = "${testInfo.testClass.get().simpleName}.${testInfo.displayName}",
                tableIdentifierRegressionTestExpectedTableNames,
            )
    }

    @AfterEach
    fun safetyFail() {
        assertNull(
            destinationProcessFactoryOverride,
            "Remember to unset the destinationProcessFactoryOverride!",
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

    /**
     * This test does _not_ randomize the table identifier, to allow for more stringent assertions
     * against the table names. As a result, it needs to explicitly drop the table(s) before
     * executing the test. This may cause transient failures if there are multiple concurrent
     * executions.
     *
     * Subclasses MUST annotate this test case with `@ResourceLock("tableIdentifierRegressionTest")`
     * to prevent race conditions.
     */
    open fun testTableIdentifierRegressionAppend() {
        regressionTestFixtures.baseTableIdentifierRegressionTest(Append)
    }

    /**
     * See [testTableIdentifierRegressionAppend] for information.
     *
     * Subclasses MUST annotate this test case with `@ResourceLock("tableIdentifierRegressionTest")`
     * to prevent race conditions.
     */
    open fun testTableIdentifierRegressionDedup() {
        regressionTestFixtures.baseTableIdentifierRegressionTest(
            Dedupe(primaryKey = listOf(listOf("blah")), cursor = emptyList())
        )
    }
}
