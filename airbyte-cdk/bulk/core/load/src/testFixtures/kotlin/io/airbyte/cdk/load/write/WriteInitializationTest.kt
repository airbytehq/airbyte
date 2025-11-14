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
 * Integration test that validates write operation can initialize with a real catalog.
 *
 * This test uses REAL catalog loading (not MockDestinationCatalog) to catch missing beans
 * that only surface when TableCatalog is created from actual catalog JSON:
 * - RawTableNameGenerator
 * - FinalTableNameGenerator
 * - ColumnNameGenerator
 * - ColumnNameMapper
 * - TableCatalog factory dependencies
 *
 * Extend this in your connector to validate write operation initialization:
 * ```
 * class MySQLWriteInitTest : WriteInitializationTest<MySQLSpecification>(
 *     configContents = Path.of("secrets/config.json").toFile().readText(),
 *     configSpecClass = MySQLSpecification::class.java,
 * )
 * ```
 *
 * This test complements ConnectorWiringSuite:
 * - ConnectorWiringSuite: Fast component test with mock catalog
 * - WriteInitializationTest: Integration test with real catalog loading
 */
abstract class WriteInitializationTest<T : ConfigurationSpecification>(
    val configContents: String,
    val configSpecClass: Class<T>,
    additionalMicronautEnvs: List<String> = emptyList(),
) : IntegrationTest(
    additionalMicronautEnvs = additionalMicronautEnvs,
    dataDumper = FakeDataDumper,
    destinationCleaner = NoopDestinationCleaner,
    recordMangler = NoopExpectedRecordMapper,
) {

    @Inject
    lateinit var writer: DestinationWriter

    /**
     * Test: Writer can be instantiated with real catalog.
     *
     * This validates that all beans required for write operation can be created:
     * - DestinationCatalog (from catalog JSON)
     * - TableCatalog (from DestinationCatalog + name generators)
     * - DestinationWriter (with TableCatalog dependency)
     *
     * If this test fails with DI errors, it means:
     * - Missing @Singleton on a required bean (RawTableNameGenerator, ColumnNameMapper, etc.)
     * - Missing bean definition in BeanFactory
     * - Circular dependency in bean graph
     *
     * This is the same DI initialization that happens in Docker runtime,
     * so catching errors here prevents Docker runtime crashes.
     */
    @Test
    fun `writer can be instantiated with real catalog`() {
        // Create minimal catalog for testing (with all required fields)
        val catalog = io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog()
            .withStreams(
                listOf(
                    io.airbyte.protocol.models.v0.ConfiguredAirbyteStream()
                        .withStream(
                            io.airbyte.protocol.models.v0.AirbyteStream()
                                .withName("write_init_test")
                                .withNamespace("test")
                                .withJsonSchema(
                                    com.fasterxml.jackson.databind.node.JsonNodeFactory.instance
                                        .objectNode()
                                        .put("type", "object")
                                        .set(
                                            "properties",
                                            com.fasterxml.jackson.databind.node.JsonNodeFactory.instance
                                                .objectNode()
                                                .set("id",
                                                    com.fasterxml.jackson.databind.node.JsonNodeFactory.instance
                                                        .objectNode()
                                                        .put("type", "integer")
                                                )
                                        )
                                )
                        )
                        .withSyncMode(io.airbyte.protocol.models.v0.SyncMode.FULL_REFRESH)
                        .withDestinationSyncMode(io.airbyte.protocol.models.v0.DestinationSyncMode.APPEND)
                        .withGenerationId(0L)
                        .withMinimumGenerationId(0L)
                        .withSyncId(42L)
                )
            )

        val process = destinationProcessFactory.createDestinationProcess(
            command = "write",
            configContents = configContents,
            catalog = catalog,
        )

        // Just start the process - DI will fail if beans are missing
        // We don't need to actually send records, just validate initialization
        kotlinx.coroutines.runBlocking {
            try {
                process.run()
                // Process should start without DI errors
                // It will fail with "no input" but that's expected
            } catch (e: Exception) {
                // Check if it's a DI error (blocker) vs expected error (no input)
                val message = e.message ?: ""
                val cause = e.cause?.message ?: ""

                if (message.contains("BeanInstantiationException") ||
                    message.contains("Failed to inject") ||
                    cause.contains("BeanInstantiationException") ||
                    cause.contains("Failed to inject")) {
                    throw AssertionError(
                        "Write operation failed to initialize due to DI error. " +
                            "This means required beans are missing. " +
                            "Check for: RawTableNameGenerator, FinalTableNameGenerator, " +
                            "ColumnNameGenerator, ColumnNameMapper, Writer. " +
                            "Original error: $message",
                        e
                    )
                }
                // Other errors (like "no input") are OK for this test
            }
        }
    }
}

