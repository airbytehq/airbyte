/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.mssql.legacy

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.google.common.collect.Iterables
import com.google.common.collect.Lists
import io.airbyte.cdk.test.fixtures.legacy.Jsons.jsonNode
import io.airbyte.cdk.test.fixtures.legacy.SourceAcceptanceTest
import io.airbyte.cdk.test.fixtures.legacy.SshHelpers.specAndInjectSsh
import io.airbyte.cdk.test.fixtures.legacy.TestDestinationEnv
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.Companion.`in`
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.*
import org.jooq.DSLContext
import org.junit.Assert
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestInstance
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode
import java.util.*
import java.util.stream.Collectors

@TestInstance(TestInstance.Lifecycle.PER_METHOD)
@Execution(ExecutionMode.CONCURRENT)
class CdcMssqlSourceAcceptanceTest : SourceAcceptanceTest() {
    private var testdb: MsSQLTestDatabase? = null

    override val imageName: String
        get() = "airbyte/source-mssql:dev"

    @get:Throws(Exception::class)
    override val spec: ConnectorSpecification
        get() = specAndInjectSsh

    override val config: JsonNode
        get() = testdb!!.integrationTestConfigBuilder()
            .withCdcReplication()
            .withoutSsl()
            .build()

    override val configuredCatalog: ConfiguredAirbyteCatalog
        get() = ConfiguredAirbyteCatalog().withStreams(configuredAirbyteStreams)

    protected val configuredAirbyteStreams: List<ConfiguredAirbyteStream>
        get() = Lists.newArrayList(
            ConfiguredAirbyteStream()
                .withSyncMode(SyncMode.INCREMENTAL)
                .withDestinationSyncMode(DestinationSyncMode.APPEND)
                .withStream(
                    CatalogHelpers.createAirbyteStream(
                        STREAM_NAME, SCHEMA_NAME,
                        Field.of("id", JsonSchemaType.NUMBER),
                        Field.of("name", JsonSchemaType.STRING)
                    )
                        .withSourceDefinedCursor(true)
                        .withSourceDefinedPrimaryKey(java.util.List.of(listOf("id")))
                        .withSupportedSyncModes(
                            Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
                        )
                ),
            ConfiguredAirbyteStream()
                .withSyncMode(SyncMode.INCREMENTAL)
                .withDestinationSyncMode(DestinationSyncMode.APPEND)
                .withStream(
                    CatalogHelpers.createAirbyteStream(
                        STREAM_NAME2, SCHEMA_NAME,
                        Field.of("id", JsonSchemaType.NUMBER),
                        Field.of("name", JsonSchemaType.STRING)
                    )
                        .withSourceDefinedCursor(true)
                        .withSourceDefinedPrimaryKey(java.util.List.of(listOf("id")))
                        .withSupportedSyncModes(
                            Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
                        )
                )
        )

    override val state: JsonNode?
        get() = null

    override fun setupEnvironment(environment: TestDestinationEnv?) {
        testdb = `in`(MsSQLTestDatabase.BaseImage.MSSQL_2022, MsSQLTestDatabase.ContainerModifier.AGENT)
        testdb!!
            .withWaitUntilAgentRunning()
            .withCdc() // create tables
            .with("CREATE TABLE %s.%s(id INTEGER PRIMARY KEY, name VARCHAR(200));", SCHEMA_NAME, STREAM_NAME)
            .with("CREATE TABLE %s.%s(id INTEGER PRIMARY KEY, name VARCHAR(200));", SCHEMA_NAME, STREAM_NAME2)
            .with(
                "CREATE TABLE %s.%s (id INTEGER PRIMARY KEY, name VARCHAR(200), userid INTEGER DEFAULT NULL);",
                SCHEMA_NAME,
                STREAM_NAME3
            ) // populate tables
            .with("INSERT INTO %s.%s (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');", SCHEMA_NAME, STREAM_NAME)
            .with("INSERT INTO %s.%s (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');", SCHEMA_NAME, STREAM_NAME2)
            .with("INSERT INTO %s.%s (id, name) VALUES (4,'voyager');", SCHEMA_NAME, STREAM_NAME3) // enable cdc on tables for designated role
            .withCdcForTable(SCHEMA_NAME, STREAM_NAME, CDC_ROLE_NAME)
            .withCdcForTable(SCHEMA_NAME, STREAM_NAME2, CDC_ROLE_NAME)
            .withCdcForTable(SCHEMA_NAME, STREAM_NAME3, CDC_ROLE_NAME) // revoke user permissions
            .with("REVOKE ALL FROM %s CASCADE;", testdb!!.userName)
            .with("EXEC sp_msforeachtable \"REVOKE ALL ON '?' TO %s;\"", testdb!!.userName) // grant user permissions
            .with("EXEC sp_addrolemember N'%s', N'%s';", "db_datareader", testdb!!.userName)
            .with("GRANT SELECT ON SCHEMA :: [cdc] TO %s", testdb!!.userName)
            .with("EXEC sp_addrolemember N'%s', N'%s';", CDC_ROLE_NAME, testdb!!.userName)
            .withWaitUntilMaxLsnAvailable()
    }

    override fun tearDown(testEnv: TestDestinationEnv?) {
        testdb!!.close()
    }

    @Test
    @Throws(Exception::class)
    fun testAddNewStreamToExistingSync() {
        val configuredCatalogWithOneStream =
            ConfiguredAirbyteCatalog().withStreams(
                java.util.List.of(
                    configuredAirbyteStreams[0]
                )
            )

        // Start a sync with one stream
        val messages = runRead(configuredCatalogWithOneStream)
        val recordMessages = filterRecords(messages)
        val stateMessages = filterStateMessages(messages)
        val streamStates = stateMessages[0].global.streamStates

        Assertions.assertEquals(3, recordMessages.size)
        Assertions.assertEquals(2, stateMessages.size)
        Assertions.assertEquals(1, streamStates.size)
        Assertions.assertEquals(STREAM_NAME, streamStates[0].streamDescriptor.name)
        Assertions.assertEquals(SCHEMA_NAME, streamStates[0].streamDescriptor.namespace)

        val lastStateMessage = Iterables.getLast(stateMessages)

        val configuredCatalogWithTwoStreams = configuredCatalogWithOneStream.withStreams(configuredAirbyteStreams)

        // Start another sync with a newly added stream
        val messages2 = runRead(configuredCatalogWithTwoStreams, jsonNode(java.util.List.of(lastStateMessage)))
        val recordMessages2 = filterRecords(messages2)
        val stateMessages2 = filterStateMessages(messages2)

        Assertions.assertEquals(3, recordMessages2.size)
        Assertions.assertEquals(2, stateMessages2.size)

        val lastStateMessage2 = Iterables.getLast(stateMessages2)
        val streamStates2 = lastStateMessage2.global.streamStates

        Assertions.assertEquals(2, streamStates2.size)

        Assertions.assertEquals(STREAM_NAME, streamStates2[0].streamDescriptor.name)
        Assertions.assertEquals(SCHEMA_NAME, streamStates2[0].streamDescriptor.namespace)
        Assertions.assertEquals(STREAM_NAME2, streamStates2[1].streamDescriptor.name)
        Assertions.assertEquals(SCHEMA_NAME, streamStates2[1].streamDescriptor.namespace)
    }

    private fun filterStateMessages(messages: List<AirbyteMessage>): List<AirbyteStateMessage> {
        return messages.stream().filter { r: AirbyteMessage -> r.type == AirbyteMessage.Type.STATE }
            .map { obj: AirbyteMessage -> obj.state }
            .collect(Collectors.toList())
    }

    @Test
    @Throws(Exception::class)
    protected fun testNullValueConversion() {
        val configuredAirbyteStreams: List<ConfiguredAirbyteStream> =
            Lists.newArrayList(
                ConfiguredAirbyteStream()
                    .withSyncMode(SyncMode.INCREMENTAL)
                    .withDestinationSyncMode(DestinationSyncMode.APPEND)
                    .withStream(
                        CatalogHelpers.createAirbyteStream(
                            STREAM_NAME3,
                            SCHEMA_NAME,
                            Field.of("id", JsonSchemaType.NUMBER),
                            Field.of("name", JsonSchemaType.STRING),
                            Field.of("userid", JsonSchemaType.NUMBER)
                        )
                            .withSourceDefinedCursor(true)
                            .withSourceDefinedPrimaryKey(java.util.List.of(listOf("id")))
                            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
                    )
            )

        val configuredCatalogWithOneStream =
            ConfiguredAirbyteCatalog().withStreams(
                java.util.List.of(
                    configuredAirbyteStreams[0]
                )
            )

        val airbyteMessages = runRead(configuredCatalogWithOneStream, state)
        val recordMessages = filterRecords(airbyteMessages)
        val stateMessages = airbyteMessages
            .stream()
            .filter { m: AirbyteMessage -> m.type == AirbyteMessage.Type.STATE }
            .map { obj: AirbyteMessage -> obj.state }
            .collect(Collectors.toList())
        Assert.assertEquals(recordMessages.size.toLong(), 1)
        Assertions.assertFalse(stateMessages.isEmpty(), "Reason")
        val mapper = ObjectMapper()

        Assertions.assertTrue(cdcFieldsOmitted(recordMessages[0].data) == mapper.readTree("{\"id\":4, \"name\":\"voyager\", \"userid\":null}"))

        // when we run incremental sync again there should be no new records. Run a sync with the latest
        // state message and assert no records were emitted.
        val latestState = extractLatestState(stateMessages)

        testdb!!.database.query { c: DSLContext ->
            c.query(
                "INSERT INTO %s.%s (id, name) VALUES (5,'deep space nine')".formatted(
                    SCHEMA_NAME,
                    STREAM_NAME3
                )
            )
        }
            .execute()

        assert(Objects.nonNull(latestState))
        val secondSyncRecords = filterRecords(runRead(configuredCatalogWithOneStream, latestState))
        Assertions.assertFalse(
            secondSyncRecords.isEmpty(),
            "Expected the second incremental sync to produce records."
        )
        Assertions.assertEquals(
            cdcFieldsOmitted(secondSyncRecords[0].data),
            mapper.readTree("{\"id\":5, \"name\":\"deep space nine\", \"userid\":null}")
        )
    }

    private fun cdcFieldsOmitted(node: JsonNode): JsonNode {
        val mapper = ObjectMapper()
        val `object` = mapper.createObjectNode()
        node.fieldNames().forEachRemaining { name: String ->
            if (!name.lowercase(Locale.getDefault()).startsWith("_ab_cdc_")) {
                `object`.put(name, node[name])
            }
        }
        return `object`
    }

    @Test
    override fun testFullRefreshRead() {
        super.testFullRefreshRead()
    }

    companion object {
        private const val SCHEMA_NAME = "dbo"
        private const val STREAM_NAME = "id_and_name"
        private const val STREAM_NAME2 = "starships"
        private const val CDC_ROLE_NAME = "cdc_selector"
        private const val STREAM_NAME3 = "stream3"
    }
}
