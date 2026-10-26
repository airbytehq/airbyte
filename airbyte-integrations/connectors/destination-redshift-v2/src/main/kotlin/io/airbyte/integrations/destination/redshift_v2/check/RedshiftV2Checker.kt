/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.check

import com.amazonaws.auth.AWSStaticCredentialsProvider
import com.amazonaws.auth.BasicAWSCredentials
import com.amazonaws.services.s3.AmazonS3ClientBuilder
import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.integrations.destination.redshift_v2.spec.RedshiftV2Configuration
import io.airbyte.integrations.destination.redshift_v2.spec.S3StagingConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.sql.Connection
import java.time.Clock
import javax.sql.DataSource

private val log = KotlinLogging.logger {}

@Singleton
class RedshiftV2Checker(
    private val dataSource: DataSource,
    private val clock: Clock,
) : DestinationChecker<RedshiftV2Configuration> {

    private val checkTimestamp = clock.millis()
    private val tableName = "_airbyte_check_table_$checkTimestamp"

    override fun check(config: RedshiftV2Configuration) {
        // Check Redshift connection
        checkRedshiftConnection(config)

        // Check S3 staging if configured
        config.s3Config?.let { s3Config -> checkS3Staging(s3Config) }
    }

    private fun checkRedshiftConnection(config: RedshiftV2Configuration) {
        val qualifiedTableName = "\"${config.schema}\".\"$tableName\""

        dataSource.connection.use { connection ->
            // Create schema if not exists
            connection.execute("CREATE SCHEMA IF NOT EXISTS \"${config.schema}\"")

            // Create test table
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS $qualifiedTableName (
                    test_column VARCHAR(256)
                )
                """.trimIndent()
            )

            // Insert test data
            connection.execute(
                """
                INSERT INTO $qualifiedTableName (test_column) VALUES ('test_value')
                """.trimIndent()
            )

            // Verify the insert
            val count =
                connection.createStatement().use { statement ->
                    statement.executeQuery("SELECT COUNT(*) FROM $qualifiedTableName").use { rs ->
                        if (rs.next()) rs.getLong(1) else 0L
                    }
                }

            require(count == 1L) {
                "Failed to insert expected rows into check table. Actual written: $count"
            }
        }
    }

    private fun getS3CheckKey(s3Config: S3StagingConfiguration): String {
        val basePath = s3Config.s3BucketPath?.trimEnd('/') ?: ""
        return if (basePath.isNotEmpty()) {
            "$basePath/_airbyte_check_$checkTimestamp"
        } else {
            "_airbyte_check_$checkTimestamp"
        }
    }

    private fun checkS3Staging(s3Config: S3StagingConfiguration) {
        log.info { "Checking S3 staging configuration for bucket: ${s3Config.s3BucketName}" }

        val s3Client = createS3Client(s3Config)
        val testKey = getS3CheckKey(s3Config)

        try {
            val testData = """{"test": "data"}"""

            // Write test file
            log.info { "Writing test file to s3://${s3Config.s3BucketName}/$testKey" }
            s3Client.putObject(s3Config.s3BucketName, testKey, testData)

            // Read it back to verify
            log.info { "Reading test file from s3://${s3Config.s3BucketName}/$testKey" }
            val s3Object = s3Client.getObject(s3Config.s3BucketName, testKey)
            val readData = s3Object.objectContent.bufferedReader().use { it.readText() }

            require(readData == testData) {
                "S3 staging check failed: read data does not match written data"
            }

            log.info { "S3 staging check passed successfully" }
        } finally {
            s3Client.shutdown()
        }
    }

    private fun createS3Client(s3Config: S3StagingConfiguration) =
        AmazonS3ClientBuilder.standard()
            .withCredentials(
                AWSStaticCredentialsProvider(
                    BasicAWSCredentials(s3Config.accessKeyId, s3Config.secretAccessKey)
                )
            )
            .withRegion(s3Config.s3BucketRegion.ifEmpty { "us-east-1" })
            .build()

    override fun cleanup(config: RedshiftV2Configuration) {
        // Cleanup Redshift test table
        val qualifiedTableName = "\"${config.schema}\".\"$tableName\""
        try {
            dataSource.connection.use { connection ->
                connection.execute("DROP TABLE IF EXISTS $qualifiedTableName")
            }
        } catch (e: Exception) {
            // Cleanup should not throw
        }

        // Cleanup S3 test file if staging was configured
        config.s3Config?.let { s3Config ->
            val s3Client = createS3Client(s3Config)
            val testKey = getS3CheckKey(s3Config)
            try {
                log.info { "Cleaning up S3 test file: s3://${s3Config.s3BucketName}/$testKey" }
                s3Client.deleteObject(s3Config.s3BucketName, testKey)
            } catch (e: Exception) {
                log.warn(e) { "Failed to cleanup S3 test file" }
            } finally {
                s3Client.shutdown()
            }
        }
    }

    private fun Connection.execute(sql: String) {
        createStatement().use { statement -> statement.execute(sql) }
    }
}
