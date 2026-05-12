/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.check

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.integrations.destination.redshift.client.RedshiftAirbyteClient
import io.airbyte.integrations.destination.redshift.config.RedshiftConfiguration
import io.airbyte.integrations.destination.redshift.sql.RedshiftDataType
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.io.ByteArrayOutputStream
import java.io.OutputStreamWriter
import java.nio.charset.StandardCharsets
import java.sql.SQLException
import java.time.OffsetDateTime
import java.util.UUID
import java.util.zip.GZIPOutputStream
import kotlinx.coroutines.runBlocking
import software.amazon.awssdk.services.s3.model.S3Exception

private val log = KotlinLogging.logger {}

internal const val CHECK_COLUMN_NAME = "test_key"
private const val CHECK_COLUMN_VALUE = "check-value"
private const val CHECK_ALTER_COLUMN_NAME = "_airbyte_check_alter"

/**
 * Redshift connection checker that validates the full S3 staging -> COPY -> Redshift pipeline.
 *
 * Each validation step is a separate function for clarity and debuggability:
 * 1. [testRedshiftConnection] -- Redshift JDBC connectivity
 * 2. [testS3WriteAccess] -- S3 write permission (gzip CSV upload)
 * 3. [testCreateTable] -- Redshift DDL (CREATE SCHEMA + CREATE TABLE)
 * 4. [testCopyFromS3] -- Redshift COPY command from S3
 * 5. [testAlterTable] -- ALTER TABLE ADD COLUMN (schema evolution permission)
 * 6. [testDeleteRow] -- delete the test row
 * 7. [testS3Cleanup] -- delete the S3 test object
 * 8. [cleanup] -- drop Redshift table (called by CDK after check)
 */
@Singleton
class RedshiftChecker(
    private val client: RedshiftAirbyteClient,
    private val configuration: RedshiftConfiguration,
) : DestinationChecker {

    private var s3Key: String? = null
    private var tableName: TableName? = null

    override fun check() {
        val testId = UUID.randomUUID().toString().replace("-", "")
        val rawId = UUID.randomUUID().toString()
        tableName =
            TableName(
                namespace = configuration.schema,
                name = "_airbyte_connection_test_$testId",
            )
        s3Key = buildS3TestKey(testId)

        try {
            runBlocking {
                testRedshiftConnection()
                testCreateTable(tableName!!)

                testS3WriteAccess(s3Key!!, rawId)
                testCopyFromS3(tableName!!, s3Key!!)

                testAlterTable(tableName!!)

                testDeleteRow(tableName!!, rawId)
                testS3Cleanup(s3Key!!)
            }

            log.info { "Redshift connection check completed successfully" }
        } catch (e: SQLException) {
            val errorMessage = buildErrorMessage(e)
            log.error(e) { "Redshift connection check failed: $errorMessage" }
            throw IllegalStateException(errorMessage, e)
        } catch (e: S3Exception) {
            val errorMessage =
                e.awsErrorDetails()?.errorMessage() ?: e.message ?: "Unknown S3 error"
            log.error(e) { "Redshift connection check failed: $errorMessage" }
            throw IllegalStateException(errorMessage, e)
        } catch (e: Exception) {
            log.error(e) { "Redshift connection check failed with unexpected error" }
            throw e
        }
    }

    /** Best-effort cleanup of the Redshift test table */
    override fun cleanup() {
        log.info { "Checker Cleaning up..." }

        try {
            val table = tableName
            if (table != null) {
                runBlocking { client.dropTable(table) }
                log.info { "Cleaned up Redshift table: ${table.namespace}.${table.name}" }
            }
        } catch (e: Exception) {
            log.warn(e) { "Failed to clean up Redshift table" }
        }
    }

    /**
     * Validates JDBC connectivity, credentials, and network reachability by executing a query. This
     * exercises the full connection path: SSL, SSH tunnel (if configured),
     */
    private suspend fun testRedshiftConnection() {
        log.info {
            "Test 1: Check Redshift connectivity to " +
                "${configuration.host}:${configuration.port}/${configuration.database}..."
        }
        client.ping()
    }

    /** Uploads a gzip-compressed CSV file with one test row to S3. */
    private suspend fun testS3WriteAccess(s3Key: String, rawId: String) {
        log.info { "Test 2: Check S3 write access..." }
        val s3Config = configuration.uploadingMethod!!

        val csvBytes = buildGzipCsv(rawId)
        client.uploadToS3(s3Config.s3BucketName, s3Key, csvBytes)
    }

    /**
     * Creates the test schema (if needed) and table in Redshift. The table has the standard Airbyte
     * meta columns plus one user column (`test_key`).
     */
    private suspend fun testCreateTable(tableName: TableName) {
        log.info { "Test 3: Check CREATE access for ${tableName.namespace}.${tableName.name}..." }
        client.createNamespace(tableName.namespace)
        client.createTable(
            buildCheckStream(tableName),
            tableName,
            ColumnNameMapping(emptyMap()),
            replace = false,
        )
    }

    /** Executes the Redshift COPY command to load the gzip CSV from S3 into the test table */
    private suspend fun testCopyFromS3(tableName: TableName, s3Key: String) {
        log.info { "Test 4: Check COPY permission to move data from S3 to Redshift..." }
        val s3Config = configuration.uploadingMethod!!
        val s3Path = "s3://${s3Config.s3BucketName}/$s3Key"

        client.copyFromS3(
            tableName = tableName,
            s3Path = s3Path,
            accessKeyId = s3Config.accessKeyId,
            secretAccessKey = s3Config.secretAccessKey,
            region = s3Config.s3BucketRegion,
        )

        val count = client.countTable(tableName)
        require(count == 1L) { "Expected 1 row in check table, found $count" }
    }

    /** Tests ALTER TABLE permission by adding a throwaway column to the test table. */
    private suspend fun testAlterTable(tableName: TableName) {
        log.info { "Test 5: Check ALTER TABLE permission..." }
        client.addColumn(tableName, CHECK_ALTER_COLUMN_NAME, RedshiftDataType.VARCHAR.typeName)
    }

    /** Deletes the test row by its `_airbyte_raw_id` */
    private suspend fun testDeleteRow(tableName: TableName, rawId: String) {
        log.info { "Test 6: Check DELETE permission..." }
        client.deleteByRawId(tableName, rawId)
    }

    /** Deletes the test S3 object to verify S3 delete permissions. */
    private suspend fun testS3Cleanup(s3Key: String) {
        log.info { "Test 7: Check S3 DELETE object permission..." }
        val s3Config = configuration.uploadingMethod!!
        client.deleteFromS3(s3Config.s3BucketName, s3Key)
    }

    /** Builds the S3 key for the test CSV file, respecting the configured bucket path prefix. */
    private fun buildS3TestKey(testId: String): String {
        val prefix =
            configuration.uploadingMethod!!.s3BucketPath?.let { path ->
                val trimmed = path.trimEnd('/')
                if (trimmed.isNotEmpty()) "$trimmed/" else ""
            }
                ?: ""
        return "${prefix}_airbyte_check_$testId.csv.gz"
    }

    /** Builds a [DestinationStream] for the check table with one user column (`test_key`). */
    private fun buildCheckStream(tableName: TableName): DestinationStream =
        DestinationStream(
            unmappedNamespace = tableName.namespace,
            unmappedName = tableName.name,
            generationId = 0L,
            minimumGenerationId = 0L,
            syncId = 0L,
            namespaceMapper = NamespaceMapper(),
            tableSchema =
                StreamTableSchema(
                    tableNames =
                        TableNames(
                            finalTableName = tableName,
                            tempTableName = tableName,
                        ),
                    columnSchema =
                        ColumnSchema(
                            inputToFinalColumnNames = mapOf(CHECK_COLUMN_NAME to CHECK_COLUMN_NAME),
                            finalSchema =
                                mapOf(
                                    CHECK_COLUMN_NAME to
                                        ColumnType(RedshiftDataType.VARCHAR.typeName, true)
                                ),
                            inputSchema = emptyMap(),
                        ),
                    importType = Append,
                ),
        )

    /**
     * Builds a gzip-compressed CSV byte array with a header row and one data row.
     *
     * The columns match the table created by [buildCheckStream]: `_airbyte_raw_id,
     * _airbyte_extracted_at, _airbyte_meta, _airbyte_generation_id, test_key`
     */
    private fun buildGzipCsv(rawId: String): ByteArray {
        val header =
            "_airbyte_raw_id,_airbyte_extracted_at,_airbyte_meta,_airbyte_generation_id,$CHECK_COLUMN_NAME"
        val now = OffsetDateTime.now()
        val row = """"$rawId","$now","{}","0","$CHECK_COLUMN_VALUE""""

        val baos = ByteArrayOutputStream()
        GZIPOutputStream(baos).use { gzip ->
            OutputStreamWriter(gzip, StandardCharsets.UTF_8).use { writer ->
                writer.write(header)
                writer.write("\n")
                writer.write(row)
                writer.write("\n")
            }
        }
        return baos.toByteArray()
    }

    /** Maps [SQLException] state codes to user-friendly error messages. */
    private fun buildErrorMessage(e: SQLException): String {
        val sqlState = e.sqlState ?: "Unknown"
        val errorCode = e.errorCode

        return when {
            sqlState.startsWith("28") ->
                "Database authentication failed. Please verify your username and password. " +
                    "State code: $sqlState;"
            sqlState.startsWith("3D") ->
                "Database '${configuration.database}' does not exist or is not accessible. " +
                    "State code: $sqlState;"
            sqlState.startsWith("08") ->
                "Database connection failed. " +
                    "Please verify the host and port are correct and the server is reachable. " +
                    "State code: $sqlState;"
            sqlState.startsWith("42") ->
                "Database permission denied or invalid operation. ${e.message} " +
                    "State code: $sqlState;"
            else ->
                "Database connection check failed: ${e.message} " +
                    "State code: $sqlState; Error code: $errorCode"
        }
    }
}
