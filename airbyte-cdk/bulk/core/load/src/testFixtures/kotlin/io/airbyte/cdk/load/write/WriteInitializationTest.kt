/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.test.util.FakeDataDumper
import io.airbyte.cdk.load.test.util.IntegrationTest
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Test

/**
 * Validates write operation can initialize with real catalog loading.
 *
 * Tests that all beans required for catalog processing exist:
 * - RawTableNameGenerator, FinalTableNameGenerator, ColumnNameGenerator
 * - ColumnNameMapper, TableCatalog factory dependencies
 *
 * Complements ConnectorWiringSuite:
 * - ConnectorWiringSuite: Fast component test, validates write path
 * - WriteInitializationTest: Integration test, validates catalog loading
 *
 * Usage: class MyWriteInitTest : WriteInitializationTest<MySpecification>(
 * ```
 *       configContents = File("secrets/config.json").readText(),
 *       configSpecClass = MySpecification::class.java,
 * ```
 * )
 *
 * Troubleshooting:
 * - DI errors = missing bean (add to BeanFactory or mark @Singleton)
 * - File not found = create secrets/config.json with valid credentials
 */
abstract class WriteInitializationTest<T : ConfigurationSpecification>(
    val configContents: String,
    val configSpecClass: Class<T>,
    additionalMicronautEnvs: List<String> = emptyList(),
) :
    IntegrationTest(
        additionalMicronautEnvs = additionalMicronautEnvs,
        dataDumper = FakeDataDumper,
        destinationCleaner = NoopDestinationCleaner,
        recordMangler = NoopExpectedRecordMapper,
    ) {

    @Inject lateinit var writer: DestinationWriter

    /**
     * Validates all beans for catalog loading exist.
     *
     * Creates write process with real catalog to ensure:
     * - DestinationCatalog can be created from catalog JSON
     * - TableCatalog factory can create catalog with name generators
     * - DestinationWriter can be instantiated
     *
     * DI errors here = missing beans (same errors that would crash Docker runtime).
     */
    @Test
    fun `writer can be instantiated with real catalog`() {
        // Create minimal catalog for testing (with all required fields)
        val catalog =
            io.airbyte.protocol.models.v0
                .ConfiguredAirbyteCatalog()
                .withStreams(
                    listOf(
                        io.airbyte.protocol.models.v0
                            .ConfiguredAirbyteStream()
                            .withStream(
                                io.airbyte.protocol.models.v0
                                    .AirbyteStream()
                                    .withName("write_init_test")
                                    .withNamespace("test")
                                    .withJsonSchema(
                                        com.fasterxml.jackson.databind.node.JsonNodeFactory.instance
                                            .objectNode()
                                            .put("type", "object")
                                            .set(
                                                "properties",
                                                com.fasterxml.jackson.databind.node.JsonNodeFactory
                                                    .instance
                                                    .objectNode()
                                                    .set(
                                                        "id",
                                                        com.fasterxml.jackson.databind.node
                                                            .JsonNodeFactory
                                                            .instance
                                                            .objectNode()
                                                            .put("type", "integer")
                                                    )
                                            )
                                    )
                            )
                            .withSyncMode(io.airbyte.protocol.models.v0.SyncMode.FULL_REFRESH)
                            .withDestinationSyncMode(
                                io.airbyte.protocol.models.v0.DestinationSyncMode.APPEND
                            )
                            .withGenerationId(0L)
                            .withMinimumGenerationId(0L)
                            .withSyncId(42L)
                    )
                )

        // Just CREATE the process - DI will fail if beans are missing
        // We don't actually RUN it (that would hang waiting for stdin)
        try {
            val process =
                destinationProcessFactory.createDestinationProcess(
                    command = "write",
                    configContents = configContents,
                    catalog = catalog,
                )

            // If we get here, DI succeeded!
            // Process was created without bean instantiation errors
            assertNotNull(
                process,
                "Write process should be created successfully. " +
                    "DI initialization passed - all required beans exist."
            )
        } catch (e: Exception) {
            // Check if it's a DI error (blocker) vs other error
            val message = e.message ?: ""
            val cause = e.cause?.message ?: ""

            if (
                message.contains("BeanInstantiationException") ||
                    message.contains("Failed to inject") ||
                    message.contains("No bean of type") ||
                    cause.contains("BeanInstantiationException") ||
                    cause.contains("Failed to inject") ||
                    cause.contains("No bean of type")
            ) {
                throw AssertionError(
                    "Write operation failed to initialize due to DI error. " +
                        "This means required beans are missing. " +
                        "Check for: RawTableNameGenerator, FinalTableNameGenerator, " +
                        "ColumnNameGenerator, ColumnNameMapper, Writer, " +
                        "AggregatePublishingConfig. " +
                        "Original error: $message",
                    e
                )
            }
            // Re-throw other unexpected errors
            throw e
        }
    }
}
