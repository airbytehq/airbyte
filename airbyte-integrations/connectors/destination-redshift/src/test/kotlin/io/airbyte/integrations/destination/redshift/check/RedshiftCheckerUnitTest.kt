/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.check

import io.airbyte.integrations.destination.redshift.client.RedshiftAirbyteClient
import io.airbyte.integrations.destination.redshift.config.RedshiftConfiguration
import io.airbyte.integrations.destination.redshift.config.S3StagingConfiguration
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.junit5.MockKExtension
import java.sql.SQLException
import java.util.stream.Stream
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.api.extension.ExtendWith
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

@ExtendWith(MockKExtension::class)
class RedshiftCheckerUnitTest {

    private lateinit var client: RedshiftAirbyteClient
    private lateinit var checker: RedshiftChecker

    @BeforeEach
    fun setup() {
        client =
            io.mockk.mockk<RedshiftAirbyteClient>(relaxed = true) {
                // countTable returns 1 (expected row count after COPY)
                coEvery { countTable(any()) } returns 1L
            }

        checker = RedshiftChecker(client, Fixtures.configuration())
    }

    // ================================================================
    // Happy path
    // ================================================================

    @Test
    fun `check succeeds - all steps complete and expected calls are made`() {
        assertDoesNotThrow { checker.check() }

        // Verify Redshift connectivity
        coVerify { client.ping() }

        // Verify S3 write
        coVerify { client.uploadToS3(any(), any(), any(), any()) }

        // Verify DDL (createNamespace + createTable)
        coVerify { client.createNamespace(any()) }
        coVerify { client.createTable(any(), any(), any(), any()) }

        // Verify COPY + count
        coVerify { client.copyFromS3(any(), any(), any(), any(), any()) }
        coVerify { client.countTable(any()) }

        // Verify ALTER TABLE
        coVerify { client.addColumn(any(), any(), any()) }

        // Verify delete
        coVerify { client.deleteByRawId(any(), any()) }

        // Verify S3 cleanup
        coVerify { client.deleteFromS3(any(), any()) }
    }

    // ================================================================
    // SQL error mapping (parameterized)
    // ================================================================

    @ParameterizedTest(name = "SQLException with state {0} produces message containing \"{1}\"")
    @MethodSource("sqlErrorMappings")
    fun `check wraps SQLException with correct error message`(
        sqlState: String,
        expectedSubstring: String,
    ) {
        // Make the very first DB call (ping) throw a SQLException
        coEvery { client.ping() } throws SQLException("test error", sqlState, 0)

        val caught = assertThrows<IllegalStateException> { checker.check() }
        assertTrue(
            caught.message!!.contains(expectedSubstring),
            "Expected message to contain \"$expectedSubstring\" but was: ${caught.message}",
        )
        assertTrue(
            caught.cause is SQLException,
            "Expected cause to be SQLException but was: ${caught.cause}",
        )
    }

    // ================================================================
    // Non-SQL exception propagation
    // ================================================================

    @Test
    fun `check propagates non-SQL exceptions directly`() {
        val originalException = RuntimeException("S3 network timeout")
        coEvery { client.uploadToS3(any(), any(), any(), any()) } throws originalException

        val caught = assertThrows<RuntimeException> { checker.check() }
        assertEquals(originalException, caught)
    }

    // ================================================================
    // Row count mismatch
    // ================================================================

    @Test
    fun `check fails when row count is not 1`() {
        // Count returns 0 instead of 1
        coEvery { client.countTable(any()) } returns 0L

        val caught = assertThrows<IllegalArgumentException> { checker.check() }
        assertTrue(
            caught.message!!.contains("Expected 1 row"),
            "Expected message about row count mismatch but was: ${caught.message}",
        )
    }

    // ================================================================
    // ALTER TABLE failure
    // ================================================================

    @Test
    fun `check fails when ALTER TABLE is denied`() {
        coEvery { client.addColumn(any(), any(), any()) } throws
            SQLException("permission denied", "42501", 0)

        val caught = assertThrows<IllegalStateException> { checker.check() }
        assertTrue(
            caught.message!!.contains("Database permission denied"),
            "Expected message about permission denied but was: ${caught.message}",
        )
    }

    // ================================================================
    // Cleanup
    // ================================================================

    @Test
    fun `cleanup drops Redshift table after check`() {
        // Run check first to populate tableName
        checker.check()

        checker.cleanup()

        // Verify table dropped
        coVerify { client.dropTable(any()) }
    }

    @Test
    fun `cleanup is a no-op when check was never called`() {
        // cleanup() called without prior check() — fields are null
        assertDoesNotThrow { checker.cleanup() }

        // No drop should occur
        coVerify(exactly = 0) { client.dropTable(any()) }
    }

    // ================================================================
    // Fixtures
    // ================================================================

    object Fixtures {
        fun configuration(
            host: String = "test-host",
            port: Int = 5439,
            database: String = "testdb",
            schema: String = "public",
            username: String = "testuser",
            password: String = "testpass",
        ): RedshiftConfiguration =
            RedshiftConfiguration(
                host = host,
                port = port,
                database = database,
                schema = schema,
                username = username,
                password = password,
                jdbcUrlParams = null,
                uploadingMethod =
                    S3StagingConfiguration(
                        s3BucketName = "test-bucket",
                        s3BucketPath = "test-path",
                        s3BucketRegion = "us-east-1",
                        accessKeyId = "AKIATEST",
                        secretAccessKey = "secret",
                    ),
                tunnelMethod = null,
                dropCascade = false,
            )
    }

    companion object {
        @JvmStatic
        fun sqlErrorMappings(): Stream<Arguments> =
            Stream.of(
                Arguments.of("28000", "Database authentication failed"),
                Arguments.of("3D000", "does not exist"),
                Arguments.of("08001", "Database connection failed"),
                Arguments.of("42501", "Database permission denied"),
                Arguments.of("99999", "Database connection check failed"),
            )
    }
}
