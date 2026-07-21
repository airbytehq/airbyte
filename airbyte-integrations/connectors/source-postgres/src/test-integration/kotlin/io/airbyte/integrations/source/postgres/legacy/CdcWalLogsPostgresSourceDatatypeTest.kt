/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.legacy

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.test.fixtures.legacy.Database
import io.airbyte.cdk.test.fixtures.legacy.Jsons.jsonNode
import io.airbyte.cdk.test.fixtures.legacy.TestDataHolder
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import java.util.function.Consumer
import org.jooq.DSLContext

class CdcWalLogsPostgresSourceDatatypeTest : AbstractPostgresSourceDatatypeTest() {
    private var stateAfterFirstSync: JsonNode? = null

    override val nameSpace: String
        get() = SCHEMA_NAME

    @Throws(Exception::class)
    protected override fun runRead(
        configuredCatalog: ConfiguredAirbyteCatalog?
    ): List<AirbyteMessage> {
        if (stateAfterFirstSync == null) {
            throw RuntimeException("stateAfterFirstSync is null")
        }
        return super.runRead(configuredCatalog, stateAfterFirstSync, imageName)
    }

    @Throws(Exception::class)
    override fun postSetup() {
        val database: Database = setupDatabase()
        for (test in testDataHolders) {
            database.query<Any?> { ctx: DSLContext ->
                ctx.fetch(test.createSqlQuery)
                null
            }
        }

        val dummyTableWithData: ConfiguredAirbyteStream? = createDummyTableWithData(database)
        val catalog: ConfiguredAirbyteCatalog = configuredCatalog
        catalog.getStreams().add(dummyTableWithData)

        val allMessages: List<AirbyteMessage> = super.runRead(catalog)
        val stateAfterFirstBatch: List<AirbyteStateMessage?> = extractStateMessages(allMessages)
        if (stateAfterFirstBatch.isEmpty()) {
            throw RuntimeException("stateAfterFirstBatch should not be null or empty")
        }
        stateAfterFirstSync =
            jsonNode<MutableList<AirbyteStateMessage?>?>(
                mutableListOf<AirbyteStateMessage?>(
                    stateAfterFirstBatch.get(stateAfterFirstBatch.size - 1)
                ),
            )
        if (stateAfterFirstSync == null) {
            throw RuntimeException("stateAfterFirstSync should not be null")
        }
        for (test in testDataHolders) {
            database.query<Any?>({ ctx: DSLContext? ->
                test.insertSqlQueries.forEach(Consumer { sql: String? -> ctx!!.fetch(sql) })
                null
            },)
        }
    }

    override fun setupDatabase(): Database {
        testdb =
            PostgresTestDatabase.`in`(
                    PostgresTestDatabase.BaseImage.POSTGRES_17,
                    PostgresTestDatabase.ContainerModifier.CONF
                )
                .with("CREATE EXTENSION hstore;")
                .with("CREATE SCHEMA $nameSpace;")
                .with("CREATE TYPE mood AS ENUM ('sad', 'ok', 'happy');")
                .with(
                    ("CREATE TYPE inventory_item AS (\n" +
                        "    name            text,\n" +
                        "    supplier_id     integer,\n" +
                        "    price           numeric\n" +
                        ");"),
                )
                .with("SET TIMEZONE TO 'MST'")
                .withReplicationSlot()
                .withPublicationForAllTables()
        return testdb.database
    }

    @get:Throws(Exception::class)
    override val config: JsonNode
        get() =
            testdb
                .integrationTestConfigBuilder()
                .withSchemas(nameSpace)
                .withoutSsl()
                .withCdcReplication()
                .build()

    protected override fun addMoneyTest() {
        addDataTypeTestData(
            TestDataHolder.builder()
                .sourceType("money")
                .airbyteType(JsonSchemaType.NUMBER)
                .addInsertValues(
                    "null",
                    "'999.99'",
                    "'1,001.01'",
                    "'-1,000'",
                    "'$999.99'",
                    "'$1001.01'",
                    "'-$1,000'", // max values for Money type: "-92233720368547758.08",
                    // "92233720368547758.07"
                    // Debezium has wrong parsing for values more than 999999999999999 and less than
                    // -999999999999999
                    // https://github.com/airbytehq/airbyte/issues/7338
                    /* "'-92233720368547758.08'", "'92233720368547758.07'" */
                    )
                .addExpectedValues(
                    null,
                    "999.99",
                    "1001.01",
                    "-1000.00",
                    "999.99",
                    "1001.01",
                    "-1000.00", /* "-92233720368547758.08", "92233720368547758.07" */
                )
                .build(),
        )
    }

    protected override fun addTimeWithTimeZoneTest() {
        // time with time zone
        for (fullSourceType in mutableSetOf<String?>("timetz", "time with time zone")) {
            addDataTypeTestData(
                TestDataHolder.builder()
                    .sourceType("timetz")
                    .fullSourceDataType(fullSourceType)
                    .airbyteType(JsonSchemaType.STRING_TIME_WITH_TIMEZONE)
                    .addInsertValues(
                        "null",
                        "'13:00:01'",
                        "'13:00:00+8'",
                        "'13:00:03-8'",
                        "'13:00:04Z'",
                        "'13:00:05.012345Z+8'",
                        "'13:00:06.00000Z-8'",
                    ) // A time value without time zone will use the time zone set on the database,
                    // which is Z-7,
                    // so 13:00:01 is returned as 13:00:01-07.
                    .addExpectedValues(
                        null,
                        "20:00:01Z",
                        "05:00:00.000000Z",
                        "21:00:03Z",
                        "13:00:04Z",
                        "21:00:05.012345Z",
                        "05:00:06Z",
                    )
                    .build(),
            )
        }
    }

    protected override fun addNumericValuesTest() {
        addDataTypeTestData(
            TestDataHolder.builder()
                .sourceType("numeric")
                .fullSourceDataType("NUMERIC(28,2)")
                .airbyteType(JsonSchemaType.NUMBER)
                .addInsertValues(
                    "'123'",
                    "null",
                    "'14525.22'",
                ) // Postgres source does not support these special values yet
                // https://github.com/airbytehq/airbyte/issues/8902
                // "'infinity'", "'-infinity'", "'nan'"
                .addExpectedValues("123", null, "14525.22")
                .build(),
        )

        // Blocked by https://github.com/airbytehq/airbyte/issues/8902
        for (type in mutableSetOf<String?>("numeric", "decimal")) {
            addDataTypeTestData(
                TestDataHolder.builder()
                    .sourceType(type)
                    .fullSourceDataType("NUMERIC(20,7)")
                    .airbyteType(JsonSchemaType.NUMBER)
                    .addInsertValues(
                        "'123'",
                        "null",
                        "'1234567890.1234567'",
                    ) // Postgres source does not support these special values yet
                    // https://github.com/airbytehq/airbyte/issues/8902
                    // "'infinity'", "'-infinity'", "'nan'"
                    .addExpectedValues("123", null, "1.2345678901234567E9")
                    .build(),
            )
        }
    }

    companion object {
        val SCHEMA_NAME: String = "cdc_wal_log_postgres_source_datatype_test"
    }
}
