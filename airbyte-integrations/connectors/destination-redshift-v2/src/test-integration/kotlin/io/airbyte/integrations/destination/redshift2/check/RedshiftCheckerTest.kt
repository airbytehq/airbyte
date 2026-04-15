/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.check

import com.fasterxml.jackson.databind.DeserializationFeature
import com.fasterxml.jackson.databind.ObjectMapper
import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.integrations.destination.redshift2.config.RedshiftConfiguration
import io.airbyte.integrations.destination.redshift2.config.RedshiftConfigurationFactory
import io.airbyte.integrations.destination.redshift2.config.RedshiftSpecification
import io.airbyte.integrations.destination.redshift2.connect.RedshiftConnect
import io.airbyte.integrations.destination.redshift2.connect.S3Connect
import io.airbyte.integrations.destination.redshift2.schema.RedshiftColumnManager
import io.airbyte.integrations.destination.redshift2.sql.RedshiftSqlGenerator
import java.nio.file.Files
import java.nio.file.Path
import kotlin.test.assertTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestInstance
import org.junit.jupiter.api.assertDoesNotThrow
import org.junit.jupiter.api.assertThrows

/** Integration tests for [RedshiftChecker] against real Redshift + S3 infrastructure. */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class RedshiftCheckerTest {

    private val mapper =
        ObjectMapper().configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)

    private val config = mapper.readTree(Files.readString(Path.of("secrets/config_staging.json")))

    private lateinit var configuration: RedshiftConfiguration
    private lateinit var dataSource: HikariDataSource
    private lateinit var sqlGenerator: RedshiftSqlGenerator

    @BeforeAll
    fun setup() {
        val spec = mapper.treeToValue(config, RedshiftSpecification::class.java)
        configuration = RedshiftConfigurationFactory().makeWithoutExceptionHandling(spec)
        dataSource = RedshiftConnect(configuration).createDataSource()
        sqlGenerator = RedshiftSqlGenerator(RedshiftColumnManager())
    }

    @Test
    fun `check succeeds and cleanup completes without error`() {
        val checker = buildChecker(configuration, dataSource)
        assertDoesNotThrow { checker.check() }
        assertDoesNotThrow { checker.cleanup() }
    }

    @Test
    fun `check fails with bad password`() {
        val badConfig = configuration.copy(password = "wrong_password_xyz")
        val badDataSource = createTestDataSource(badConfig)
        try {
            val checker = buildChecker(badConfig, badDataSource)
            val ex = assertThrows<IllegalStateException> { checker.check() }
            assertTrue(ex.message!!.contains("Database authentication failed"))
            assertDoesNotThrow { checker.cleanup() }
        } finally {
            badDataSource.close()
        }
    }

    @Test
    fun `check fails with nonexistent database`() {
        val badConfig = configuration.copy(database = "nonexistent_db_xyz_12345")
        val badDataSource = createTestDataSource(badConfig)
        try {
            val checker = buildChecker(badConfig, badDataSource)
            val ex = assertThrows<IllegalStateException> { checker.check() }
            assertTrue(ex.message!!.contains("does not exist"))
            assertDoesNotThrow { checker.cleanup() }
        } finally {
            badDataSource.close()
        }
    }

    @Test
    fun `check fails with unresolvable host`() {
        val badConfig = configuration.copy(host = "nonexistent-host.invalid")
        val badDataSource = createTestDataSource(badConfig)
        try {
            val checker = buildChecker(badConfig, badDataSource)
            val ex = assertThrows<IllegalStateException> { checker.check() }
            assertTrue(
                ex.message!!.contains(
                    "Please verify the host and port are correct and the server is reachable"
                )
            )
            assertDoesNotThrow { checker.cleanup() }
        } finally {
            badDataSource.close()
        }
    }

    @Test
    fun `check fails with wrong port`() {
        val badConfig = configuration.copy(port = 1)
        val badDataSource = createTestDataSource(badConfig)
        try {
            val checker = buildChecker(badConfig, badDataSource)
            assertThrows<IllegalStateException> { checker.check() }
            assertDoesNotThrow { checker.cleanup() }
        } finally {
            badDataSource.close()
        }
    }

    @Test
    fun `check fails with nonexistent S3 bucket`() {
        val badS3Config =
            configuration.uploadingMethod!!.copy(
                s3BucketName = "nonexistent-bucket-xyz-12345",
            )
        val badConfig = configuration.copy(uploadingMethod = badS3Config)
        val checker = buildChecker(badConfig, dataSource)

        val ex = assertThrows<IllegalStateException> { checker.check() }
        assertTrue(ex.message!!.contains("bucket does not exist"))
        assertDoesNotThrow { checker.cleanup() }
    }

    @Test
    fun `check fails with invalid S3 credentials`() {
        val badS3Config =
            configuration.uploadingMethod!!.copy(
                accessKeyId = "AKIAINVALID",
                secretAccessKey = "invalid_secret_xyz",
            )
        val badConfig = configuration.copy(uploadingMethod = badS3Config)
        val checker = buildChecker(badConfig, dataSource)

        val ex = assertThrows<IllegalStateException> { checker.check() }
        assertTrue(
            ex.message!!.contains("AWS Access Key Id you provided does not exist in our records.")
        )
        assertDoesNotThrow { checker.cleanup() }
    }

    /** Builds a [RedshiftChecker] from the given config and data source. */
    private fun buildChecker(
        config: RedshiftConfiguration,
        ds: HikariDataSource,
    ): RedshiftChecker =
        RedshiftChecker(ds, config, S3Connect(config).createS3Client(), sqlGenerator)

    /**
     * Creates a [HikariDataSource] with 10-second timeouts (lower than real) for fast failure in
     * tests.
     */
    private fun createTestDataSource(config: RedshiftConfiguration): HikariDataSource {
        val endpoint = RedshiftConnect(config).resolveEndpoint()
        return HikariDataSource(
            HikariConfig().apply {
                connectionTimeout = 10_000
                maximumPoolSize = 2
                minimumIdle = 0
                initializationFailTimeout = -1
                driverClassName = RedshiftConnect.DRIVER_CLASS
                jdbcUrl = "jdbc:redshift://$endpoint/${config.database}"
                username = config.username
                password = config.password
                addDataSourceProperty("ssl", "true")
                addDataSourceProperty("sslfactory", RedshiftConnect.SSL_FACTORY)
                addDataSourceProperty("connectTimeout", "10")
            },
        )
    }
}
