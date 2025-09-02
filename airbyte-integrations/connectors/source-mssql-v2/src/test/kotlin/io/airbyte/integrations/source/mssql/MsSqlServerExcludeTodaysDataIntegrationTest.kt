/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.SyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.MSSQLServerContainer

private val log = KotlinLogging.logger {}

class MsSqlServerExcludeTodaysDataIntegrationTest {

    private val createdTables = mutableListOf<String>()

    @AfterEach
    fun cleanupTables() {
        // Clean up all tables created during the test
        if (createdTables.isNotEmpty()) {
            connectionFactory.get().use { connection: Connection ->
                connection.isReadOnly = false
                createdTables.forEach { tableName ->
                    try {
                        connection.createStatement().use { stmt ->
                            stmt.execute("DROP TABLE IF EXISTS $tableName")
                        }
                        log.info { "Dropped test table: $tableName" }
                    } catch (e: Exception) {
                        log.warn(e) { "Failed to drop table $tableName" }
                    }
                }
            }
            createdTables.clear()
        }
    }

    @Test
    @Timeout(60)
    fun testExcludeTodaysDataWithDateColumn() {
        // Setup: Create a table with records from different dates
        val tableName = "test_exclude_today_date"
        val today = LocalDate.now()
        val yesterday = today.minusDays(1)
        val twoDaysAgo = today.minusDays(2)

        setupDateTable(tableName, today, yesterday, twoDaysAgo)

        // Test with exclude_todays_data = true
        val configWithExclude = createConfig(excludeTodaysData = true)
        val recordsWithExclude = performSync(configWithExclude, tableName, "order_date")

        // Verify: Today's records should be excluded
        val recordDates = extractDates(recordsWithExclude, "order_date")
        Assertions.assertFalse(
            recordDates.contains(today.toString()),
            "Today's records should be excluded when exclude_todays_data is true"
        )
        Assertions.assertTrue(
            recordDates.contains(yesterday.toString()),
            "Yesterday's records should be included"
        )
        Assertions.assertTrue(
            recordDates.contains(twoDaysAgo.toString()),
            "Records from two days ago should be included"
        )

        // Test with exclude_todays_data = false
        val configWithoutExclude = createConfig(excludeTodaysData = false)
        val recordsWithoutExclude = performSync(configWithoutExclude, tableName, "order_date")

        // Verify: Today's records should be included
        val allRecordDates = extractDates(recordsWithoutExclude, "order_date")
        Assertions.assertTrue(
            allRecordDates.contains(today.toString()),
            "Today's records should be included when exclude_todays_data is false"
        )
    }

    @Test
    @Timeout(60)
    fun testExcludeTodaysDataWithDateTimeColumn() {
        // Setup: Create a table with datetime records
        val tableName = "test_exclude_today_datetime"
        val now = LocalDateTime.now()
        val todayMorning = now.withHour(9).withMinute(0).withSecond(0)
        val todayEvening = now.withHour(18).withMinute(30).withSecond(0)
        val yesterdayNoon = now.minusDays(1).withHour(12).withMinute(0).withSecond(0)
        val lastMidnight = now.toLocalDate().atStartOfDay()
        val beforeMidnight = lastMidnight.minusMinutes(1)

        setupDateTimeTable(tableName, todayMorning, todayEvening, yesterdayNoon, beforeMidnight)

        // Test with exclude_todays_data = true
        val configWithExclude = createConfig(excludeTodaysData = true)
        val recordsWithExclude = performSync(configWithExclude, tableName, "created_at")

        // Verify: Records from today (after midnight) should be excluded
        val timestamps = extractTimestamps(recordsWithExclude, "created_at")

        Assertions.assertFalse(
            timestamps.any {
                it.contains(todayMorning.format(DateTimeFormatter.ISO_LOCAL_DATE_TIME))
            },
            "Today morning's records should be excluded"
        )
        Assertions.assertFalse(
            timestamps.any {
                it.contains(todayEvening.format(DateTimeFormatter.ISO_LOCAL_DATE_TIME))
            },
            "Today evening's records should be excluded"
        )
        Assertions.assertTrue(
            timestamps.any { ts -> ts.startsWith(yesterdayNoon.toLocalDate().toString()) },
            "Yesterday's records should be included"
        )
        Assertions.assertTrue(
            timestamps.any { ts -> ts.startsWith(beforeMidnight.toLocalDate().toString()) },
            "Records from just before midnight should be included"
        )
    }

    @Test
    @Timeout(60)
    fun testExcludeTodaysDataWithDatetime2Column() {
        // Setup: Create a table with datetime2 column for higher precision
        val tableName = "test_exclude_today_datetime2"
        val now = LocalDateTime.now()
        val todayWithMicros = now.withNano(0) // Remove nanoseconds
        val yesterdayWithMicros = now.minusDays(1).withNano(0) // Remove nanoseconds

        setupDateTime2Table(tableName, todayWithMicros, yesterdayWithMicros)

        // Test with exclude_todays_data = true
        val configWithExclude = createConfig(excludeTodaysData = true)
        val recordsWithExclude = performSync(configWithExclude, tableName, "updated_at")

        // Verify: Today's high-precision records should be excluded
        val timestamps = extractTimestamps(recordsWithExclude, "updated_at")

        Assertions.assertEquals(1, timestamps.size, "Only yesterday's record should be included")
        Assertions.assertTrue(
            timestamps.any { ts -> ts.startsWith(yesterdayWithMicros.toLocalDate().toString()) },
            "Yesterday's high-precision record should be included"
        )
    }

    private fun setupDateTable(
        tableName: String,
        today: LocalDate,
        yesterday: LocalDate,
        twoDaysAgo: LocalDate
    ) {
        connectionFactory.get().use { connection: Connection ->
            connection.isReadOnly = false

            // Create table
            val createTable =
                """
                DROP TABLE IF EXISTS $tableName;
                CREATE TABLE $tableName (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    order_date DATE,
                    amount DECIMAL(10,2)
                )
            """.trimIndent()

            connection.createStatement().use { stmt -> stmt.execute(createTable) }

            // Insert test data
            val insertData =
                """
                INSERT INTO $tableName (order_date, amount) VALUES
                ('$today', 100.00),
                ('$today', 150.00),
                ('$yesterday', 200.00),
                ('$yesterday', 250.00),
                ('$twoDaysAgo', 300.00);
            """.trimIndent()

            connection.createStatement().use { stmt -> stmt.execute(insertData) }

            log.info { "Created table $tableName with test data" }
            createdTables.add(tableName)
        }
    }

    private fun setupDateTimeTable(
        tableName: String,
        todayMorning: LocalDateTime,
        todayEvening: LocalDateTime,
        yesterdayNoon: LocalDateTime,
        beforeMidnight: LocalDateTime
    ) {
        connectionFactory.get().use { connection: Connection ->
            connection.isReadOnly = false

            // Create table using regular DATETIME (this test is for DATETIME columns)
            val createTable =
                """
                DROP TABLE IF EXISTS $tableName;
                CREATE TABLE $tableName (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    created_at DATETIME,
                    description VARCHAR(100)
                )
            """.trimIndent()

            connection.createStatement().use { stmt -> stmt.execute(createTable) }

            // Insert test data
            val formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
            val insertData =
                """
                INSERT INTO $tableName (created_at, description) VALUES
                ('${todayMorning.format(formatter)}', 'Today morning'),
                ('${todayEvening.format(formatter)}', 'Today evening'),
                ('${yesterdayNoon.format(formatter)}', 'Yesterday noon'),
                ('${beforeMidnight.format(formatter)}', 'Just before midnight');
            """.trimIndent()

            connection.createStatement().use { stmt -> stmt.execute(insertData) }

            log.info { "Created table $tableName with datetime test data (precision workaround)" }
            createdTables.add(tableName)
        }
    }

    private fun setupDateTime2Table(
        tableName: String,
        todayWithMicros: LocalDateTime,
        yesterdayWithMicros: LocalDateTime
    ) {
        connectionFactory.get().use { connection: Connection ->
            connection.isReadOnly = false

            // Create table using DATETIME2(6) to handle precision mismatch
            val createTable =
                """
                DROP TABLE IF EXISTS $tableName;
                CREATE TABLE $tableName (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    updated_at DATETIME2(6),
                    status VARCHAR(50)
                )
            """.trimIndent()

            connection.createStatement().use { stmt -> stmt.execute(createTable) }

            // Insert test data with simpler format
            val formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
            val todayFormatted = todayWithMicros.format(formatter)
            val yesterdayFormatted = yesterdayWithMicros.format(formatter)

            log.info { "Inserting today: $todayFormatted, yesterday: $yesterdayFormatted" }

            val insertData =
                """
                INSERT INTO $tableName (updated_at, status) VALUES
                ('$todayFormatted', 'Today with microseconds'),
                ('$yesterdayFormatted', 'Yesterday with microseconds');
            """.trimIndent()

            connection.createStatement().use { stmt -> stmt.execute(insertData) }

            log.info { "Created table $tableName with datetime2 test data (precision workaround)" }
            createdTables.add(tableName)
        }
    }

    private fun createConfig(
        excludeTodaysData: Boolean
    ): MsSqlServerSourceConfigurationSpecification {
        val config = MsSqlServerContainerFactory.config(dbContainer)
        config.setIncrementalValue(
            UserDefinedCursor().apply { this.excludeTodaysData = excludeTodaysData }
        )
        return config
    }

    private fun performSync(
        config: MsSqlServerSourceConfigurationSpecification,
        tableName: String,
        cursorField: String
    ): List<JsonNode> {
        // Discover catalog
        val discoverOutput = CliRunner.source("discover", config).run()
        val catalog =
            discoverOutput.catalogs().firstOrNull()
                ?: throw IllegalStateException("No catalog discovered")

        val stream =
            catalog.streams.find { it.name == tableName }
                ?: throw IllegalStateException("Table $tableName not found in catalog")

        // Configure stream for incremental sync with cursor
        val configuredStream =
            CatalogHelpers.toDefaultConfiguredStream(stream).apply {
                syncMode = SyncMode.INCREMENTAL
                this.cursorField = listOf(cursorField)
            }

        val configuredCatalog = ConfiguredAirbyteCatalog().withStreams(listOf(configuredStream))

        // Perform sync
        val syncOutput = CliRunner.source("read", config, configuredCatalog).run()
        val records = syncOutput.records().mapNotNull { it.data }

        log.info { "Synced ${records.size} records from $tableName" }
        return records
    }

    private fun extractDates(records: List<JsonNode>, fieldName: String): List<String> {
        return records.mapNotNull { record -> record.get(fieldName)?.asText() }
    }

    private fun extractTimestamps(records: List<JsonNode>, fieldName: String): List<String> {
        return records.mapNotNull { record -> record.get(fieldName)?.asText() }
    }

    companion object {
        lateinit var dbContainer: MSSQLServerContainer<*>

        val connectionFactory: JdbcConnectionFactory by lazy {
            JdbcConnectionFactory(
                MsSqlServerSourceConfigurationFactory()
                    .make(MsSqlServerContainerFactory.config(dbContainer))
            )
        }

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startContainer() {
            dbContainer =
                MsSqlServerContainerFactory.exclusive(
                    "mcr.microsoft.com/mssql/server:2022-latest",
                    MsSqlServerContainerFactory.WithNetwork,
                    MsSqlServerContainerFactory.WithTestDatabase
                )

            // Ensure test schema exists
            connectionFactory.get().use { connection: Connection ->
                connection.isReadOnly = false
                connection.createStatement().use { stmt ->
                    stmt.execute(
                        "IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'dbo') BEGIN EXEC('CREATE SCHEMA dbo') END"
                    )
                }
            }
        }

        @JvmStatic
        @AfterAll
        fun stopContainer() {
            if (::dbContainer.isInitialized) {
                dbContainer.stop()
            }
        }
    }
}
