/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.check

import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.model.ObjectMetadata
import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.integrations.destination.redshift2.sql.RedshiftTableOperationsClient
import io.airbyte.integrations.destination.redshift2.sql.RedshiftSqlTypes
import io.airbyte.integrations.destination.redshift2.config.RedshiftConfiguration
import io.airbyte.integrations.destination.redshift2.connect.S3Connect
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.OutputStreamWriter
import java.nio.charset.StandardCharsets
import java.sql.SQLException
import java.time.OffsetDateTime
import java.util.UUID
import java.util.zip.GZIPOutputStream
import javax.sql.DataSource

private val log = KotlinLogging.logger {}

internal const val CHECK_COLUMN_NAME = "test_key"
private const val CHECK_COLUMN_VALUE = "check-value"

/**
 * Redshift connection checker that validates the full S3 staging -> COPY -> Redshift pipeline.
 *
 * Each validation step is a separate function for clarity and debuggability:
 * 1. [testRedshiftConnection] -- Redshift JDBC connectivity
 * 2. [testS3WriteAccess] -- S3 write permission (gzip CSV upload)
 * 3. [testCreateTable] -- Redshift DDL (CREATE SCHEMA + CREATE TABLE)
 * 4. [testCopyFromS3] -- Redshift COPY command from S3
 * 5. [testRowCount] -- verify exactly 1 row was loaded
 * 6. [testDeleteRow] -- delete the test row
 * 7. [cleanup] -- drop Redshift table + delete S3 object
 */
@Singleton
class RedshiftChecker(
    private val dataSource: DataSource,
    private val configuration: RedshiftConfiguration,
    private val s3Connect: S3Connect,
    private val tableOpsClient: RedshiftTableOperationsClient,
) : DestinationChecker {

    override fun check() {
        val testId = UUID.randomUUID().toString().replace("-", "")
        val rawId = UUID.randomUUID().toString()
        val tableName =
            TableName(
                namespace = configuration.schema,
                name = "_airbyte_connection_test_$testId",
            )
        val s3Key = buildS3TestKey(testId)
        var s3Client: AmazonS3? = null

        try {
            // Step 1: Test Redshift connectivity
            testRedshiftConnection()

            // Step 2: Test S3 access and write dummy CSV row
            s3Client = testS3WriteAccess(s3Key, rawId)

            // Step 3: Create test table in Redshift
            testCreateTable(tableName)

            // Step 4: COPY from S3 into Redshift
            testCopyFromS3(tableName, s3Key)

            // Step 5: Verify row count
            testRowCount(tableName)

            // Step 6: Delete the test row
            testDeleteRow(tableName, rawId)

            log.info { "Redshift connection check completed successfully" }
        } catch (e: SQLException) {
            val errorMessage = buildErrorMessage(e)
            log.error(e) { "Redshift connection check failed: $errorMessage" }
            throw IllegalStateException(errorMessage, e)
        } catch (e: Exception) {
            log.error(e) { "Redshift connection check failed with unexpected error" }
            throw e
        } finally {
            // Step 7: Cleanup S3 object and Redshift table
            cleanup(s3Client, s3Key, tableName)
        }
    }

    // ---- Step 1: Redshift Connectivity ----

    /**
     * Validates JDBC connectivity by executing a trivial query.
     * This exercises the full connection path: SSL, SSH tunnel (if configured),
     * credentials, and network reachability.
     */
    private fun testRedshiftConnection() {
        log.info {
            "Step 1: Testing Redshift connectivity to " +
                "${configuration.host}:${configuration.port}/${configuration.database}..."
        }
        dataSource.connection.use { conn ->
            conn.createStatement().use { stmt ->
                stmt.executeQuery("SELECT 1").use { rs ->
                    require(rs.next()) { "Failed to execute basic query against Redshift" }
                }
            }
        }
        log.info { "Step 1: Redshift connection successful" }
    }

    // ---- Step 2: S3 Write Access ----

    /**
     * Creates an S3 client and uploads a gzip-compressed CSV file with one test row.
     * The CSV format matches what the Redshift COPY command expects:
     * header row + one data row with Airbyte meta columns and a test column.
     *
     * @return the [AmazonS3] client for reuse in cleanup.
     */
    private fun testS3WriteAccess(s3Key: String, rawId: String): AmazonS3 {
        log.info { "Step 2: Testing S3 write access..." }
        val s3Client = s3Connect.createS3Client()
        val s3Config = configuration.uploadingMethod!!

        val csvBytes = buildGzipCsv(rawId)
        val metadata =
            ObjectMetadata().apply {
                contentLength = csvBytes.size.toLong()
                contentType = "application/gzip"
            }
        s3Client.putObject(
            s3Config.s3BucketName,
            s3Key,
            ByteArrayInputStream(csvBytes),
            metadata,
        )
        log.info { "Step 2: S3 write successful at s3://${s3Config.s3BucketName}/$s3Key" }
        return s3Client
    }

    // ---- Step 3: Create Table ----

    /**
     * Creates the test schema (if needed) and table in Redshift using [RedshiftTableOperationsClient].
     * The table has the standard Airbyte meta columns plus one user column (`test_key`).
     */
    private fun testCreateTable(tableName: TableName) {
        log.info { "Step 3: Creating test table ${tableName.namespace}.${tableName.name}..." }
        val createSchemaSql = tableOpsClient.createNamespaceSql(tableName.namespace)
        val createTableSql = tableOpsClient.createTable(tableName, buildCheckTableSchema(tableName))

        dataSource.connection.use { conn ->
            conn.createStatement().use { stmt ->
                stmt.execute(createSchemaSql)
                stmt.execute(createTableSql)
            }
        }
        log.info { "Step 3: Table created successfully" }
    }

    // ---- Step 4: COPY from S3 ----

    /**
     * Executes the Redshift COPY command to load the gzip CSV from S3 into the test table.
     * Uses the same COPY options as the production sync pipeline:
     * CSV GZIP, TIMEFORMAT 'auto', STATUPDATE OFF.
     *
     * Note: The COPY SQL is intentionally NOT logged because it contains S3 credentials.
     */
    private fun testCopyFromS3(tableName: TableName, s3Key: String) {
        log.info { "Step 4: COPYing data from S3 to Redshift..." }
        val s3Config = configuration.uploadingMethod!!
        val s3Path = "s3://${s3Config.s3BucketName}/$s3Key"

        // COPY SQL contains credentials -- do NOT log it
        val copySql =
            """
            COPY "${tableName.namespace}"."${tableName.name}"
            FROM '$s3Path'
            CREDENTIALS 'aws_access_key_id=${s3Config.accessKeyId};aws_secret_access_key=${s3Config.secretAccessKey}'
            CSV GZIP
            REGION '${s3Config.s3BucketRegion?.ifBlank { S3Connect.DEFAULT_S3_REGION } ?: S3Connect.DEFAULT_S3_REGION}'
            TIMEFORMAT 'auto'
            STATUPDATE OFF
            IGNOREHEADER 1;
            """
                .trimIndent()

        dataSource.connection.use { conn ->
            conn.createStatement().use { stmt -> stmt.execute(copySql) }
        }
        log.info { "Step 4: COPY from S3 successful" }
    }

    // ---- Step 5: Verify Row Count ----

    /**
     * Queries the test table and verifies that exactly one row was loaded by the COPY command.
     */
    private fun testRowCount(tableName: TableName) {
        log.info { "Step 5: Verifying row count..." }
        val countSql = tableOpsClient.countTableSql(tableName)

        dataSource.connection.use { conn ->
            conn.createStatement().use { stmt ->
                stmt.executeQuery(countSql).use { rs ->
                    require(rs.next()) { "Failed to execute count query" }
                    val count = rs.getLong(1)
                    require(count == 1L) {
                        "Expected 1 row in check table, found $count"
                    }
                }
            }
        }
        log.info { "Step 5: Row count verified (1 row)" }
    }

    // ---- Step 6: Delete Row ----

    /**
     * Deletes the test row by its `_airbyte_raw_id` using the parameterized SQL
     * from [RedshiftTableOperationsClient.deleteByRawId].
     */
    private fun testDeleteRow(tableName: TableName, rawId: String) {
        log.info { "Step 6: Deleting test row..." }
        val deleteSql = tableOpsClient.deleteByRawId(tableName)

        dataSource.connection.use { conn ->
            conn.prepareStatement(deleteSql).use { pstmt ->
                pstmt.setString(1, rawId)
                val deleted = pstmt.executeUpdate()
                require(deleted == 1) { "Expected to delete 1 row, deleted $deleted" }
            }
        }
        log.info { "Step 6: Row deleted successfully" }
    }

    // ---- Step 7: Cleanup ----

    /**
     * Best-effort cleanup of the S3 test object and Redshift test table.
     * Failures are logged as warnings but do not propagate.
     */
    private fun cleanup(s3Client: AmazonS3?, s3Key: String, tableName: TableName) {
        log.info { "Step 7: Cleaning up..." }

        // Delete S3 object
        try {
            val s3Config = configuration.uploadingMethod
            if (s3Client != null && s3Config != null) {
                s3Client.deleteObject(s3Config.s3BucketName, s3Key)
                log.info { "Cleaned up S3 object: $s3Key" }
            }
        } catch (e: Exception) {
            log.warn(e) { "Failed to clean up S3 object: $s3Key" }
        }

        // Drop Redshift table
        try {
            val dropSql = tableOpsClient.dropTableSql(tableName)
            dataSource.connection.use { conn ->
                conn.createStatement().use { stmt -> stmt.execute(dropSql) }
            }
            log.info { "Cleaned up Redshift table: ${tableName.namespace}.${tableName.name}" }
        } catch (e: Exception) {
            log.warn(e) { "Failed to clean up Redshift table" }
        }
    }

    // ---- Helpers ----

    /**
     * Builds the S3 key for the test CSV file, respecting the configured bucket path prefix.
     */
    private fun buildS3TestKey(testId: String): String {
        val prefix = configuration.uploadingMethod?.s3BucketPath?.let { path ->
            val trimmed = path.trimEnd('/')
            if (trimmed.isNotEmpty()) "$trimmed/" else ""
        } ?: ""
        return "${prefix}_airbyte_check_$testId.csv.gz"
    }

    /**
     * Builds a [StreamTableSchema] for the check table with one user column (`test_key`).
     */
    private fun buildCheckTableSchema(tableName: TableName): StreamTableSchema =
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
                        mapOf(CHECK_COLUMN_NAME to ColumnType(RedshiftSqlTypes.VARCHAR_MAX, true)),
                    inputSchema = emptyMap(),
                ),
            importType = Append,
        )

    /**
     * Builds a gzip-compressed CSV byte array with a header row and one data row.
     *
     * The columns match the table created by [buildCheckTableSchema]:
     * `_airbyte_raw_id, _airbyte_extracted_at, _airbyte_meta, _airbyte_generation_id, test_key`
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

    /**
     * Maps [SQLException] state codes to user-friendly error messages.
     */
    private fun buildErrorMessage(e: SQLException): String {
        val sqlState = e.sqlState ?: "Unknown"
        val errorCode = e.errorCode

        return when {
            sqlState.startsWith("28") ->
                "Authentication failed. Please verify your username and password. " +
                    "State code: $sqlState;"
            sqlState.startsWith("3D") ->
                "Database '${configuration.database}' does not exist or is not accessible. " +
                    "State code: $sqlState;"
            sqlState.startsWith("08") ->
                "Failed to connect to Redshift at ${configuration.host}:${configuration.port}. " +
                    "Please verify the host and port are correct and the server is reachable. " +
                    "State code: $sqlState;"
            sqlState.startsWith("42") ->
                "Permission denied or invalid operation. ${e.message} State code: $sqlState;"
            else ->
                "Connection check failed: ${e.message} " +
                    "State code: $sqlState; Error code: $errorCode"
        }
    }
}
