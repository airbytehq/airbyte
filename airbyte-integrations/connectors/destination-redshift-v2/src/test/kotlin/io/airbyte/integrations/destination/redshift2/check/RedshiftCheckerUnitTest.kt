/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.check

import com.amazonaws.services.s3.AmazonS3
import io.airbyte.integrations.destination.redshift2.config.RedshiftConfiguration
import io.airbyte.integrations.destination.redshift2.config.S3StagingConfiguration
import io.airbyte.integrations.destination.redshift2.connect.S3Connect
import io.airbyte.integrations.destination.redshift2.sql.RedshiftSqlGenerator
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import io.mockk.mockk
import io.mockk.verify
import java.sql.Connection
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.sql.SQLException
import java.sql.Statement
import java.util.stream.Stream
import javax.sql.DataSource
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

    @MockK lateinit var dataSource: DataSource
    @MockK lateinit var s3Connect: S3Connect
    @MockK lateinit var sqlGenerator: RedshiftSqlGenerator
    @MockK lateinit var mockConnection: Connection
    @MockK lateinit var mockStatement: Statement
    @MockK lateinit var mockResultSet: ResultSet
    @MockK lateinit var mockPreparedStatement: PreparedStatement
    @MockK lateinit var mockS3Client: AmazonS3

    private lateinit var checker: RedshiftChecker

    @BeforeEach
    fun setup() {
        // Wire DataSource -> Connection -> Statement/PreparedStatement -> ResultSet
        every { dataSource.connection } returns mockConnection
        every { mockConnection.createStatement() } returns mockStatement
        every { mockConnection.prepareStatement(any()) } returns mockPreparedStatement
        every { mockConnection.close() } returns Unit

        // Statement behavior: execute() succeeds, executeQuery() returns a ResultSet
        every { mockStatement.execute(any<String>()) } returns true
        every { mockStatement.executeQuery(any()) } returns mockResultSet
        every { mockStatement.close() } returns Unit

        // ResultSet: next() returns true, getLong(1) returns 1 (row count = 1)
        every { mockResultSet.next() } returns true
        every { mockResultSet.getLong(1) } returns 1L
        every { mockResultSet.close() } returns Unit

        // PreparedStatement: delete succeeds (1 row affected)
        every { mockPreparedStatement.setString(any(), any()) } returns Unit
        every { mockPreparedStatement.executeUpdate() } returns 1
        every { mockPreparedStatement.close() } returns Unit

        // S3 client: putObject and deleteObject succeed
        every { s3Connect.createS3Client() } returns mockS3Client
        every { mockS3Client.putObject(any<String>(), any(), any(), any()) } returns mockk()
        every { mockS3Client.deleteObject(any<String>(), any<String>()) } returns Unit

        // SQL generator: return dummy SQL strings
        every { sqlGenerator.createNamespace(any()) } returns "CREATE SCHEMA sql"
        every { sqlGenerator.createTable(any(), any()) } returns "CREATE TABLE sql"
        every { sqlGenerator.countTable(any(), any()) } returns "SELECT count sql"
        every { sqlGenerator.deleteByRawId(any()) } returns "DELETE sql"
        every { sqlGenerator.dropTable(any()) } returns "DROP TABLE sql"
        every { sqlGenerator.copyFromS3(any(), any(), any(), any(), any()) } returns "COPY sql"

        checker = RedshiftChecker(dataSource, Fixtures.configuration(), s3Connect, sqlGenerator)
    }

    // ================================================================
    // Happy path
    // ================================================================

    @Test
    fun `check succeeds - all steps complete and expected calls are made`() {
        assertDoesNotThrow { checker.check() }

        // Verify Redshift connectivity (SELECT 1)
        verify { mockStatement.executeQuery(any()) }

        // Verify S3 write
        verify { mockS3Client.putObject(any<String>(), any<String>(), any(), any()) }

        // Verify DDL (createNamespace + createTable)
        verify { sqlGenerator.createNamespace(any()) }
        verify { sqlGenerator.createTable(any(), any()) }

        // Verify count query
        verify { sqlGenerator.countTable(any(), any()) }

        // Verify delete
        verify { sqlGenerator.deleteByRawId(any()) }
        verify { mockPreparedStatement.executeUpdate() }
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
        // Make the very first DB call (SELECT 1) throw a SQLException
        every { mockStatement.executeQuery(any()) } throws SQLException("test error", sqlState, 0)

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
        every { s3Connect.createS3Client() } throws originalException

        val caught = assertThrows<RuntimeException> { checker.check() }
        assertEquals(originalException, caught)
    }

    // ================================================================
    // Row count mismatch
    // ================================================================

    @Test
    fun `check fails when row count is not 1`() {
        // Count returns 0 instead of 1
        every { mockResultSet.getLong(1) } returns 0L

        val caught = assertThrows<IllegalArgumentException> { checker.check() }
        assertTrue(
            caught.message!!.contains("Expected 1 row"),
            "Expected message about row count mismatch but was: ${caught.message}",
        )
    }

    // ================================================================
    // Cleanup
    // ================================================================

    @Test
    fun `cleanup drops Redshift table after check`() {
        // Run check first to populate s3Client, s3Key, tableName
        checker.check()

        // Reset mocks to track only cleanup calls
        io.mockk.clearMocks(mockS3Client, mockStatement, answers = false, recordedCalls = true)

        checker.cleanup()

        // Verify table dropped
        verify { sqlGenerator.dropTable(any()) }
        verify { mockStatement.execute(any<String>()) }
    }

    @Test
    fun `cleanup continues to drop table even when S3 delete fails`() {
        // Run check first
        checker.check()

        // Make S3 delete throw
        every { mockS3Client.deleteObject(any<String>(), any<String>()) } throws
            RuntimeException("S3 failure")

        // cleanup should NOT throw (best-effort)
        assertDoesNotThrow { checker.cleanup() }

        // Verify table drop was still attempted
        verify { sqlGenerator.dropTable(any()) }
    }

    @Test
    fun `cleanup is a no-op when check was never called`() {
        // cleanup() called without prior check() — fields are null
        assertDoesNotThrow { checker.cleanup() }

        // No S3 or DB interactions should occur
        verify(exactly = 0) { mockS3Client.deleteObject(any<String>(), any<String>()) }
        verify(exactly = 0) { sqlGenerator.dropTable(any()) }
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
