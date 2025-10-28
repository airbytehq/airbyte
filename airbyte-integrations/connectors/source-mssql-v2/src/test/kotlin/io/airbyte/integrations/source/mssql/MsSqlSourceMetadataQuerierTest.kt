/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import org.junit.jupiter.api.*
import org.junit.jupiter.api.Assertions.*
import org.testcontainers.containers.MSSQLServerContainer

private val log = KotlinLogging.logger {}

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class MsSqlSourceMetadataQuerierTest {

    private lateinit var dbContainer: MSSQLServerContainer<*>
    private lateinit var config: MsSqlServerSourceConfiguration
    private lateinit var metadataQuerier: MsSqlSourceMetadataQuerier

    @BeforeAll
    @Timeout(value = 300)
    fun setUp() {
        dbContainer =
            MsSqlServerContainerFactory.shared(
                "mcr.microsoft.com/mssql/server:2022-latest",
                MsSqlServerContainerFactory.WithNetwork,
                MsSqlServerContainerFactory.WithTestDatabase
            )

        val spec = MsSqlServerContainerFactory.config(dbContainer)
        spec.setIncrementalValue(UserDefinedCursor())
        config = MsSqlServerSourceConfigurationFactory().make(spec)

        // Set up tables for testing
        createTestTables()

        // Create metadata querier
        val jdbcConnectionFactory = JdbcConnectionFactory(config)
        val sourceOperations = MsSqlSourceOperations()
        val base =
            JdbcMetadataQuerier(
                DefaultJdbcConstants(),
                config,
                sourceOperations,
                sourceOperations,
                JdbcCheckQueries(),
                jdbcConnectionFactory
            )
        metadataQuerier = MsSqlSourceMetadataQuerier(base)
    }

    private fun createTestTables() {
        JdbcConnectionFactory(config).get().use { connection: Connection ->
            connection.isReadOnly = false

            // Clean up existing test tables
            val dropStatements =
                listOf(
                    "DROP TABLE IF EXISTS dbo.table_with_clustered_no_pk",
                    "DROP TABLE IF EXISTS dbo.table_with_pk_no_clustered",
                    "DROP TABLE IF EXISTS dbo.table_with_pk_and_single_clustered",
                    "DROP TABLE IF EXISTS dbo.table_with_pk_and_composite_clustered",
                    "DROP TABLE IF EXISTS dbo.table_no_pk_no_clustered"
                )

            for (ddl in dropStatements) {
                connection.createStatement().use { stmt ->
                    try {
                        stmt.execute(ddl)
                    } catch (e: Exception) {
                        log.debug { "Table might not exist: ${e.message}" }
                    }
                }
            }

            // Test Case 1: Table with clustered index but no primary key
            // Expected: Should use the clustered index column as primary key
            connection.createStatement().use { stmt ->
                stmt.execute(
                    """
                    CREATE TABLE dbo.table_with_clustered_no_pk (
                        id INT NOT NULL,
                        name NVARCHAR(100),
                        created_at DATETIME2
                    )
                """
                )
                stmt.execute(
                    """
                    CREATE CLUSTERED INDEX idx_clustered_id 
                    ON dbo.table_with_clustered_no_pk (id)
                """
                )
            }

            // Test Case 2: Table with primary key but no clustered index
            // Expected: Should use the primary key
            connection.createStatement().use { stmt ->
                stmt.execute(
                    """
                    CREATE TABLE dbo.table_with_pk_no_clustered (
                        id INT NOT NULL,
                        name NVARCHAR(100),
                        created_at DATETIME2,
                        CONSTRAINT pk_table2 PRIMARY KEY NONCLUSTERED (id)
                    )
                """
                )
            }

            // Test Case 3: Table with both primary key and single-column clustered index on
            // different columns
            // Expected: Should use the single-column clustered index
            connection.createStatement().use { stmt ->
                stmt.execute(
                    """
                    CREATE TABLE dbo.table_with_pk_and_single_clustered (
                        id INT NOT NULL,
                        code NVARCHAR(50) NOT NULL,
                        name NVARCHAR(100),
                        created_at DATETIME2,
                        CONSTRAINT pk_table3 PRIMARY KEY NONCLUSTERED (id)
                    )
                """
                )
                stmt.execute(
                    """
                    CREATE CLUSTERED INDEX idx_clustered_code 
                    ON dbo.table_with_pk_and_single_clustered (code)
                """
                )
            }

            // Test Case 4: Table with primary key and composite clustered index
            // Expected: Should use the primary key (not the composite clustered index)
            connection.createStatement().use { stmt ->
                stmt.execute(
                    """
                    CREATE TABLE dbo.table_with_pk_and_composite_clustered (
                        id INT NOT NULL,
                        code NVARCHAR(50) NOT NULL,
                        category NVARCHAR(50) NOT NULL,
                        name NVARCHAR(100),
                        created_at DATETIME2,
                        CONSTRAINT pk_table4 PRIMARY KEY NONCLUSTERED (id)
                    )
                """
                )
                stmt.execute(
                    """
                    CREATE CLUSTERED INDEX idx_clustered_composite 
                    ON dbo.table_with_pk_and_composite_clustered (code, category)
                """
                )
            }

            // Test Case 5: Table with no primary key and no clustered index
            // Expected: Should return empty list
            connection.createStatement().use { stmt ->
                stmt.execute(
                    """
                    CREATE TABLE dbo.table_no_pk_no_clustered (
                        id INT,
                        name NVARCHAR(100),
                        created_at DATETIME2
                    )
                """
                )
            }
        }
    }

    @Test
    @DisplayName("Should use single-column clustered index when no primary key exists")
    fun testClusteredIndexNoPrimaryKey() {
        val streamId =
            StreamIdentifier.from(
                StreamDescriptor().withName("table_with_clustered_no_pk").withNamespace("dbo")
            )

        val primaryKey = metadataQuerier.primaryKey(streamId)

        assertEquals(1, primaryKey.size, "Should have one primary key column")
        assertEquals(listOf("id"), primaryKey[0], "Should use clustered index column 'id'")
    }

    @Test
    @DisplayName("Should use primary key when no clustered index exists")
    fun testPrimaryKeyNoClusteredIndex() {
        val streamId =
            StreamIdentifier.from(
                StreamDescriptor().withName("table_with_pk_no_clustered").withNamespace("dbo")
            )

        val primaryKey = metadataQuerier.primaryKey(streamId)

        assertEquals(1, primaryKey.size, "Should have one primary key column")
        assertEquals(listOf("id"), primaryKey[0], "Should use primary key column 'id'")
    }

    @Test
    @DisplayName("Should prefer single-column clustered index over primary key")
    fun testSingleClusteredIndexOverPrimaryKey() {
        val streamId =
            StreamIdentifier.from(
                StreamDescriptor()
                    .withName("table_with_pk_and_single_clustered")
                    .withNamespace("dbo")
            )

        val primaryKey = metadataQuerier.primaryKey(streamId)

        assertEquals(1, primaryKey.size, "Should have one primary key column")
        assertEquals(
            listOf("code"),
            primaryKey[0],
            "Should use single-column clustered index 'code' instead of primary key 'id'"
        )
    }

    @Test
    @DisplayName("Should use primary key when clustered index is composite")
    fun testPrimaryKeyWhenCompositeClusteredIndex() {
        val streamId =
            StreamIdentifier.from(
                StreamDescriptor()
                    .withName("table_with_pk_and_composite_clustered")
                    .withNamespace("dbo")
            )

        val primaryKey = metadataQuerier.primaryKey(streamId)

        assertEquals(1, primaryKey.size, "Should have one primary key column")
        assertEquals(
            listOf("id"),
            primaryKey[0],
            "Should use primary key 'id' instead of composite clustered index"
        )
    }

    @Test
    @DisplayName("Should return empty list when no primary key and no clustered index")
    fun testNoPrimaryKeyNoClusteredIndex() {
        val streamId =
            StreamIdentifier.from(
                StreamDescriptor().withName("table_no_pk_no_clustered").withNamespace("dbo")
            )

        val primaryKey = metadataQuerier.primaryKey(streamId)

        assertTrue(
            primaryKey.isEmpty(),
            "Should return empty list when no PK and no clustered index"
        )
    }

    @Test
    @DisplayName("Verify clustered index discovery query")
    fun testClusteredIndexDiscovery() {
        // This test verifies that the clustered index discovery is working correctly
        val memoizedClusteredIndexKeys = metadataQuerier.memoizedClusteredIndexKeys

        // Find our test tables
        val tables = metadataQuerier.memoizedTableNames
        val testTables = tables.filter { it.name.startsWith("table_") && it.schema == "dbo" }

        assertTrue(testTables.size >= 5, "Should have at least 5 test tables")

        // Verify specific clustered indexes are discovered
        val tableWithClusteredNoPk = testTables.find { it.name == "table_with_clustered_no_pk" }
        assertNotNull(tableWithClusteredNoPk, "Should find table_with_clustered_no_pk")
        val clusteredKeys = memoizedClusteredIndexKeys[tableWithClusteredNoPk]
        assertNotNull(clusteredKeys, "Should have clustered index for table_with_clustered_no_pk")
        assertEquals(1, clusteredKeys?.size, "Should have single column clustered index")
        assertEquals(
            listOf("id"),
            clusteredKeys?.get(0),
            "Clustered index should be on 'id' column"
        )

        // Verify composite clustered index
        val tableWithComposite =
            testTables.find { it.name == "table_with_pk_and_composite_clustered" }
        assertNotNull(tableWithComposite, "Should find table_with_pk_and_composite_clustered")
        val compositeKeys = memoizedClusteredIndexKeys[tableWithComposite]
        assertNotNull(compositeKeys, "Should have clustered index for composite table")
        assertEquals(2, compositeKeys?.size, "Should have two columns in composite clustered index")
        assertEquals(listOf("code"), compositeKeys?.get(0), "First column should be 'code'")
        assertEquals(
            listOf("category"),
            compositeKeys?.get(1),
            "Second column should be 'category'"
        )
    }

    @Test
    @DisplayName("Verify primary key discovery query")
    fun testPrimaryKeyDiscovery() {
        // This test verifies that the primary key discovery is working correctly
        val memoizedPrimaryKeys = metadataQuerier.memoizedPrimaryKeys

        // Find our test tables
        val tables = metadataQuerier.memoizedTableNames
        val testTables = tables.filter { it.name.startsWith("table_") && it.schema == "dbo" }

        // Verify primary keys are discovered correctly
        val tableWithPkNoCluster = testTables.find { it.name == "table_with_pk_no_clustered" }
        assertNotNull(tableWithPkNoCluster, "Should find table_with_pk_no_clustered")
        val pkKeys = memoizedPrimaryKeys[tableWithPkNoCluster]
        assertNotNull(pkKeys, "Should have primary key for table_with_pk_no_clustered")
        assertEquals(1, pkKeys?.size, "Should have single column primary key")
        assertEquals(listOf("id"), pkKeys?.get(0), "Primary key should be on 'id' column")

        // Verify table without primary key
        val tableNoPk = testTables.find { it.name == "table_with_clustered_no_pk" }
        assertNotNull(tableNoPk, "Should find table_with_clustered_no_pk")
        val noPkKeys = memoizedPrimaryKeys[tableNoPk]
        assertNull(noPkKeys, "Should not have primary key for table_with_clustered_no_pk")
    }

    @AfterAll
    fun tearDown() {
        // Clean up test tables
        try {
            JdbcConnectionFactory(config).get().use { connection: Connection ->
                connection.isReadOnly = false
                val dropStatements =
                    listOf(
                        "DROP TABLE IF EXISTS dbo.table_with_clustered_no_pk",
                        "DROP TABLE IF EXISTS dbo.table_with_pk_no_clustered",
                        "DROP TABLE IF EXISTS dbo.table_with_pk_and_single_clustered",
                        "DROP TABLE IF EXISTS dbo.table_with_pk_and_composite_clustered",
                        "DROP TABLE IF EXISTS dbo.table_no_pk_no_clustered"
                    )

                for (ddl in dropStatements) {
                    connection.createStatement().use { stmt ->
                        try {
                            stmt.execute(ddl)
                        } catch (e: Exception) {
                            log.debug { "Error dropping table: ${e.message}" }
                        }
                    }
                }
            }
        } catch (e: Exception) {
            log.error { "Error during teardown: ${e.message}" }
        }
    }
}
