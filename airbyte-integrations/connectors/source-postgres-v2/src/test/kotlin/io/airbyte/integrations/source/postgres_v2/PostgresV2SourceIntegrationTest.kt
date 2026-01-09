/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres_v2

import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import java.sql.Connection
import java.sql.DriverManager
import java.sql.Types
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestInstance
import org.testcontainers.containers.PostgreSQLContainer
import org.testcontainers.utility.DockerImageName

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class PostgresV2SourceIntegrationTest {

    companion object {
        private lateinit var postgres: PostgreSQLContainer<*>

        @BeforeAll
        @JvmStatic
        fun setupContainer() {
            postgres =
                PostgreSQLContainer(DockerImageName.parse("postgres:15-alpine"))
                    .withDatabaseName("testdb")
                    .withUsername("testuser")
                    .withPassword("testpassword")
            postgres.start()
        }

        @AfterAll
        @JvmStatic
        fun teardownContainer() {
            if (::postgres.isInitialized) {
                postgres.stop()
            }
        }
    }

    private fun getConnection(): Connection {
        return DriverManager.getConnection(postgres.jdbcUrl, postgres.username, postgres.password)
    }

    private fun createTestSpec(): PostgresV2SourceConfigurationSpecification {
        return PostgresV2SourceConfigurationSpecification().apply {
            host = postgres.host
            port = postgres.firstMappedPort
            database = postgres.databaseName
            username = postgres.username
            password = postgres.password
            schemas = listOf("public")
            checkpointTargetIntervalSeconds = 300
            concurrency = 1
        }
    }

    @Test
    fun testConfigurationFactory() {
        val spec = createTestSpec()
        val factory = PostgresV2SourceConfigurationFactory()
        val config = factory.make(spec)

        assertEquals(postgres.host, config.realHost)
        assertEquals(postgres.firstMappedPort, config.realPort)
        assertEquals(setOf("public"), config.namespaces)
        assertTrue(config.jdbcUrlFmt.contains("jdbc:postgresql://"))
        assertTrue(config.jdbcUrlFmt.contains(postgres.databaseName))
    }

    @Test
    fun testTypeMapping() {
        val ops = PostgresV2SourceOperations()

        // Test various PostgreSQL types
        val testCases =
            listOf(
                "INT4" to IntFieldType,
                "VARCHAR" to StringFieldType,
                "TEXT" to StringFieldType,
                "BOOLEAN" to io.airbyte.cdk.jdbc.BooleanFieldType,
                "BIGINT" to io.airbyte.cdk.jdbc.LongFieldType,
                "FLOAT8" to io.airbyte.cdk.jdbc.DoubleFieldType,
                "DATE" to io.airbyte.cdk.jdbc.LocalDateFieldType,
                "TIMESTAMP" to io.airbyte.cdk.jdbc.LocalDateTimeFieldType,
                "TIMESTAMPTZ" to io.airbyte.cdk.jdbc.OffsetDateTimeFieldType,
            )

        testCases.forEach { (typeName, expectedType) ->
            val systemType =
                io.airbyte.cdk.discover.SystemType(typeName = typeName, typeCode = Types.OTHER)
            val metadata =
                io.airbyte.cdk.discover.JdbcMetadataQuerier.ColumnMetadata(
                    name = "test_col",
                    label = "test_col",
                    type = systemType,
                    nullable = true,
                )
            val result = ops.toFieldType(metadata)
            assertEquals(
                expectedType::class,
                result::class,
                "Type $typeName should map to ${expectedType::class.simpleName}"
            )
        }
    }

    @Test
    fun testQueryGeneration() {
        val ops = PostgresV2SourceOperations()
        val field = Field("id", IntFieldType)
        val field2 = Field("name", StringFieldType)

        val selectSpec =
            io.airbyte.cdk.read.SelectQuerySpec(
                io.airbyte.cdk.read.SelectColumns(listOf(field, field2)),
                io.airbyte.cdk.read.From("users", "public"),
            )

        val query = ops.generate(selectSpec)

        assertTrue(query.sql.contains("SELECT"))
        assertTrue(query.sql.contains("\"id\""))
        assertTrue(query.sql.contains("\"name\""))
        assertTrue(query.sql.contains("FROM \"public\".\"users\""))
    }

    @Test
    fun testQueryGenerationWithWhere() {
        val ops = PostgresV2SourceOperations()
        val field = Field("id", io.airbyte.cdk.jdbc.LongFieldType)

        val selectSpec =
            io.airbyte.cdk.read.SelectQuerySpec(
                io.airbyte.cdk.read.SelectColumns(listOf(field)),
                io.airbyte.cdk.read.From("users", "public"),
                io.airbyte.cdk.read.Where(
                    io.airbyte.cdk.read.Greater(field, io.airbyte.cdk.util.Jsons.numberNode(10))
                ),
            )

        val query = ops.generate(selectSpec)

        assertTrue(query.sql.contains("WHERE"))
        assertTrue(query.sql.contains("\"id\" > ?"))
    }

    @Test
    fun testQueryGenerationWithOrderByAndLimit() {
        val ops = PostgresV2SourceOperations()
        val field = Field("id", io.airbyte.cdk.jdbc.LongFieldType)

        val selectSpec =
            io.airbyte.cdk.read.SelectQuerySpec(
                io.airbyte.cdk.read.SelectColumns(listOf(field)),
                io.airbyte.cdk.read.From("users", "public"),
                io.airbyte.cdk.read.NoWhere,
                io.airbyte.cdk.read.OrderBy(listOf(field)),
                io.airbyte.cdk.read.Limit(100),
            )

        val query = ops.generate(selectSpec)

        assertTrue(query.sql.contains("ORDER BY \"id\""))
        assertTrue(query.sql.contains("LIMIT ?"))
    }

    @Test
    fun testDatabaseConnectivity() {
        getConnection().use { conn ->
            conn.createStatement().use { stmt ->
                val rs = stmt.executeQuery("SELECT 1")
                assertTrue(rs.next())
                assertEquals(1, rs.getInt(1))
            }
        }
    }

    @Test
    fun testTableCreationAndDiscovery() {
        getConnection().use { conn ->
            // Create test table
            conn.createStatement().use { stmt ->
                stmt.execute(
                    """
                    CREATE TABLE IF NOT EXISTS test_users (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        email TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )
            }

            // Insert test data
            conn
                .prepareStatement(
                    "INSERT INTO test_users (name, email) VALUES (?, ?) ON CONFLICT DO NOTHING"
                )
                .use { pstmt ->
                    pstmt.setString(1, "John Doe")
                    pstmt.setString(2, "john@example.com")
                    pstmt.executeUpdate()
                }

            // Verify data
            conn.createStatement().use { stmt ->
                val rs = stmt.executeQuery("SELECT COUNT(*) FROM test_users")
                assertTrue(rs.next())
                assertTrue(rs.getInt(1) >= 1)
            }
        }
    }

    @Test
    fun testPrimaryKeyStateValue() {
        val pkField = Field("id", io.airbyte.cdk.jdbc.LongFieldType)

        val checkpoint =
            PostgresV2SourceJdbcStreamStateValue.snapshotCheckpoint(
                primaryKey = listOf(pkField),
                primaryKeyCheckpoint = listOf(io.airbyte.cdk.util.Jsons.numberNode(100)),
            )

        assertNotNull(checkpoint)
        assertTrue(checkpoint.has("pk_name"))
        assertTrue(checkpoint.has("pk_val"))
        assertEquals("id", checkpoint.get("pk_name").asText())
        assertEquals("100", checkpoint.get("pk_val").asText())
    }

    @Test
    fun testSnapshotCompleted() {
        val completed = PostgresV2SourceJdbcStreamStateValue.snapshotCompleted

        assertNotNull(completed)
        assertTrue(completed.has("state_type"))
        assertEquals("primary_key", completed.get("state_type").asText())
    }
}
