/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.LocalDateFieldType
import io.airbyte.cdk.jdbc.LocalDateTimeFieldType
import io.airbyte.cdk.jdbc.LocalTimeFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.ShortFieldType
import io.airbyte.cdk.read.DatatypeTestCase
import io.airbyte.cdk.read.DatatypeTestOperations
import io.airbyte.cdk.read.DynamicDatatypeTestFactory
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.airbyte.protocol.models.v0.SyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.DynamicNode
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestFactory
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.MySQLContainer

class MySqlSourceDatatypeIntegrationTest {

    @TestFactory
    @Timeout(300)
    fun syncTests(): Iterable<DynamicNode> =
        DynamicDatatypeTestFactory(MySqlSourceDatatypeTestOperations).build(dbContainer)

    /**
     * Regression test for https://github.com/airbytehq/airbyte/discussions/70380.
     *
     * MySQL's JDBC driver reports `TINYINT(1)` columns as BIT/boolean by default. When the user
     * enables the new `treat_tinyint1_as_integer` connector setting, the connector appends
     * `tinyInt1isBit=false` to the JDBC URL so the driver reports them as TINYINT (a small
     * integer); the full-load schema therefore exposes such columns as integers. The Debezium-
     * based CDC path used to unconditionally register a custom converter that coerced `TINYINT(1)`
     * values into booleans, producing `false`/`true` payloads that downstream destinations could
     * not decode as numbers (e.g. `IllegalArgumentException: invalid number value false`). With the
     * fix in place, the converter is omitted when the new option is enabled, so CDC emits the same
     * numeric values as the initial snapshot.
     */
    @Test
    @Timeout(300)
    fun cdcRespectsTreatTinyint1AsInteger() {
        // Reuse the testcontainer's default `test` database; the test MySQL user only has full
        // privileges there.
        val database = "test"
        val tableName = "tinyint1_tbl"
        val streamName = tableName

        fun configSpec(cdc: Boolean): MySqlSourceConfigurationSpecification =
            MySqlContainerFactory.config(dbContainer).apply {
                this.database = database
                this.treatTinyint1AsInteger = true
                if (cdc) setIncrementalValue(Cdc()) else setIncrementalValue(UserDefinedCursor)
            }

        val cdcConfigSpec = configSpec(cdc = true)
        val cdcConfig = MySqlSourceConfigurationFactory().make(cdcConfigSpec)
        JdbcConnectionFactory(cdcConfig).get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { it.execute("USE $database") }
            connection.createStatement().use { it.execute("DROP TABLE IF EXISTS $tableName") }
            connection.createStatement().use {
                it.execute("CREATE TABLE $tableName (k INT PRIMARY KEY, v TINYINT(1))")
            }
            connection.createStatement().use {
                it.execute("INSERT INTO $tableName (k, v) VALUES (1, 0), (2, 1)")
            }
        }

        // Build a catalog around the TINYINT(1) column. With treat_tinyint1_as_integer enabled,
        // the column should be discovered as a Short, not a Boolean.
        fun buildCatalog(
            spec: MySqlSourceConfigurationSpecification,
            cdc: Boolean,
        ): ConfiguredAirbyteCatalog {
            val descriptor = StreamDescriptor().withName(streamName).withNamespace(database)
            val discoveredStream =
                DiscoveredStream(
                    id = StreamIdentifier.Companion.from(descriptor),
                    columns =
                        listOf(
                            EmittedField("k", IntFieldType),
                            EmittedField("v", ShortFieldType),
                        ),
                    primaryKeyColumnIDs = listOf(listOf("k")),
                )
            val airbyteStream: AirbyteStream =
                MySqlSourceOperations()
                    .create(
                        MySqlSourceConfigurationFactory().make(spec),
                        discoveredStream,
                    )
            val configuredStream: ConfiguredAirbyteStream =
                CatalogHelpers.toDefaultConfiguredStream(airbyteStream)
                    .withSyncMode(SyncMode.INCREMENTAL)
                    .withPrimaryKey(discoveredStream.primaryKeyColumnIDs)
                    .apply {
                        if (cdc) {
                            cursorField = listOf(MySqlSourceCdcMetaFields.CDC_CURSOR.id)
                        } else {
                            cursorField = listOf("k")
                        }
                    }
            return ConfiguredAirbyteCatalog().withStreams(listOf(configuredStream))
        }

        // Snapshot read produces the initial values via Debezium.
        val initialOutput =
            CliRunner.source("read", cdcConfigSpec, buildCatalog(cdcConfigSpec, cdc = true)).run()
        val initialState: AirbyteStateMessage = initialOutput.states().last()
        assertVTinyIntValuesAreNumeric(initialOutput.records())

        // Insert another row to produce a binlog event, then verify the converter does not coerce
        // values into booleans.
        JdbcConnectionFactory(cdcConfig).get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use {
                it.execute("INSERT INTO $database.$tableName (k, v) VALUES (3, 0)")
            }
        }
        val cdcOutput =
            CliRunner.source(
                    "read",
                    cdcConfigSpec,
                    buildCatalog(cdcConfigSpec, cdc = true),
                    listOf(initialState),
                )
                .run()
        assertVTinyIntValuesAreNumeric(cdcOutput.records())

        // Stream-mode (full refresh / cursor-based) read should agree with CDC: numeric values.
        val streamConfigSpec = configSpec(cdc = false)
        val streamOutput =
            CliRunner.source("read", streamConfigSpec, buildCatalog(streamConfigSpec, cdc = false))
                .run()
        assertVTinyIntValuesAreNumeric(streamOutput.records())
    }

    private fun assertVTinyIntValuesAreNumeric(records: List<AirbyteRecordMessage>) {
        Assertions.assertTrue(records.isNotEmpty(), "expected at least one record")
        for (record in records) {
            val v = record.data["v"]
            Assertions.assertNotNull(v, "record $record missing 'v' column")
            Assertions.assertFalse(
                v.isBoolean,
                "TINYINT(1) value should not be emitted as boolean when " +
                    "treat_tinyint1_as_integer=true: $record",
            )
            Assertions.assertTrue(
                v.isNumber,
                "TINYINT(1) value should be a number when " +
                    "treat_tinyint1_as_integer=true: $record",
            )
        }
    }

    /**
     * Regression test for https://github.com/airbytehq/oncall/issues/12600.
     *
     * Debezium injects zeroDateTimeBehavior=CONVERT_TO_NULL in the JDBC param which will convert
     * zero dates (i.e. 0000-00-00 00:00:00) to NULL (ref
     * https://github.com/debezium/debezium/blob/f13c18f0db7bb5be47c8c4b427e7138da2a29d99/debezium-connector-mysql/src/main/java/io/debezium/connector/mysql/jdbc/MySqlConnectionConfiguration.java#L23),
     * since they are invalid date/time values in JDBC.
     *
     * The issue occurs when a zero date is converted to NULL for a non-nullable column. In this
     * case, Kafka throws `Invalid value: null used for required field` and terminates the sync. To
     * handle this, the DATE and DATETIME converter handlers register their output schema as
     * optional(), so a zero-date that converts to NULL no longer violates a required field.
     *
     * Here is the mapping:
     * - Datetime (micro and millis): invalid, interpreted as NULL
     * - Date: invalid, interpreted as NULL
     * - Timestamp: interpreted as 0, which is then converted to the Unix epoch, 1970-01-01.
     * Snapshot reads can still produce NULL values.
     * - Time: 00:00:00 represents midnight, which is a valid time value.
     */
    @Test
    @Timeout(300)
    fun cdcRespectsTestZeroDateTimeHandling() {
        // Reuse the testcontainer's default `test` database; the test MySQL user only has full
        // privileges there.
        val database = "test"
        val tableName = "zero_datetime_tbl"
        val streamName = tableName

        fun configSpec(): MySqlSourceConfigurationSpecification =
            MySqlContainerFactory.config(dbContainer).apply {
                this.database = database
                setIncrementalValue(Cdc())
                jdbcUrlParams = "zeroDateTimeBehavior=convertToNull" // mimic Debezium configuration
            }

        val cdcConfigSpec = configSpec()
        val cdcConfig = MySqlSourceConfigurationFactory().make(cdcConfigSpec)
        JdbcConnectionFactory(cdcConfig).get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { it.execute("USE $database") }
            connection.createStatement().use { it.execute("SET SESSION sql_mode = ''") }
            connection.createStatement().use { it.execute("DROP TABLE IF EXISTS $tableName") }
            connection.createStatement().use {
                it.execute(
                    "CREATE TABLE $tableName (k INT PRIMARY KEY, v DATETIME(3) NOT NULL, w DATETIME(6) NOT NULL, " +
                        "y DATETIME(3) NOT NULL DEFAULT '2020-03-30 10:30:00', x DATETIME(6) NOT NULL DEFAULT '2020-03-30 10:30:00')"
                )
            }
            connection.createStatement().use {
                it.execute(
                    "INSERT INTO $tableName (k, v, w, y, x) VALUES (1, '0000-00-00 00:00:00', '0000-00-00 00:00:00', " +
                        "'0000-00-00 00:00:00', '0000-00-00 00:00:00') "
                )
            }
        }

        // Build a catalog around the DATETIME(3) & DATETIME(6) column. A zero-date insert should
        // produce a null value.
        // If default value is configured, it should default to that.
        fun buildCatalog(
            spec: MySqlSourceConfigurationSpecification,
        ): ConfiguredAirbyteCatalog {
            val descriptor = StreamDescriptor().withName(streamName).withNamespace(database)
            val discoveredStream =
                DiscoveredStream(
                    id = StreamIdentifier.Companion.from(descriptor),
                    columns =
                        listOf(
                            EmittedField("k", IntFieldType),
                            EmittedField("v", LocalDateTimeFieldType),
                            EmittedField("w", LocalDateTimeFieldType),
                            EmittedField("y", LocalDateTimeFieldType),
                            EmittedField("x", LocalDateTimeFieldType),
                        ),
                    primaryKeyColumnIDs = listOf(listOf("k")),
                )
            val airbyteStream: AirbyteStream =
                MySqlSourceOperations()
                    .create(
                        MySqlSourceConfigurationFactory().make(spec),
                        discoveredStream,
                    )
            val configuredStream: ConfiguredAirbyteStream =
                CatalogHelpers.toDefaultConfiguredStream(airbyteStream)
                    .withSyncMode(SyncMode.INCREMENTAL)
                    .withPrimaryKey(discoveredStream.primaryKeyColumnIDs)
                    .apply { cursorField = listOf(MySqlSourceCdcMetaFields.CDC_CURSOR.id) }
            return ConfiguredAirbyteCatalog().withStreams(listOf(configuredStream))
        }

        // Snapshot read: Debezium reads the zero-date via JDBC (convertToNull) -> null.
        val initialOutput =
            CliRunner.source("read", cdcConfigSpec, buildCatalog(cdcConfigSpec)).run()
        val initialState: AirbyteStateMessage = initialOutput.states().last()
        assertTrue(initialOutput.records().isNotEmpty())
        assertTrue(initialOutput.records()[0].data["v"].isNull)
        assertTrue(initialOutput.records()[0].data["w"].isNull)
        assertTrue(initialOutput.records()[0].data["y"].isNull)
        assertTrue(initialOutput.records()[0].data["x"].isNull)

        // Binlog read: insert another zero-date row and verify the converter nulls it on the
        // streaming path too and
        // doesn't crush due to the column be non-nullable or use the dafault value when exists.
        // Fresh connection -> must relax sql_mode again.
        JdbcConnectionFactory(cdcConfig).get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { it.execute("SET SESSION sql_mode = ''") }
            connection.createStatement().use {
                it.execute(
                    "INSERT INTO $database.$tableName (k, v, w, y, x) VALUES (2, '0000-00-00 00:00:00', '0000-00-00 00:00:00'," +
                        "'0000-00-00 00:00:00', '0000-00-00 00:00:00')"
                )
            }
        }
        val cdcOutput =
            CliRunner.source(
                    "read",
                    cdcConfigSpec,
                    buildCatalog(cdcConfigSpec),
                    listOf(initialState),
                )
                .run()
        assertTrue(cdcOutput.records().isNotEmpty())
        assertTrue(cdcOutput.records()[0].data["v"].isNull)
        assertTrue(cdcOutput.records()[0].data["w"].isNull)
        // Default values
        assertEquals(
            "2020-03-30T10:30:00.000000",
            cdcOutput.records()[0].data["y"].asText()
        ) // millis
        assertEquals(
            "2020-03-30T10:30:00.000000",
            cdcOutput.records()[0].data["x"].asText()
        ) // micro
    }

    @Test
    @Timeout(300)
    fun cdcRespectsTestDateHandling() {
        // Reuse the testcontainer's default `test` database; the test MySQL user only has full
        // privileges there.
        val database = "test"
        val tableName = "zero_date_tbl"
        val streamName = tableName

        fun configSpec(): MySqlSourceConfigurationSpecification =
            MySqlContainerFactory.config(dbContainer).apply {
                this.database = database
                setIncrementalValue(Cdc())
                jdbcUrlParams = "zeroDateTimeBehavior=convertToNull" // mimic Debezium configuration
            }

        val cdcConfigSpec = configSpec()
        val cdcConfig = MySqlSourceConfigurationFactory().make(cdcConfigSpec)
        JdbcConnectionFactory(cdcConfig).get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { it.execute("USE $database") }
            connection.createStatement().use { it.execute("SET SESSION sql_mode = ''") }
            connection.createStatement().use { it.execute("DROP TABLE IF EXISTS $tableName") }
            connection.createStatement().use {
                it.execute(
                    "CREATE TABLE $tableName (k INT PRIMARY KEY, v DATE NOT NULL, w DATE NOT NULL DEFAULT '2025-05-05')"
                )
            }
            connection.createStatement().use {
                it.execute(
                    "INSERT INTO $tableName (k, v, w) VALUES (1, '0000-00-00', '0000-00-00') "
                )
            }
        }

        // Build a catalog around the DATE column. A zero-date insert should produce a null value.
        fun buildCatalog(
            spec: MySqlSourceConfigurationSpecification,
        ): ConfiguredAirbyteCatalog {
            val descriptor = StreamDescriptor().withName(streamName).withNamespace(database)
            val discoveredStream =
                DiscoveredStream(
                    id = StreamIdentifier.Companion.from(descriptor),
                    columns =
                        listOf(
                            EmittedField("k", IntFieldType),
                            EmittedField("v", LocalDateFieldType),
                            EmittedField("w", LocalDateFieldType),
                        ),
                    primaryKeyColumnIDs = listOf(listOf("k")),
                )
            val airbyteStream: AirbyteStream =
                MySqlSourceOperations()
                    .create(
                        MySqlSourceConfigurationFactory().make(spec),
                        discoveredStream,
                    )
            val configuredStream: ConfiguredAirbyteStream =
                CatalogHelpers.toDefaultConfiguredStream(airbyteStream)
                    .withSyncMode(SyncMode.INCREMENTAL)
                    .withPrimaryKey(discoveredStream.primaryKeyColumnIDs)
                    .apply { cursorField = listOf(MySqlSourceCdcMetaFields.CDC_CURSOR.id) }
            return ConfiguredAirbyteCatalog().withStreams(listOf(configuredStream))
        }

        // Snapshot read: Debezium reads the zero-date via JDBC (convertToNull) -> null.
        val initialOutput =
            CliRunner.source("read", cdcConfigSpec, buildCatalog(cdcConfigSpec)).run()
        val initialState: AirbyteStateMessage = initialOutput.states().last()
        assertTrue(initialOutput.records().isNotEmpty())
        assertTrue(initialOutput.records()[0].data["v"].isNull)
        assertTrue(initialOutput.records()[0].data["w"].isNull)

        // Binlog read: insert another zero-date row and verify the converter nulls it on the
        // streaming path too and
        // doesn't crush due to the column be non-nullable. Fresh connection -> must relax sql_mode
        // again.
        JdbcConnectionFactory(cdcConfig).get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { it.execute("SET SESSION sql_mode = ''") }
            connection.createStatement().use {
                it.execute(
                    "INSERT INTO $database.$tableName (k, v, w) VALUES (2, '0000-00-00', '0000-00-00')"
                )
            }
        }
        val cdcOutput =
            CliRunner.source(
                    "read",
                    cdcConfigSpec,
                    buildCatalog(cdcConfigSpec),
                    listOf(initialState),
                )
                .run()
        assertTrue(cdcOutput.records().isNotEmpty())
        assertTrue(cdcOutput.records()[0].data["v"].isNull)
        // Default value
        assertEquals("2025-05-05", cdcOutput.records()[0].data["w"].asText())
    }

    @Test
    @Timeout(300)
    fun cdcRespectsTestTimestampHandling() {
        // Reuse the testcontainer's default `test` database; the test MySQL user only has full
        // privileges there.
        val database = "test"
        val tableName = "zero_timestamp_tbl"
        val streamName = tableName

        fun configSpec(): MySqlSourceConfigurationSpecification =
            MySqlContainerFactory.config(dbContainer).apply {
                this.database = database
                setIncrementalValue(Cdc())
                jdbcUrlParams = "zeroDateTimeBehavior=convertToNull" // mimic Debezium configuration
            }

        val cdcConfigSpec = configSpec()
        val cdcConfig = MySqlSourceConfigurationFactory().make(cdcConfigSpec)
        JdbcConnectionFactory(cdcConfig).get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { it.execute("USE $database") }
            connection.createStatement().use { it.execute("SET SESSION sql_mode = ''") }
            connection.createStatement().use { it.execute("DROP TABLE IF EXISTS $tableName") }
            connection.createStatement().use {
                it.execute(
                    "CREATE TABLE $tableName (k INT PRIMARY KEY, v TIMESTAMP NOT NULL, w TIMESTAMP NOT NULL DEFAULT '2025-05-05 00:00:00') "
                )
            }
            connection.createStatement().use {
                it.execute(
                    "INSERT INTO $tableName (k, v, w) VALUES (1, '0000-00-00 00:00:00', '0000-00-00 00:00:00') "
                )
            }
        }

        // Build a catalog around the TIMESTAMP column. A zero-date insert should produce a null
        // value.
        fun buildCatalog(
            spec: MySqlSourceConfigurationSpecification,
        ): ConfiguredAirbyteCatalog {
            val descriptor = StreamDescriptor().withName(streamName).withNamespace(database)
            val discoveredStream =
                DiscoveredStream(
                    id = StreamIdentifier.Companion.from(descriptor),
                    columns =
                        listOf(
                            EmittedField("k", IntFieldType),
                            EmittedField("v", OffsetDateTimeFieldType),
                            EmittedField("w", OffsetDateTimeFieldType),
                        ),
                    primaryKeyColumnIDs = listOf(listOf("k")),
                )
            val airbyteStream: AirbyteStream =
                MySqlSourceOperations()
                    .create(
                        MySqlSourceConfigurationFactory().make(spec),
                        discoveredStream,
                    )
            val configuredStream: ConfiguredAirbyteStream =
                CatalogHelpers.toDefaultConfiguredStream(airbyteStream)
                    .withSyncMode(SyncMode.INCREMENTAL)
                    .withPrimaryKey(discoveredStream.primaryKeyColumnIDs)
                    .apply { cursorField = listOf(MySqlSourceCdcMetaFields.CDC_CURSOR.id) }
            return ConfiguredAirbyteCatalog().withStreams(listOf(configuredStream))
        }

        // Snapshot read: Debezium reads the zero-date via JDBC (convertToNull) -> null.
        val initialOutput =
            CliRunner.source("read", cdcConfigSpec, buildCatalog(cdcConfigSpec)).run()
        val initialState: AirbyteStateMessage = initialOutput.states().last()
        assertTrue(initialOutput.records().isNotEmpty())
        assertTrue(initialOutput.records()[0].data["v"].isNull)
        assertTrue(initialOutput.records()[0].data["w"].isNull)

        // Binlog read: insert another zero-date row and verify the converter convert this to Unix
        // epoch.
        // Fresh connection -> must relax sql_mode again.
        JdbcConnectionFactory(cdcConfig).get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { it.execute("SET SESSION sql_mode = ''") }
            connection.createStatement().use {
                it.execute(
                    "INSERT INTO $database.$tableName (k, v, w) VALUES (2, '0000-00-00 00:00:00', '0000-00-00 00:00:00')"
                )
            }
        }
        val cdcOutput =
            CliRunner.source(
                    "read",
                    cdcConfigSpec,
                    buildCatalog(cdcConfigSpec),
                    listOf(initialState),
                )
                .run()
        assertTrue(cdcOutput.records().isNotEmpty())
        // Timestamp zero dates are converted to 0 which is represent as Unix epoch.
        // Since the column is not getting a NULL value, the default value will be ignored.
        assertEquals(
            expected = "1970-01-01T00:00:00.000000Z",
            actual = cdcOutput.records()[0].data["v"].asText()
        )
        assertEquals(
            expected = "1970-01-01T00:00:00.000000Z",
            actual = cdcOutput.records()[0].data["w"].asText()
        )
    }

    @Test
    @Timeout(300)
    fun cdcRespectsTestTimeHandling() {
        // Reuse the testcontainer's default `test` database; the test MySQL user only has full
        // privileges there.
        val database = "test"
        val tableName = "zero_time_tbl"
        val streamName = tableName

        fun configSpec(): MySqlSourceConfigurationSpecification =
            MySqlContainerFactory.config(dbContainer).apply {
                this.database = database
                setIncrementalValue(Cdc())
                jdbcUrlParams = "zeroDateTimeBehavior=convertToNull" // mimic Debezium configuration
            }

        val cdcConfigSpec = configSpec()
        val cdcConfig = MySqlSourceConfigurationFactory().make(cdcConfigSpec)
        JdbcConnectionFactory(cdcConfig).get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { it.execute("USE $database") }
            connection.createStatement().use { it.execute("SET SESSION sql_mode = ''") }
            connection.createStatement().use { it.execute("DROP TABLE IF EXISTS $tableName") }
            connection.createStatement().use {
                it.execute("CREATE TABLE $tableName (k INT PRIMARY KEY, v TIME NOT NULL)")
            }
            connection.createStatement().use {
                it.execute("INSERT INTO $tableName (k, v) VALUES (1, '00:00:00') ")
            }
        }

        // Build a catalog around the TIME column. A zero-date is valid (midnight)
        fun buildCatalog(
            spec: MySqlSourceConfigurationSpecification,
        ): ConfiguredAirbyteCatalog {
            val descriptor = StreamDescriptor().withName(streamName).withNamespace(database)
            val discoveredStream =
                DiscoveredStream(
                    id = StreamIdentifier.Companion.from(descriptor),
                    columns =
                        listOf(
                            EmittedField("k", IntFieldType),
                            EmittedField("v", LocalTimeFieldType),
                        ),
                    primaryKeyColumnIDs = listOf(listOf("k")),
                )
            val airbyteStream: AirbyteStream =
                MySqlSourceOperations()
                    .create(
                        MySqlSourceConfigurationFactory().make(spec),
                        discoveredStream,
                    )
            val configuredStream: ConfiguredAirbyteStream =
                CatalogHelpers.toDefaultConfiguredStream(airbyteStream)
                    .withSyncMode(SyncMode.INCREMENTAL)
                    .withPrimaryKey(discoveredStream.primaryKeyColumnIDs)
                    .apply { cursorField = listOf(MySqlSourceCdcMetaFields.CDC_CURSOR.id) }
            return ConfiguredAirbyteCatalog().withStreams(listOf(configuredStream))
        }

        // Snapshot read: Debezium reads the values as midnight.
        val initialOutput =
            CliRunner.source("read", cdcConfigSpec, buildCatalog(cdcConfigSpec)).run()
        val initialState: AirbyteStateMessage = initialOutput.states().last()
        assertTrue(initialOutput.records().isNotEmpty())
        assertEquals("00:00:00.000000", initialOutput.records()[0].data["v"].asText())

        // Binlog read: insert another zero-date row.
        // Fresh connection -> must relax sql_mode again.
        JdbcConnectionFactory(cdcConfig).get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { it.execute("SET SESSION sql_mode = ''") }
            connection.createStatement().use {
                it.execute("INSERT INTO $database.$tableName (k, v) VALUES (2, '00:00:00')")
            }
        }
        val cdcOutput =
            CliRunner.source(
                    "read",
                    cdcConfigSpec,
                    buildCatalog(cdcConfigSpec),
                    listOf(initialState),
                )
                .run()
        assertTrue(cdcOutput.records().isNotEmpty())
        assertEquals(
            expected = "00:00:00.000000",
            actual = cdcOutput.records()[0].data["v"].asText()
        )
    }

    companion object {

        lateinit var dbContainer: MySQLContainer<*>

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startAndProvisionTestContainer() {
            dbContainer = MySqlContainerFactory.shared("mysql:9.2.0", MySqlContainerFactory.WithCdc)
        }
    }
}

object MySqlSourceDatatypeTestOperations :
    DatatypeTestOperations<
        MySQLContainer<*>,
        MySqlSourceConfigurationSpecification,
        MySqlSourceConfiguration,
        MySqlSourceConfigurationFactory,
        MySqlSourceDatatypeTestCase
    > {

    private val log = KotlinLogging.logger {}

    override val withGlobal: Boolean = true
    override val globalCursorMetaField: MetaField = MySqlSourceCdcMetaFields.CDC_CURSOR

    override fun streamConfigSpec(
        container: MySQLContainer<*>
    ): MySqlSourceConfigurationSpecification =
        MySqlContainerFactory.config(container).also { it.setIncrementalValue(UserDefinedCursor) }

    override fun globalConfigSpec(
        container: MySQLContainer<*>
    ): MySqlSourceConfigurationSpecification =
        MySqlContainerFactory.config(container).also { it.setIncrementalValue(Cdc()) }

    override val configFactory: MySqlSourceConfigurationFactory = MySqlSourceConfigurationFactory()

    override fun createStreams(config: MySqlSourceConfiguration) {
        JdbcConnectionFactory(config).get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { it.execute("CREATE DATABASE IF NOT EXISTS test") }
            connection.createStatement().use { it.execute("USE test") }
            for ((_, case) in testCases) {
                for (ddl in case.ddl) {
                    log.info { "test case ${case.id}: executing $ddl" }
                    connection.createStatement().use { stmt -> stmt.execute(ddl) }
                }
            }
        }
    }

    override fun populateStreams(config: MySqlSourceConfiguration) {
        JdbcConnectionFactory(config).get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { it.execute("USE test") }
            for ((_, case) in testCases) {
                for (dml in case.dml) {
                    log.info { "test case ${case.id}: executing $dml" }
                    connection.createStatement().use { stmt -> stmt.execute(dml) }
                }
            }
        }
    }

    val bitValues =
        mapOf(
            "b'1'" to "true",
            "b'0'" to "false",
        )

    val multiBitValues =
        mapOf(
            "b'10101010'" to """"qg=="""",
        )

    val stringValues =
        mapOf(
            "'abcdef'" to """"abcdef"""",
            "'ABCD'" to """"ABCD"""",
            "'OXBEEF'" to """"OXBEEF"""",
        )

    val jsonValues = mapOf("""'{"col1": "v1"}'""" to """"{\"col1\": \"v1\"}"""")

    val yearValues =
        mapOf(
            "1992" to """1992""",
            "2002" to """2002""",
            "70" to """1970""",
        )

    val bigDecimalValues =
        mapOf(
            "10000000000000000000000000000000000000000.0001" to
                "10000000000000000000000000000000000000000.0001",
        )

    val bigIntegerValues =
        mapOf(
            "10000000000000000000000000000000000000000" to
                "10000000000000000000000000000000000000000",
        )

    val decimalValues =
        mapOf(
            "0.2" to """0.2""",
        )

    val floatValues =
        mapOf(
            "123.4567" to """123.4567""",
        )

    val doubleValues =
        mapOf(
            "123.4567" to """123.45670318603516""",
        )

    val zeroPrecisionDecimalValues =
        mapOf(
            "2" to """2""",
        )

    val tinyintValues =
        mapOf(
            "10" to "10",
            "4" to "4",
            "2" to "2",
        )

    val intValues =
        mapOf(
            "10" to "10",
            "100000000" to "100000000",
            "200000000" to "200000000",
        )

    val dateValues =
        mapOf(
            "'2022-01-01'" to """"2022-01-01"""",
            "'0600-12-02'" to """"0600-12-02"""",
            "'1752-09-09'" to """"1752-09-09"""",
            "NULL" to """"2020-03-30""""
        )

    val timeValues =
        mapOf(
            "'14:30:00'" to """"14:30:00.000000"""",
            "NULL" to """"10:30:00.000000"""",
        )

    val dateTimeValues =
        mapOf(
            "'2024-09-13 14:30:00'" to """"2024-09-13T14:30:00.000000"""",
            "'2024-09-13T14:40:00+00:00'" to """"2024-09-13T14:40:00.000000"""",
            "'1752-09-01 14:30:00'" to """"1752-09-01T14:30:00.000000"""",
            "NULL" to """"2020-03-30T10:30:00.000000"""",
        )

    val timestampValues =
        mapOf(
            "'2024-09-12 14:30:00'" to """"2024-09-12T14:30:00.000000Z"""",
            "CONVERT_TZ('2024-09-12 14:30:00', 'America/Los_Angeles', 'UTC')" to
                """"2024-09-12T21:30:00.000000Z"""",
            "NULL" to """"2020-03-30T10:30:00.000000Z"""",
        )

    val booleanValues =
        mapOf(
            "TRUE" to "true",
            "FALSE" to "false",
            "NULL" to "null",
        )

    val enumValues =
        mapOf(
            "'a'" to """"a"""",
            "'b'" to """"b"""",
            "'c'" to """"c"""",
        )

    // Encoded into base64
    val binaryValues =
        mapOf(
            "X'89504E470D0A1A0A0000000D49484452'" to """"iVBORw0KGgoAAAANSUhEUg=="""",
        )

    override val testCases: Map<String, MySqlSourceDatatypeTestCase> =
        listOf(
                MySqlSourceDatatypeTestCase(
                    "BOOLEAN",
                    booleanValues,
                    LeafAirbyteSchemaType.BOOLEAN,
                ),
                MySqlSourceDatatypeTestCase(
                    "VARCHAR(10)",
                    stringValues,
                    LeafAirbyteSchemaType.STRING,
                ),
                MySqlSourceDatatypeTestCase(
                    "DECIMAL(60,4)",
                    bigDecimalValues,
                    LeafAirbyteSchemaType.NUMBER,
                ),
                MySqlSourceDatatypeTestCase(
                    "DECIMAL(60,0)",
                    bigIntegerValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlSourceDatatypeTestCase(
                    "DECIMAL(10,1)",
                    decimalValues,
                    LeafAirbyteSchemaType.NUMBER,
                ),
                MySqlSourceDatatypeTestCase(
                    "DECIMAL(10,1) UNSIGNED",
                    decimalValues,
                    LeafAirbyteSchemaType.NUMBER,
                ),
                MySqlSourceDatatypeTestCase(
                    "DECIMAL UNSIGNED",
                    zeroPrecisionDecimalValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlSourceDatatypeTestCase("FLOAT", floatValues, LeafAirbyteSchemaType.NUMBER),
                MySqlSourceDatatypeTestCase(
                    "FLOAT(34)",
                    floatValues,
                    LeafAirbyteSchemaType.NUMBER,
                ),
                MySqlSourceDatatypeTestCase(
                    "FLOAT(7,4)",
                    floatValues,
                    LeafAirbyteSchemaType.NUMBER,
                    isGlobal = false // 123.4567 renders as 123.45670318603516 with CDC, which is OK
                ),
                MySqlSourceDatatypeTestCase(
                    "FLOAT(53,8)",
                    floatValues,
                    LeafAirbyteSchemaType.NUMBER,
                    // Disable CDC testing for this case:
                    //  - 123.4567 is rendered as 123.45670318603516
                    //    not strictly equal due to IEEE754 encoding artifacts, but acceptable.
                    isGlobal = false,
                ),
                MySqlSourceDatatypeTestCase(
                    "FLOAT(53,8)",
                    doubleValues,
                    LeafAirbyteSchemaType.NUMBER,
                ),
                MySqlSourceDatatypeTestCase("DOUBLE", decimalValues, LeafAirbyteSchemaType.NUMBER),
                MySqlSourceDatatypeTestCase(
                    "DOUBLE UNSIGNED",
                    decimalValues,
                    LeafAirbyteSchemaType.NUMBER,
                ),
                MySqlSourceDatatypeTestCase(
                    "TINYINT",
                    tinyintValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlSourceDatatypeTestCase(
                    "TINYINT UNSIGNED",
                    tinyintValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlSourceDatatypeTestCase(
                    "SMALLINT",
                    tinyintValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlSourceDatatypeTestCase(
                    "MEDIUMINT",
                    tinyintValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlSourceDatatypeTestCase("BIGINT", intValues, LeafAirbyteSchemaType.INTEGER),
                MySqlSourceDatatypeTestCase(
                    "SMALLINT UNSIGNED",
                    tinyintValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlSourceDatatypeTestCase(
                    "MEDIUMINT UNSIGNED",
                    tinyintValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlSourceDatatypeTestCase(
                    "BIGINT UNSIGNED",
                    intValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlSourceDatatypeTestCase("INT", intValues, LeafAirbyteSchemaType.INTEGER),
                MySqlSourceDatatypeTestCase(
                    "INT UNSIGNED",
                    intValues,
                    LeafAirbyteSchemaType.INTEGER,
                ),
                MySqlSourceDatatypeTestCase(
                    "DATE NOT NULL DEFAULT '2020-03-30'",
                    dateValues,
                    LeafAirbyteSchemaType.DATE,
                ),
                MySqlSourceDatatypeTestCase(
                    "TIMESTAMP NOT NULL DEFAULT '2020-03-30 10:30:00'",
                    timestampValues,
                    LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
                ),
                MySqlSourceDatatypeTestCase(
                    "DATETIME(3) NOT NULL DEFAULT '2020-03-30 10:30:00'",
                    dateTimeValues,
                    LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
                ),
                MySqlSourceDatatypeTestCase(
                    "TIME NOT NULL DEFAULT '10:30:00'",
                    timeValues,
                    LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE,
                ),
                MySqlSourceDatatypeTestCase("YEAR", yearValues, LeafAirbyteSchemaType.INTEGER),
                MySqlSourceDatatypeTestCase(
                    "VARBINARY(255)",
                    binaryValues,
                    LeafAirbyteSchemaType.BINARY,
                ),
                MySqlSourceDatatypeTestCase(
                    "BIT",
                    bitValues,
                    LeafAirbyteSchemaType.BOOLEAN,
                ),
                MySqlSourceDatatypeTestCase(
                    "BIT(8)",
                    multiBitValues,
                    LeafAirbyteSchemaType.BINARY,
                ),
                MySqlSourceDatatypeTestCase(
                    "JSON",
                    jsonValues,
                    LeafAirbyteSchemaType.JSONB,
                    isGlobal = false // different, more compact rendering with CDC, which is OK
                ),
                MySqlSourceDatatypeTestCase(
                    "ENUM('a', 'b', 'c')",
                    enumValues,
                    LeafAirbyteSchemaType.STRING,
                ),
            )
            .associateBy { it.id }
}

data class MySqlSourceDatatypeTestCase(
    val sqlType: String,
    val sqlToAirbyte: Map<String, String>,
    override val expectedAirbyteSchemaType: AirbyteSchemaType,
    override val isGlobal: Boolean = true,
) : DatatypeTestCase {

    override val isStream: Boolean
        get() = true

    private val typeName: String
        get() =
            sqlType
                .replace("[^a-zA-Z0-9]".toRegex(), " ")
                .trim()
                .replace(" +".toRegex(), "_")
                .lowercase()

    override val id: String
        get() = "tbl_$typeName"

    override val fieldName: String
        get() = "col_$typeName"

    override val expectedData: List<String>
        get() = sqlToAirbyte.values.map { """{"${fieldName}":$it}""" }

    val ddl: List<String>
        get() =
            listOf(
                "CREATE TABLE IF NOT EXISTS $id " +
                    "(pk INT AUTO_INCREMENT, $fieldName $sqlType, PRIMARY KEY (pk))",
                "TRUNCATE TABLE $id",
            )

    val dml: List<String>
        get() =
            sqlToAirbyte.keys.map {
                if (it == "NULL") {
                    "INSERT INTO $id VALUES ()"
                } else {
                    "INSERT INTO $id ($fieldName) VALUES ($it)"
                }
            }
}
