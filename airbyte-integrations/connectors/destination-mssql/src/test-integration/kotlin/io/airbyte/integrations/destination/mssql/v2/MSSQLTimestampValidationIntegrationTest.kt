/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.message.DestinationRecordJsonSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.sql.Connection
import java.sql.DriverManager
import java.util.*
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test

/**
 * Integration test that verifies the full round-trip through [MSSQLQueryBuilder.populateStatement]
 * when a pre-1753 timestamp is sent. The [MSSQLValueCoercer.validateTimestamp] function should
 * nullify the value and `setAsNullValue` should set the parameter to SQL NULL, allowing the INSERT
 * to succeed.
 */
class MSSQLTimestampValidationIntegrationTest {

    companion object {
        private const val TEST_SCHEMA = "ts_validation_test"
        private const val TABLE_NAME = "timestamp_nullify_test"

        private val columns =
            linkedMapOf(
                "id" to FieldType(IntegerType, true),
                "ts_col" to FieldType(TimestampTypeWithoutTimezone, true),
            )

        @JvmStatic
        @BeforeAll
        fun beforeAll() {
            MSSQLContainerHelper.start()
            getConnection().use { conn ->
                conn.createStatement().use { stmt ->
                    stmt.execute(
                        """
                        IF NOT EXISTS (SELECT name FROM sys.schemas WHERE name = '$TEST_SCHEMA')
                        BEGIN
                            EXEC ('CREATE SCHEMA [$TEST_SCHEMA]');
                        END
                        """.trimIndent(),
                    )
                }
            }
        }

        @JvmStatic
        @AfterAll
        fun afterAll() {
            getConnection().use { conn ->
                conn.createStatement().use { stmt ->
                    stmt.execute(
                        """
                        DECLARE @sql NVARCHAR(MAX) = N'';
                        SELECT @sql += 'DROP TABLE ' + QUOTENAME(s.name) + '.' + QUOTENAME(t.name) + ';'
                        FROM sys.schemas s
                        JOIN sys.tables t ON s.schema_id = t.schema_id
                        WHERE s.name = '$TEST_SCHEMA';
                        EXEC sp_executesql @sql;
                        """.trimIndent(),
                    )
                    stmt.execute("DROP SCHEMA IF EXISTS [$TEST_SCHEMA]")
                }
            }
        }

        private fun getConnection(): Connection {
            val host = MSSQLContainerHelper.getHost()
            val port = MSSQLContainerHelper.getPort()
            val user = MSSQLContainerHelper.getUsername()
            val password = MSSQLContainerHelper.getPassword()
            return DriverManager.getConnection(
                "jdbc:sqlserver://$host:$port;encrypt=false;trustServerCertificate=true",
                user,
                password,
            )
        }

        private fun makeStream(): DestinationStream {
            return DestinationStream(
                unmappedNamespace = TEST_SCHEMA,
                unmappedName = TABLE_NAME,
                importType = Append,
                schema = ObjectType(properties = columns),
                generationId = 1,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = NamespaceMapper(),
            )
        }

        private fun makeRecord(stream: DestinationStream, jsonData: String): DestinationRecordRaw {
            val recordMessage =
                AirbyteRecordMessage()
                    .withNamespace(TEST_SCHEMA)
                    .withStream(TABLE_NAME)
                    .withData(jsonData.deserializeToNode())
                    .withEmittedAt(System.currentTimeMillis())

            val airbyteMessage =
                AirbyteMessage().withType(AirbyteMessage.Type.RECORD).withRecord(recordMessage)

            return DestinationRecordRaw(
                stream = stream,
                rawData = DestinationRecordJsonSource(airbyteMessage),
                serializedSizeBytes = jsonData.length.toLong(),
                airbyteRawId = UUID.randomUUID(),
            )
        }
    }

    @Test
    fun `pre-1753 timestamp is nullified and INSERT succeeds via populateStatement`() {
        val stream = makeStream()
        val builder = MSSQLQueryBuilder(defaultSchema = TEST_SCHEMA, stream = stream)

        getConnection().use { conn ->
            // 1. Create the table
            builder.createTableIfNotExists(conn)

            // 2. Build a record with a pre-1753 timestamp (the value that originally crashed)
            val record = makeRecord(stream, """{"id": 1, "ts_col": "0001-01-01T00:00:00"}""")

            // 3. Insert via populateStatement -- this should NOT throw
            val insertSql = builder.getFinalTableInsertColumnHeader()
            conn.prepareStatement(insertSql).use { stmt ->
                builder.populateStatement(stmt, record, builder.finalTableSchema)
                stmt.executeUpdate()
            }

            // 4. Read back the record and verify ts_col is NULL
            conn
                .prepareStatement(
                    "SELECT * FROM [$TEST_SCHEMA].[$TABLE_NAME] WHERE [id] = 1",
                )
                .use { stmt ->
                    stmt.executeQuery().use { rs ->
                        assertTrue(rs.next(), "Expected one row in result set")
                        val result = builder.readResult(rs, builder.finalTableSchema)

                        // ts_col should have been nullified by validateTimestamp
                        val tsValue = result.values["ts_col"]
                        assertEquals(
                            NullValue,
                            tsValue,
                            "Pre-1753 timestamp should be nullified to NULL in the database",
                        )
                    }
                }
        }
    }

    @Test
    fun `valid timestamp passes through populateStatement and round-trips correctly`() {
        val stream = makeStream()
        val builder = MSSQLQueryBuilder(defaultSchema = TEST_SCHEMA, stream = stream)

        getConnection().use { conn ->
            // Table already created by previous test, but ensure it exists
            builder.createTableIfNotExists(conn)

            // Insert a record with a valid timestamp
            val record = makeRecord(stream, """{"id": 2, "ts_col": "2023-06-15T12:34:56"}""")

            val insertSql = builder.getFinalTableInsertColumnHeader()
            conn.prepareStatement(insertSql).use { stmt ->
                builder.populateStatement(stmt, record, builder.finalTableSchema)
                stmt.executeUpdate()
            }

            // Read back and verify the timestamp value is present
            conn
                .prepareStatement(
                    "SELECT * FROM [$TEST_SCHEMA].[$TABLE_NAME] WHERE [id] = 2",
                )
                .use { stmt ->
                    stmt.executeQuery().use { rs ->
                        assertTrue(rs.next(), "Expected one row in result set")
                        val result = builder.readResult(rs, builder.finalTableSchema)

                        val tsValue = result.values["ts_col"]
                        assertTrue(
                            tsValue !is NullValue && tsValue != NullValue,
                            "Valid timestamp should not be null, got: $tsValue",
                        )
                    }
                }
        }
    }
}
