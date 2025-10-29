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
    @Timeout(120)
    fun testExcludeTodaysDataWithCursorBasedIncremental() {
        // Setup: Create a table with date column for cursor-based incremental sync
        val tableName = "test_exclude_today_incremental"
        val today = LocalDate.now()
        val yesterday = today.minusDays(1)
        val twoDaysAgo = today.minusDays(2)
        val threeDaysAgo = today.minusDays(3)

        // Initial data setup with records from 3 days ago and 2 days ago
        connectionFactory.get().use { connection: Connection ->
            connection.isReadOnly = false

            // Create table
            val createTable =
                """
                DROP TABLE IF EXISTS $tableName;
                CREATE TABLE $tableName (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    order_date DATE,
                    amount DECIMAL(10,2),
                    status VARCHAR(50)
                )
            """.trimIndent()

            connection.createStatement().use { stmt -> stmt.execute(createTable) }

            // Insert initial data (only old records)
            val insertInitialData =
                """
                INSERT INTO $tableName (order_date, amount, status) VALUES
                ('$threeDaysAgo', 100.00, 'initial'),
                ('$twoDaysAgo', 200.00, 'initial');
            """.trimIndent()

            connection.createStatement().use { stmt -> stmt.execute(insertInitialData) }

            log.info { "Created table $tableName with initial data" }
            createdTables.add(tableName)
        }

        // First sync: Initial snapshot with exclude_todays_data = true
        val configWithExclude = createConfig(excludeTodaysData = true)
        val initialRecords = performSync(configWithExclude, tableName, "order_date")

        // Verify initial sync contains only old records
        val initialDates = extractDates(initialRecords, "order_date")
        Assertions.assertEquals(2, initialRecords.size, "Initial sync should have 2 records")
        Assertions.assertTrue(
            initialDates.contains(threeDaysAgo.toString()),
            "Initial sync should include records from 3 days ago"
        )
        Assertions.assertTrue(
            initialDates.contains(twoDaysAgo.toString()),
            "Initial sync should include records from 2 days ago"
        )

        // Add new records including yesterday and today
        connectionFactory.get().use { connection: Connection ->
            connection.isReadOnly = false

            val insertNewData =
                """
                INSERT INTO $tableName (order_date, amount, status) VALUES
                ('$yesterday', 300.00, 'incremental'),
                ('$yesterday', 350.00, 'incremental'),
                ('$today', 400.00, 'incremental_today'),
                ('$today', 450.00, 'incremental_today');
            """.trimIndent()

            connection.createStatement().use { stmt -> stmt.execute(insertNewData) }
            log.info { "Added new records including yesterday and today" }
        }

        // Second sync: Incremental sync should exclude today's data
        val incrementalRecords = performSync(configWithExclude, tableName, "order_date")

        // Extract only the new records from incremental sync
        val allDates = extractDates(incrementalRecords, "order_date")

        // Count records by date
        val todayCount = allDates.count { it == today.toString() }
        val yesterdayCount = allDates.count { it == yesterday.toString() }

        // Verify: Today's records should be excluded in incremental sync
        Assertions.assertEquals(
            0,
            todayCount,
            "Today's records should be excluded during incremental sync when exclude_todays_data is true"
        )

        // Verify: Yesterday's records should be included
        Assertions.assertTrue(
            yesterdayCount >= 2,
            "Yesterday's records should be included in incremental sync"
        )

        // Test without exclude_todays_data to confirm today's records exist
        val configWithoutExclude = createConfig(excludeTodaysData = false)
        val allRecordsIncludingToday = performSync(configWithoutExclude, tableName, "order_date")

        val allDatesWithToday = extractDates(allRecordsIncludingToday, "order_date")
        val todayCountWithoutExclude = allDatesWithToday.count { it == today.toString() }

        Assertions.assertEquals(
            2,
            todayCountWithoutExclude,
            "Today's records should be included when exclude_todays_data is false"
        )

        log.info { "Incremental sync test completed successfully" }
    }

    @Test
    @Timeout(120)
    fun testExcludeTodaysDataNotTriggeredForNonTemporalCursor() {
        // Setup: Create a table with non-temporal cursor field (INTEGER and VARCHAR)
        val tableName = "test_exclude_today_non_temporal"
        val today = LocalDate.now()
        val yesterday = today.minusDays(1)

        connectionFactory.get().use { connection: Connection ->
            connection.isReadOnly = false

            // Create table with INTEGER primary key as cursor and date column for verification
            val createTable =
                """
                DROP TABLE IF EXISTS $tableName;
                CREATE TABLE $tableName (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    order_date DATE,
                    status VARCHAR(50),
                    amount DECIMAL(10,2)
                )
            """.trimIndent()

            connection.createStatement().use { stmt -> stmt.execute(createTable) }

            // Insert test data with today's and yesterday's dates
            // IDs will be 1, 2, 3, 4, 5
            val insertData =
                """
                INSERT INTO $tableName (order_date, status, amount) VALUES
                ('$yesterday', 'old', 100.00),
                ('$yesterday', 'old', 150.00),
                ('$today', 'new', 200.00),
                ('$today', 'new', 250.00),
                ('$today', 'new', 300.00);
            """.trimIndent()

            connection.createStatement().use { stmt -> stmt.execute(insertData) }

            log.info { "Created table $tableName with non-temporal cursor test data" }
            createdTables.add(tableName)
        }

        // Test 1: Using INTEGER cursor field with exclude_todays_data = true
        // The feature should NOT be triggered, all records should be returned
        val configWithExclude = createConfig(excludeTodaysData = true)
        val recordsWithIntCursor = performSync(configWithExclude, tableName, "id")

        // Verify: All records should be included (feature not triggered for INTEGER cursor)
        Assertions.assertEquals(
            5,
            recordsWithIntCursor.size,
            "All 5 records should be included when cursor is INTEGER, even with exclude_todays_data = true"
        )

        // Verify today's records are included
        val dates = extractDates(recordsWithIntCursor, "order_date")
        val todayCount = dates.count { it == today.toString() }
        Assertions.assertEquals(
            3,
            todayCount,
            "Today's 3 records should be included when cursor is INTEGER type"
        )

        // Test 2: Using VARCHAR cursor field with exclude_todays_data = true
        val recordsWithStringCursor = performSync(configWithExclude, tableName, "status")

        // Verify: All records should be included (feature not triggered for VARCHAR cursor)
        Assertions.assertEquals(
            5,
            recordsWithStringCursor.size,
            "All 5 records should be included when cursor is VARCHAR, even with exclude_todays_data = true"
        )

        // Test 3: Incremental sync with non-temporal cursor should also include all new records
        connectionFactory.get().use { connection: Connection ->
            connection.isReadOnly = false

            // Add more records with today's date
            val insertNewData =
                """
                INSERT INTO $tableName (order_date, status, amount) VALUES
                ('$today', 'newer', 350.00),
                ('$today', 'newer', 400.00);
            """.trimIndent()

            connection.createStatement().use { stmt -> stmt.execute(insertNewData) }
            log.info { "Added new records with today's date" }
        }

        // Perform incremental sync with INTEGER cursor
        val incrementalRecords = performSync(configWithExclude, tableName, "id")

        // Verify: All 7 records should be present (5 original + 2 new)
        Assertions.assertEquals(
            7,
            incrementalRecords.size,
            "All records including new today's records should be included in incremental sync with non-temporal cursor"
        )

        // Verify new today's records are included
        val allDates = extractDates(incrementalRecords, "order_date")
        val finalTodayCount = allDates.count { it == today.toString() }
        Assertions.assertEquals(
            5,
            finalTodayCount,
            "All 5 of today's records should be included after incremental sync with non-temporal cursor"
        )

        log.info {
            "Non-temporal cursor test completed successfully - exclude_todays_data feature was correctly NOT triggered"
        }
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
