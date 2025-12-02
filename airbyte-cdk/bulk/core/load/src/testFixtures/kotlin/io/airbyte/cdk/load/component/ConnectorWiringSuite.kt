/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.write.DestinationWriter
import java.util.UUID
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.*

/**
 * Validates basic Micronaut DI wiring and write path functionality.
 *
 * Tests:
 * 1. all beans are injectable - Catches missing @Singleton, circular dependencies, missing beans
 * 2. writer setup completes - Validates namespace creation and status gathering
 * 3. can create append stream loader - Validates StreamLoader instantiation
 * 4. stream loader start creates table - Validates table creation
 * 5. can write one record - Full write path validation (most important)
 *
 * Setup:
 * 1. Add testFixtures dependency to build.gradle
 * 2. Create application-component.yml with airbyte.connector.operation="write"
 * 3. Provide @Primary ConfiguredAirbyteCatalog bean (use DefaultComponentTestCatalog.make())
 * 4. Start database in @BeforeAll (testcontainer or real instance)
 * 5. If Writer requires catalog streams: inject DestinationCatalog and override createTestStream()
 *
 * Troubleshooting:
 * - DI errors = test working correctly, add missing beans
 * - "Property doesn't exist" = missing application-component.yml
 * - "Catalog must have at least one stream" = missing ConfiguredAirbyteCatalog bean
 * - NullPointerException in createStreamLoader = override createTestStream()
 */
interface ConnectorWiringSuite {

    // Required: Provided by connector test via Micronaut injection
    val writer: DestinationWriter
    val client: TableOperationsClient
    val aggregateFactory: AggregateFactory

    // Optional: Override to provide custom test namespace (defaults to "test")
    val testNamespace: String
        get() = "test"

    /**
     * Test: All core beans are injectable without DI errors.
     *
     * Validates that Micronaut can create all required beans:
     * - DestinationWriter
     * - TableOperationsClient
     * - AggregateFactory
     *
     * This catches missing @Singleton annotations, circular dependencies, and missing bean
     * definitions.
     */
    fun `all beans are injectable`() {
        assertNotNull(writer, "DestinationWriter should be injectable")
        assertNotNull(client, "TableOperationsClient should be injectable")
        assertNotNull(aggregateFactory, "AggregateFactory should be injectable")
    }

    /**
     * Test: Writer.setup() executes without errors.
     *
     * Validates:
     * - Namespace creation works
     * - Initial status gathering works
     * - No crashes during setup phase
     */
    fun `writer setup completes`() = runBlocking {
        // Should not throw
        writer.setup()
    }

    /**
     * Test: Writer can create StreamLoader for append mode.
     *
     * Validates:
     * - Writer.createStreamLoader() returns non-null
     * - StreamLoader instantiation doesn't crash
     * - Append mode is supported
     */
    fun `can create append stream loader`() = runBlocking {
        writer.setup()
        val stream = createTestStream(importType = Append)
        val loader = writer.createStreamLoader(stream)
        assertNotNull(loader, "StreamLoader should be created for append mode")
    }

    /**
     * Test: StreamLoader.start() creates tables.
     *
     * Validates:
     * - StreamLoader.start() runs without error
     * - Table is created in database
     * - Table can be queried
     */
    fun `stream loader start creates table`() = runBlocking {
        writer.setup()
        val stream = createTestStream()
        val tableName = TableName(testNamespace, stream.mappedDescriptor.name)

        try {
            val loader = writer.createStreamLoader(stream)

            // Start should create table
            loader.start()

            // Verify table exists
            assertTrue(
                client.tableExists(tableName),
                "Table ${tableName} should exist after StreamLoader.start()"
            )
        } finally {
            // Cleanup
            client.dropTable(tableName)
        }
    }

    /**
     * Test: Write one record using StreamLoader (validates full write path).
     *
     * This is the most important test - validates the complete write path:
     * - Sets up writer (namespace creation, initial status gathering)
     * - Creates StreamLoader (which creates table)
     * - Writes one record through aggregate/buffer
     * - Verifies data appears in database
     *
     * If this test passes, your write path works end-to-end!
     */
    fun `can write one record`() = runBlocking {
        writer.setup()
        val stream = createTestStream()
        val tableName = TableName(testNamespace, stream.mappedDescriptor.name)

        try {
            // 1. Create namespace
            client.createNamespace(testNamespace)

            // 2. Create and start StreamLoader
            val loader = writer.createStreamLoader(stream)
            loader.start()

            // 3. Create aggregate for this stream
            val key = createStoreKey(stream)
            val aggregate = aggregateFactory.create(key)

            // 4. Write one record
            val record = createTestRecord()
            aggregate.accept(record)
            aggregate.flush()

            // 5. Verify data in database
            val count = client.countTable(tableName)
            assertEquals(1L, count, "Should have exactly 1 record after write. Got $count records.")

            // 6. Close loader
            loader.close(hadNonzeroRecords = true, streamFailure = null)
        } finally {
            // Cleanup
            client.dropTable(tableName)
        }
    }

    // ========== Helper Methods ==========

    /**
     * Creates a minimal test stream for validation. Override this if you need custom stream
     * configuration.
     */
    fun createTestStream(
        namespace: String = "test",
        name: String = "test_stream_${UUID.randomUUID()}",
        importType: io.airbyte.cdk.load.command.ImportType = Append
    ): DestinationStream {
        return DestinationStream(
            unmappedNamespace = namespace,
            unmappedName = name,
            importType = importType,
            schema =
                ObjectType(
                    properties =
                        linkedMapOf(
                            "id" to FieldType(IntegerType, nullable = false),
                            "name" to FieldType(StringType, nullable = true)
                        )
                ),
            generationId = 0,
            minimumGenerationId = 0,
            syncId = 42,
            namespaceMapper = NamespaceMapper(), // Default identity mapper
            tableSchema =
                StreamTableSchema(
                    columnSchema =
                        ColumnSchema(
                            inputSchema = mapOf(),
                            inputToFinalColumnNames = mapOf(),
                            finalSchema = mapOf(),
                        ),
                    importType = Append,
                    tableNames = TableNames(finalTableName = TableName("namespace", "test")),
                ),
        )
    }

    /**
     * Creates a StoreKey for the given stream. Used to retrieve aggregate from factory.
     *
     * Note: StoreKey is a typealias for DestinationStream.Descriptor
     */
    fun createStoreKey(stream: DestinationStream): StoreKey {
        // StoreKey = DestinationStream.Descriptor
        return stream.mappedDescriptor
    }

    /**
     * Creates a simple column name mapping for test stream. Maps column names to themselves
     * (identity mapping). Override if your database requires name transformation.
     */
    fun createSimpleColumnMapping(): io.airbyte.cdk.load.table.ColumnNameMapping {
        return io.airbyte.cdk.load.table.ColumnNameMapping(mapOf("id" to "id", "name" to "name"))
    }

    /**
     * Creates a test record with all required Airbyte metadata columns. Override this if you need
     * custom record structure.
     */
    fun createTestRecord(): RecordDTO {
        return RecordDTO(
            fields =
                mapOf(
                    // User columns
                    "id" to IntegerValue(1),
                    "name" to StringValue("Alice"),
                    // Airbyte metadata columns (required)
                    "_airbyte_raw_id" to StringValue(UUID.randomUUID().toString()),
                    "_airbyte_extracted_at" to TimestampWithTimezoneValue("2024-01-01T00:00:00Z"),
                    "_airbyte_meta" to ObjectValue(linkedMapOf()),
                    "_airbyte_generation_id" to IntegerValue(0)
                ),
            partitionKey = PartitionKey(""), // Empty partition for non-partitioned streams
            sizeBytes = 100,
            emittedAtMs = System.currentTimeMillis()
        )
    }
}
