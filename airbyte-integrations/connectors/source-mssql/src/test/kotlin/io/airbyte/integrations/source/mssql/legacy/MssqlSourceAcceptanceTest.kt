/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.mssql.legacy

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.google.common.collect.Iterables
import com.google.common.collect.Lists
import io.airbyte.cdk.test.fixtures.legacy.Jsons
import io.airbyte.cdk.test.fixtures.legacy.SourceAcceptanceTest
import io.airbyte.cdk.test.fixtures.legacy.SshHelpers
import io.airbyte.cdk.test.fixtures.legacy.TestDestinationEnv
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.*
import org.junit.Assert
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import java.sql.SQLException
import java.util.*
import java.util.stream.Collectors

open class MssqlSourceAcceptanceTest : SourceAcceptanceTest() {
    @JvmField
    protected var testdb: MsSQLTestDatabase? = null

    @Throws(SQLException::class)
    override open fun setupEnvironment(environment: TestDestinationEnv?) {
        testdb = MsSQLTestDatabase.`in`(MsSQLTestDatabase.BaseImage.MSSQL_2022)
            .with("CREATE TABLE %s.%s (id INTEGER, name VARCHAR(200), born DATETIMEOFFSET(7));", SCHEMA_NAME, STREAM_NAME)
            .with("CREATE TABLE %s.%s(id INTEGER PRIMARY KEY, name VARCHAR(200));", SCHEMA_NAME, STREAM_NAME2)
            .with(
                "INSERT INTO id_and_name (id, name, born) VALUES " +
                        "(1, 'picard', '2124-03-04T01:01:01Z'), " +
                        "(2, 'crusher', '2124-03-04T01:01:01Z'), " +
                        "(3, 'vash', '2124-03-04T01:01:01Z');"
            )
            .with("INSERT INTO %s.%s (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato'), (4, 'Argo');", SCHEMA_NAME, STREAM_NAME2)
            .with("CREATE TABLE %s.%s (id INTEGER PRIMARY KEY, name VARCHAR(200), userid INTEGER DEFAULT NULL);", SCHEMA_NAME, STREAM_NAME3)
            .with("INSERT INTO %s.%s (id, name) VALUES (4,'voyager');", SCHEMA_NAME, STREAM_NAME3)
    }

    override fun tearDown(testEnv: TestDestinationEnv?) {
        testdb!!.close()
    }

    override val imageName: String
        get() = "airbyte/source-mssql:dev"

    @get:Throws(Exception::class)
    override val spec: ConnectorSpecification
        get() = SshHelpers.specAndInjectSsh

    override open val config: JsonNode?
        get() = testdb!!.integrationTestConfigBuilder()
            .withoutSsl()
            .build()

    override val configuredCatalog: ConfiguredAirbyteCatalog
        get() = ConfiguredAirbyteCatalog().withStreams(
            Lists.newArrayList(
                ConfiguredAirbyteStream()
                    .withSyncMode(SyncMode.INCREMENTAL)
                    .withCursorField(Lists.newArrayList("id"))
                    .withDestinationSyncMode(DestinationSyncMode.APPEND)
                    .withStream(
                        CatalogHelpers.createAirbyteStream(
                            STREAM_NAME, SCHEMA_NAME,
                            Field.of("id", JsonSchemaType.NUMBER),
                            Field.of("name", JsonSchemaType.STRING)
                        )
                            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
                    ),
                ConfiguredAirbyteStream()
                    .withSyncMode(SyncMode.INCREMENTAL)
                    .withCursorField(Lists.newArrayList("id"))
                    .withDestinationSyncMode(DestinationSyncMode.APPEND)
                    .withStream(
                        CatalogHelpers.createAirbyteStream(
                            STREAM_NAME2, SCHEMA_NAME,
                            Field.of("id", JsonSchemaType.NUMBER),
                            Field.of("name", JsonSchemaType.STRING)
                        )
                            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
                    )
            )
        )

    override val state: JsonNode
        get() = Jsons.jsonNode<Any>(mapOf<Any, Any>())

    @Test
    @Throws(Exception::class)
    protected fun testAddNewStreamToExistingSync() {
        val configuredAirbyteStreams: List<ConfiguredAirbyteStream> =
            Lists.newArrayList(
                CatalogHelpers.createConfiguredAirbyteStream(
                    STREAM_NAME,
                    SCHEMA_NAME,
                    Field.of("id", JsonSchemaType.NUMBER),
                    Field.of("name", JsonSchemaType.STRING)
                )
                    .withDestinationSyncMode(DestinationSyncMode.APPEND)
                    .withSyncMode(SyncMode.INCREMENTAL)
                    .withCursorField(listOf("id")),
                CatalogHelpers.createConfiguredAirbyteStream(
                    STREAM_NAME2,
                    SCHEMA_NAME,
                    Field.of("id", JsonSchemaType.NUMBER),
                    Field.of("name", JsonSchemaType.STRING)
                )
                    .withDestinationSyncMode(DestinationSyncMode.APPEND)
                    .withSyncMode(SyncMode.INCREMENTAL)
                    .withCursorField(listOf("id"))
            )
        val configuredCatalogWithOneStream =
            ConfiguredAirbyteCatalog().withStreams(
                java.util.List.of(
                    configuredAirbyteStreams[0]
                )
            )

        // Start a sync with one stream
        val messages: List<AirbyteMessage> = runRead(withSourceDefinedCursors(configuredCatalogWithOneStream))
        val recordMessages: List<AirbyteRecordMessage> = filterRecords(messages)
        val stateMessages = filterStateMessages(messages)
        val lastStateMessage = Iterables.getLast(stateMessages)
        val streamState = lastStateMessage.stream

        Assert.assertEquals(3, recordMessages.size.toLong())
        Assert.assertEquals(1, stateMessages.size.toLong())
        Assert.assertEquals(STREAM_NAME, streamState.streamDescriptor.name)
        Assert.assertEquals(SCHEMA_NAME, streamState.streamDescriptor.namespace)

        val configuredCatalogWithTwoStreams =
            ConfiguredAirbyteCatalog().withStreams(configuredAirbyteStreams)

        // Start another sync with a newly added stream
        val messages2: List<AirbyteMessage> = runRead(configuredCatalogWithTwoStreams, Jsons.jsonNode(java.util.List.of(lastStateMessage)))
        val recordMessages2: List<AirbyteRecordMessage> = filterRecords(messages2)
        val stateMessages2 = filterStateMessages(messages2)

        Assert.assertEquals(4, recordMessages2.size.toLong())
        Assert.assertEquals(2, stateMessages2.size.toLong())

        Assert.assertEquals(2, stateMessages2.size.toLong())
        Assert.assertEquals(STREAM_NAME, stateMessages2[0].stream.streamDescriptor.name)
        Assert.assertEquals(SCHEMA_NAME, stateMessages2[0].stream.streamDescriptor.namespace)
        Assert.assertEquals(STREAM_NAME2, stateMessages2[1].stream.streamDescriptor.name)
        Assert.assertEquals(SCHEMA_NAME, stateMessages2[1].stream.streamDescriptor.namespace)
    }

    @Test
    @Throws(Exception::class)
    protected fun testNullValueConversion() {
        val configuredAirbyteStreams: List<ConfiguredAirbyteStream> =
            Lists.newArrayList(
                CatalogHelpers.createConfiguredAirbyteStream(
                    STREAM_NAME3,
                    SCHEMA_NAME,
                    Field.of("id", JsonSchemaType.NUMBER),
                    Field.of("name", JsonSchemaType.STRING),
                    Field.of("userid", JsonSchemaType.NUMBER)
                )
                    .withDestinationSyncMode(DestinationSyncMode.APPEND)
                    .withSyncMode(SyncMode.INCREMENTAL)
                    .withCursorField(listOf("id"))
            )
        val configuredCatalogWithOneStream =
            ConfiguredAirbyteCatalog().withStreams(
                java.util.List.of(
                    configuredAirbyteStreams[0]
                )
            )

        val airbyteMessages: List<AirbyteMessage> = runRead(configuredCatalogWithOneStream, state)
        val recordMessages: List<AirbyteRecordMessage> = filterRecords(airbyteMessages)
        val stateMessages = airbyteMessages
            .stream()
            .filter { m: AirbyteMessage -> m.type == AirbyteMessage.Type.STATE }
            .map { obj: AirbyteMessage -> obj.state }
            .collect(Collectors.toList())
        Assert.assertEquals(recordMessages.size.toLong(), 1)
        Assertions.assertFalse(stateMessages.isEmpty(), "Reason")
        val mapper = ObjectMapper()

        Assertions.assertEquals(mapper.readTree("{\"id\":4, \"name\":\"voyager\", \"userid\":null}}"), recordMessages[0].data)

        // when we run incremental sync again there should be no new records. Run a sync with the latest
        // state message and assert no records were emitted.
        val latestState: JsonNode? = extractLatestState(stateMessages)

        testdb!!.database.query { c -> c.query("INSERT INTO %s.%s (id, name) VALUES (5,'deep space nine');".formatted(SCHEMA_NAME, STREAM_NAME3)) }!!
            .execute()

        assert(Objects.nonNull(latestState))
        val secondSyncRecords: List<AirbyteRecordMessage> = filterRecords(runRead(configuredCatalogWithOneStream, latestState))
        Assertions.assertFalse(
            secondSyncRecords.isEmpty(),
            "Expected the second incremental sync to produce records."
        )
        Assertions.assertEquals(mapper.readTree("{\"id\":5, \"name\":\"deep space nine\", \"userid\":null}}"), secondSyncRecords[0].data)
    }

    private fun filterStateMessages(messages: List<AirbyteMessage>): List<AirbyteStateMessage> {
        return messages.stream().filter { r: AirbyteMessage -> r.type == AirbyteMessage.Type.STATE }
            .map { obj: AirbyteMessage -> obj.state }
            .collect(Collectors.toList())
    }

    companion object {
        @JvmStatic protected val SCHEMA_NAME: String = "dbo"
        @JvmStatic protected val STREAM_NAME: String = "id_and_name"
        @JvmStatic protected val STREAM_NAME2: String = "starships"
        @JvmStatic protected val STREAM_NAME3: String = "stream3"
    }
}
