/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.airbyte.protocol.models.v0.SyncMode
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
                    "DROP TABLE IF EXISTS dbo.table_no_pk_no_clustered",
                    "DROP TABLE IF EXISTS dbo.table_with_non_unique_clustered",
                    "DROP TABLE IF EXISTS dbo.table_with_composite_pk"
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

            // Test Case 1: Table with UNIQUE clustered index but no primary key
            // Expected PK: Empty (no PK constraint)
            // Expected OC: Use the unique clustered index column
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
                    CREATE UNIQUE CLUSTERED INDEX idx_clustered_id
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

            // Test Case 3: Table with both primary key and single-column UNIQUE clustered index on
            // different columns
            // Expected PK: Should return actual PK (id)
            // Expected OC: Should use single-column unique clustered index (code)
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
                    CREATE UNIQUE CLUSTERED INDEX idx_clustered_code
                    ON dbo.table_with_pk_and_single_clustered (code)
                """
                )
            }

            // Test Case 4: Table with primary key and UNIQUE composite clustered index
            // Expected PK: Should return actual PK (id)
            // Expected OC: Should use first PK column since CI is composite
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
                    CREATE UNIQUE CLUSTERED INDEX idx_clustered_composite
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

            // Test Case 6: Table with PK and NON-UNIQUE clustered index
            // Expected PK: Should return actual PK (id)
            // Expected OC: Should fall back to first PK column (not CI, since CI is non-unique)
            connection.createStatement().use { stmt ->
                stmt.execute(
                    """
                    CREATE TABLE dbo.table_with_non_unique_clustered (
                        id INT NOT NULL,
                        category NVARCHAR(50) NOT NULL,
                        name NVARCHAR(100),
                        created_at DATETIME2,
                        CONSTRAINT pk_table6 PRIMARY KEY NONCLUSTERED (id)
                    )
                """
                )
                stmt.execute(
                    """
                    CREATE CLUSTERED INDEX idx_non_unique_category
                    ON dbo.table_with_non_unique_clustered (category)
                """
                )
            }

            // Test Case 7: Table with composite PK (3 columns)
            // Expected PK: Should return all 3 columns
            // Expected OC: Should use first PK column
            connection.createStatement().use { stmt ->
                stmt.execute(
                    """
                    CREATE TABLE dbo.table_with_composite_pk (
                        reg_id INT NOT NULL,
                        agent_id INT NOT NULL,
                        assigned_date DATE NOT NULL,
                        name NVARCHAR(100),
                        CONSTRAINT pk_table7 PRIMARY KEY NONCLUSTERED (reg_id, agent_id, assigned_date)
                    )
                """
                )
            }
        }
    }

    @Test
    @DisplayName("Should return empty PK when only clustered index exists (no PK constraint)")
    fun testClusteredIndexNoPrimaryKey() {
        val streamId =
            StreamIdentifier.from(
                StreamDescriptor().withName("table_with_clustered_no_pk").withNamespace("dbo")
            )

        // Test discovery: should return empty (no PK constraint)
        val primaryKey = metadataQuerier.primaryKey(streamId)
        assertTrue(primaryKey.isEmpty(), "Should return empty list when no PK constraint exists")

        // Test sync strategy: should use clustered index column
        val orderedColumn = metadataQuerier.getOrderedColumnForSync(streamId)
        assertEquals("id", orderedColumn, "Should use clustered index column 'id' for syncing")
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
    @DisplayName("Discovery returns PK, sync strategy prefers clustered index")
    fun testSingleClusteredIndexOverPrimaryKey() {
        val streamId =
            StreamIdentifier.from(
                StreamDescriptor()
                    .withName("table_with_pk_and_single_clustered")
                    .withNamespace("dbo")
            )

        // Test discovery: should return actual PK constraint
        val primaryKey = metadataQuerier.primaryKey(streamId)
        assertEquals(1, primaryKey.size, "Should have one primary key column")
        assertEquals(listOf("id"), primaryKey[0], "Discovery should return actual primary key 'id'")

        // Test sync strategy: should prefer clustered index over PK
        val orderedColumn = metadataQuerier.getOrderedColumnForSync(streamId)
        assertEquals(
            "code",
            orderedColumn,
            "Sync strategy should prefer clustered index 'code' over PK"
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

    @Test
    @DisplayName("Should use user-defined logical PK from catalog when no physical PK exists")
    fun testUserDefinedLogicalPrimaryKey() {
        val streamId =
            StreamIdentifier.from(
                StreamDescriptor().withName("table_no_pk_no_clustered").withNamespace("dbo")
            )

        // Create a ConfiguredAirbyteCatalog with a user-defined logical PK
        val configuredCatalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    listOf(
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName("table_no_pk_no_clustered")
                                    .withNamespace("dbo")
                            )
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withPrimaryKey(listOf(listOf("name")))
                    )
                )

        // Create a new querier with the configured catalog
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
        val querierWithCatalog = MsSqlSourceMetadataQuerier(base, configuredCatalog)

        // Test that it uses the user-defined logical PK
        val primaryKey = querierWithCatalog.primaryKey(streamId)

        assertEquals(1, primaryKey.size, "Should have one logical primary key column")
        assertEquals(
            listOf("name"),
            primaryKey[0],
            "Should use user-defined logical primary key 'name' from catalog"
        )
    }

    @Test
    @DisplayName("Should filter out non-unique clustered index and fall back to PK")
    fun testNonUniqueClusteredIndexFiltered() {
        val streamId =
            StreamIdentifier.from(
                StreamDescriptor().withName("table_with_non_unique_clustered").withNamespace("dbo")
            )

        // Test discovery: should return actual PK constraint
        val primaryKey = metadataQuerier.primaryKey(streamId)
        assertEquals(1, primaryKey.size, "Should have one primary key column")
        assertEquals(listOf("id"), primaryKey[0], "Discovery should return actual primary key 'id'")

        // Verify that non-unique CI is NOT in memoizedClusteredIndexKeys
        val tables = metadataQuerier.memoizedTableNames
        val table =
            tables.find { it.name == "table_with_non_unique_clustered" && it.schema == "dbo" }
        assertNotNull(table, "Should find table_with_non_unique_clustered")
        val clusteredKeys = metadataQuerier.memoizedClusteredIndexKeys[table]
        assertNull(clusteredKeys, "Non-unique clustered index should be filtered out")

        // Test sync strategy: should fall back to first PK column (not CI)
        val orderedColumn = metadataQuerier.getOrderedColumnForSync(streamId)
        assertEquals("id", orderedColumn, "Should fall back to PK 'id' since CI is non-unique")
    }

    @Test
    @DisplayName("Should discover all columns in composite primary key")
    fun testCompositePrimaryKey() {
        val streamId =
            StreamIdentifier.from(
                StreamDescriptor().withName("table_with_composite_pk").withNamespace("dbo")
            )

        // Test discovery: should return all 3 PK columns
        val primaryKey = metadataQuerier.primaryKey(streamId)
        assertEquals(3, primaryKey.size, "Should have three primary key columns")
        assertEquals(listOf("reg_id"), primaryKey[0], "First PK column should be 'reg_id'")
        assertEquals(listOf("agent_id"), primaryKey[1], "Second PK column should be 'agent_id'")
        assertEquals(
            listOf("assigned_date"),
            primaryKey[2],
            "Third PK column should be 'assigned_date'"
        )

        // Test sync strategy: should use first PK column
        val orderedColumn = metadataQuerier.getOrderedColumnForSync(streamId)
        assertEquals("reg_id", orderedColumn, "Should use first PK column 'reg_id' for syncing")
    }

    @Test
    @DisplayName("Should prefer physical PK over user-defined logical PK")
    fun testPhysicalPrimaryKeyPreferredOverLogical() {
        val streamId =
            StreamIdentifier.from(
                StreamDescriptor().withName("table_with_pk_no_clustered").withNamespace("dbo")
            )

        // Create a ConfiguredAirbyteCatalog with a different logical PK
        val configuredCatalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    listOf(
                        ConfiguredAirbyteStream()
                            .withStream(
                                AirbyteStream()
                                    .withName("table_with_pk_no_clustered")
                                    .withNamespace("dbo")
                            )
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withPrimaryKey(listOf(listOf("name")))
                    )
                )

        // Create a new querier with the configured catalog
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
        val querierWithCatalog = MsSqlSourceMetadataQuerier(base, configuredCatalog)

        // Test that it prefers the physical PK over the logical one
        val primaryKey = querierWithCatalog.primaryKey(streamId)

        assertEquals(1, primaryKey.size, "Should have one primary key column")
        assertEquals(
            listOf("id"),
            primaryKey[0],
            "Should use physical primary key 'id' even when logical PK 'name' is defined"
        )
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
                        "DROP TABLE IF EXISTS dbo.table_no_pk_no_clustered",
                        "DROP TABLE IF EXISTS dbo.table_with_non_unique_clustered",
                        "DROP TABLE IF EXISTS dbo.table_with_composite_pk"
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
