/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.jdbc.test

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.ImmutableMap
import com.google.common.collect.Lists
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.db.factory.DataSourceFactory.create
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.source.jdbc.AbstractJdbcSource
import io.airbyte.commons.functional.CheckedConsumer
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.stream.MoreStreams
import io.airbyte.commons.string.Strings
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.*
import io.github.oshai.kotlinlogging.KotlinLogging
import java.math.BigDecimal
import java.sql.Connection
import java.util.*
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

private val LOGGER = KotlinLogging.logger {}

/**
 * Runs a "large" amount of data through a JdbcSource to ensure that it streams / chunks records.
 */
// todo (cgardens) - this needs more love and thought. we should be able to test this without having
// to rewrite so much data. it is enough for now to sanity check that our JdbcSources can actually
// handle more data than fits in memory.
@SuppressFBWarnings(
    value = ["MS_SHOULD_BE_FINAL"],
    justification =
        "The static variables are updated in sub classes for convenience, and cannot be final."
)
abstract class JdbcStressTest {
    private var bitSet: BitSet? = null
    private lateinit var config: JsonNode
    private var source: AbstractJdbcSource<*>? = null

    /**
     * These tests write records without specifying a namespace (schema name). They will be written
     * into whatever the default schema is for the database. When they are discovered they will be
     * namespaced by the schema name (e.g. <default-schema-name>.<table_name>). Thus the source
     * needs to tell the tests what that default schema name is. If the database does not support
     * schemas, then database name should used instead.
     *
     * @return name that will be used to namespace the record. </table_name></default-schema-name>
     */
    abstract val defaultSchemaName: Optional<String>

    /**
     * A valid configuration to connect to a test database.
     *
     * @return config
     */
    abstract fun getConfig(): JsonNode

    /**
     * Full qualified class name of the JDBC driver for the database.
     *
     * @return driver
     */
    abstract val driverClass: String

    /**
     * An instance of the source that should be tests.
     *
     * @return source
     */
    abstract fun getSource(): AbstractJdbcSource<*>?

    protected fun createTableQuery(tableName: String?, columnClause: String?): String {
        return String.format("CREATE TABLE %s(%s)", tableName, columnClause)
    }

    @Throws(Exception::class)
    open fun setup() {
        LOGGER.info("running for driver:" + driverClass)
        bitSet = BitSet(TOTAL_RECORDS.toInt())

        source = getSource()
        streamName =
            defaultSchemaName.map { `val`: String -> `val` + "." + TABLE_NAME }.orElse(TABLE_NAME)
        config = getConfig()

        val jdbcConfig = source!!.toDatabaseConfig(config)
        val database: JdbcDatabase =
            DefaultJdbcDatabase(
                create(
                    jdbcConfig[JdbcUtils.USERNAME_KEY].asText(),
                    if (jdbcConfig.has(JdbcUtils.PASSWORD_KEY))
                        jdbcConfig[JdbcUtils.PASSWORD_KEY].asText()
                    else null,
                    driverClass,
                    jdbcConfig[JdbcUtils.JDBC_URL_KEY].asText()
                )
            )

        database.execute(
            CheckedConsumer { connection: Connection ->
                connection
                    .createStatement()
                    .execute(
                        createTableQuery(
                            "id_and_name",
                            String.format("id %s, name VARCHAR(200)", COL_ID_TYPE)
                        )
                    )
            }
        )
        val batchCount = TOTAL_RECORDS / BATCH_SIZE
        LOGGER.info("writing {} batches of {}", batchCount, BATCH_SIZE)
        for (i in 0 until batchCount) {
            if (i % 1000 == 0L) LOGGER.info("writing batch: $i")
            val insert: MutableList<String> = ArrayList()
            for (j in 0 until BATCH_SIZE) {
                val recordNumber = (i * BATCH_SIZE + j).toInt()
                insert.add(String.format(INSERT_STATEMENT, recordNumber, recordNumber))
            }

            val sql = prepareInsertStatement(insert)
            database.execute(
                CheckedConsumer { connection: Connection ->
                    connection.createStatement().execute(sql)
                }
            )
        }
    }

    // todo (cgardens) - restructure these tests so that testFullRefresh() and testIncremental() can
    // be
    // separate tests. current constrained by only wanting to setup the fixture in the database
    // once,
    // but it is not trivial to move them to @BeforeAll because it is static and we are doing
    // inheritance. Not impossible, just needs to be done thoughtfully and for all JdbcSources.
    @Test
    @Throws(Exception::class)
    fun stressTest() {
        testFullRefresh()
        testIncremental()
    }

    @Throws(Exception::class)
    private fun testFullRefresh() {
        runTest(configuredCatalogFullRefresh, "full_refresh")
    }

    @Throws(Exception::class)
    private fun testIncremental() {
        runTest(configuredCatalogIncremental, "incremental")
    }

    @Throws(Exception::class)
    private fun runTest(configuredCatalog: ConfiguredAirbyteCatalog, testName: String) {
        LOGGER.info("running stress test for: $testName")
        val read: Iterator<AirbyteMessage> =
            source!!.read(config, configuredCatalog, Jsons.jsonNode(emptyMap<Any, Any>()))
        val actualCount =
            MoreStreams.toStream(read)
                .filter { m: AirbyteMessage -> m.type == AirbyteMessage.Type.RECORD }
                .peek { m: AirbyteMessage ->
                    if (m.record.data[COL_ID].asLong() % 100000 == 0L) {
                        LOGGER.info("reading batch: " + m.record.data[COL_ID].asLong() / 1000)
                    }
                }
                .peek { m: AirbyteMessage -> assertExpectedMessage(m) }
                .count()
        val expectedRoundedRecordsCount = TOTAL_RECORDS - TOTAL_RECORDS % 1000
        LOGGER.info("expected records count: " + TOTAL_RECORDS)
        LOGGER.info("actual records count: $actualCount")
        Assertions.assertEquals(expectedRoundedRecordsCount, actualCount, "testing: $testName")
        Assertions.assertEquals(
            expectedRoundedRecordsCount,
            bitSet!!.cardinality().toLong(),
            "testing: $testName"
        )
    }

    // each is roughly 106 bytes.
    private fun assertExpectedMessage(actualMessage: AirbyteMessage) {
        val recordNumber = actualMessage.record.data[COL_ID].asLong()
        bitSet!!.set(recordNumber.toInt())
        actualMessage.record.emittedAt = null

        val expectedRecordNumber: Number =
            if (driverClass.lowercase(Locale.getDefault()).contains("oracle"))
                BigDecimal(recordNumber)
            else recordNumber

        val expectedMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream(streamName)
                        .withData(
                            Jsons.jsonNode(
                                ImmutableMap.of(
                                    COL_ID,
                                    expectedRecordNumber,
                                    COL_NAME,
                                    "picard-$recordNumber"
                                )
                            )
                        )
                )
        Assertions.assertEquals(expectedMessage, actualMessage)
    }

    private fun prepareInsertStatement(inserts: List<String>): String {
        if (driverClass.lowercase(Locale.getDefault()).contains("oracle")) {
            return String.format("INSERT ALL %s SELECT * FROM dual", Strings.join(inserts, " "))
        }
        return String.format(
            "INSERT INTO id_and_name (id, name) VALUES %s",
            Strings.join(inserts, ", ")
        )
    }

    companion object {

        // this will get rounded down to the nearest 1000th.
        private const val TOTAL_RECORDS = 10000000L
        private const val BATCH_SIZE = 1000
        var TABLE_NAME: String = "id_and_name"
        var COL_ID: String = "id"
        var COL_NAME: String = "name"
        var COL_ID_TYPE: String = "BIGINT"
        var INSERT_STATEMENT: String = "(%s,'picard-%s')"

        private var streamName: String? = null

        private val configuredCatalogFullRefresh: ConfiguredAirbyteCatalog
            get() = CatalogHelpers.toDefaultConfiguredCatalog(catalog)

        private val configuredCatalogIncremental: ConfiguredAirbyteCatalog
            get() =
                ConfiguredAirbyteCatalog()
                    .withStreams(
                        listOf(
                            ConfiguredAirbyteStream()
                                .withStream(catalog.streams[0])
                                .withCursorField(listOf(COL_ID))
                                .withSyncMode(SyncMode.INCREMENTAL)
                                .withDestinationSyncMode(DestinationSyncMode.APPEND)
                        )
                    )

        private val catalog: AirbyteCatalog
            get() =
                AirbyteCatalog()
                    .withStreams(
                        Lists.newArrayList(
                            CatalogHelpers.createAirbyteStream(
                                    streamName,
                                    Field.of(COL_ID, JsonSchemaType.NUMBER),
                                    Field.of(COL_NAME, JsonSchemaType.STRING)
                                )
                                .withSupportedSyncModes(
                                    Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
                                )
                        )
                    )
    }
}
