/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.file.object_storage.MSSQLCSVFormattingWriter
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.integrations.destination.mssql.v2.config.AzureBlobStorageClientCreator
import io.airbyte.integrations.destination.mssql.v2.config.BulkLoadConfiguration
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLConfiguration
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLDataSourceFactory
import jakarta.inject.Singleton
import java.io.ByteArrayOutputStream
import java.sql.Connection
import java.util.UUID
import javax.sql.DataSource
import kotlinx.coroutines.runBlocking

@Singleton
class MSSQLChecker(private val dataSourceFactory: MSSQLDataSourceFactory) :
    DestinationChecker<MSSQLConfiguration> {

    companion object {
        private const val TEST_CSV_FILENAME = "check_test_data.csv"
        private const val TEST_ID_VALUE = 1
        private const val COLUMN_NAME = "id"
    }

    private val testStream =
        DestinationStream(
            descriptor =
                DestinationStream.Descriptor(
                    namespace = null,
                    name = "check_test_${UUID.randomUUID()}",
                ),
            importType = Append,
            schema =
                ObjectType(linkedMapOf(COLUMN_NAME to FieldType(IntegerType, nullable = true))),
            generationId = 0L,
            minimumGenerationId = 0L,
            syncId = 0L,
        )

    override fun check(config: MSSQLConfiguration) {
        val dataSource: DataSource = dataSourceFactory.getDataSource(config)
        val sqlBuilder = MSSQLQueryBuilder(config.schema, testStream)

        dataSource.connection.use { connection ->
            try {
                // Create test table
                sqlBuilder.createTableIfNotExists(connection)

                // Perform bulk load test if configured
                if (
                    config.mssqlLoadTypeConfiguration.loadTypeConfiguration is BulkLoadConfiguration
                ) {
                    val bulkLoadConfig = config.mssqlLoadTypeConfiguration.loadTypeConfiguration
                    val azureBlobClient =
                        AzureBlobStorageClientCreator.createAzureBlobClient(
                            bulkLoadConfiguration = bulkLoadConfig
                        )

                    val mssqlFormatFileCreator =
                        MSSQLFormatFileCreator(
                            dataSource,
                            stream = testStream,
                            azureBlobClient = azureBlobClient
                        )

                    val mssqlBulkLoadHandler =
                        MSSQLBulkLoadHandler(
                            dataSource,
                            config.schema,
                            testStream.descriptor.name,
                            bulkLoadConfig.bulkLoadDataSource,
                            sqlBuilder
                        )

                    // Create and upload test CSV file
                    val csvData = createTestCsvData(stream = testStream)
                    val csvFilePath = "${testStream.descriptor.name}/$TEST_CSV_FILENAME"

                    runBlocking {
                        // Upload the CSV file to Azure Blob Storage
                        val csvBlob = azureBlobClient.put(csvFilePath, csvData)

                        // Create and upload format file
                        val formatFileBlob =
                            mssqlFormatFileCreator.createAndUploadFormatFile(config.schema)

                        try {
                            // Execute bulk load operation
                            mssqlBulkLoadHandler.bulkLoadForAppendOverwrite(
                                csvBlob.key,
                                formatFileBlob.key
                            )

                            // Verify data was loaded by querying the table
                            verifyDataLoaded(connection, config.schema, testStream.descriptor.name)
                        } finally {
                            // Clean up by deleting the files
                            azureBlobClient.delete(formatFileBlob)
                            azureBlobClient.delete(csvBlob)
                        }
                    }
                }
            } finally {
                // Drop the test table
                sqlBuilder.dropTable(connection)
            }
        }
    }

    /** Creates a CSV file with headers matching the required table structure and one test record */
    private fun createTestCsvData(stream: DestinationStream): ByteArray {
        return ByteArrayOutputStream().use { outputStream ->
            MSSQLCSVFormattingWriter(stream, outputStream, true).use { csvWriter ->
                val destinationRecord =
                    DestinationRecordAirbyteValue(
                        stream.descriptor,
                        ObjectValue(linkedMapOf(COLUMN_NAME to IntegerValue(1))),
                        0L,
                        null,
                    )
                csvWriter.accept(destinationRecord)
                csvWriter.flush()
            }
            // Return the generated CSV data
            outputStream.toByteArray()
        }
    }

    /**
     * Verifies that the test data was successfully loaded into the table Uses quoted identifiers
     * for schema and table names to handle special characters properly
     */
    private fun verifyDataLoaded(connection: Connection, schema: String, tableName: String) {
        val query =
            "SELECT COUNT(*) FROM [${schema}].[${tableName}] WHERE [$COLUMN_NAME] = $TEST_ID_VALUE"
        connection.createStatement().use { statement ->
            statement.executeQuery(query).use { resultSet ->
                if (resultSet.next()) {
                    val count = resultSet.getInt(1)
                    if (count != 1) {
                        throw RuntimeException(
                            "Bulk load verification failed: Expected 1 record but found $count"
                        )
                    }
                } else {
                    throw RuntimeException("Bulk load verification failed: No results returned")
                }
            }
        }
    }
}
