/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.jdbc.test

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.db.factory.DatabaseDriver
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility
import io.airbyte.cdk.integrations.base.Source
import io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils
import io.airbyte.cdk.integrations.source.relationaldb.models.DbState
import io.airbyte.cdk.integrations.source.relationaldb.models.DbStreamState
import io.airbyte.cdk.testutils.TestDatabase
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.resources.MoreResources
import io.airbyte.commons.stream.AirbyteStreamStatusHolder
import io.airbyte.commons.util.MoreIterators
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.*
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.*
import java.math.BigDecimal
import java.sql.SQLException
import java.util.*
import java.util.function.Consumer
import junit.framework.TestCase.assertEquals
import org.hamcrest.MatcherAssert
import org.hamcrest.Matchers
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.Mockito

/** Tests that should be run on all Sources that extend the AbstractJdbcSource. */
@SuppressFBWarnings(
    value = ["MS_SHOULD_BE_FINAL"],
    justification =
        "The static variables are updated in subclasses for convenience, and cannot be final.",
)
abstract class JdbcSourceAcceptanceTest<S : Source, T : TestDatabase<*, T, *>> {
    @JvmField protected var testdb: T = createTestDatabase()

    protected fun streamName(): String {
        return TABLE_NAME
    }

    /**
     * A valid configuration to connect to a test database.
     *
     * @return config
     */
    protected abstract fun config(): JsonNode

    /**
     * An instance of the source that should be tests.
     *
     * @return abstract jdbc source
     */
    protected abstract fun source(): S

    /**
     * Creates a TestDatabase instance to be used in [.setup].
     *
     * @return TestDatabase instance to use for test case.
     */
    protected abstract fun createTestDatabase(): T

    /**
     * These tests write records without specifying a namespace (schema name). They will be written
     * into whatever the default schema is for the database. When they are discovered they will be
     * namespaced by the schema name (e.g. <default-schema-name>.<table_name>). Thus the source
     * needs to tell the tests what that default schema name is. If the database does not support
     * schemas, then database name should used instead.
     *
     * @return name that will be used to namespace the record. </table_name></default-schema-name>
     */
    protected abstract fun supportsSchemas(): Boolean

    protected fun createTableQuery(
        tableName: String?,
        columnClause: String?,
        primaryKeyClause: String
    ): String {
        return String.format(
            "CREATE TABLE %s(%s %s %s)",
            tableName,
            columnClause,
            if (primaryKeyClause == "") "" else ",",
            primaryKeyClause,
        )
    }

    protected fun primaryKeyClause(columns: List<String>): String {
        if (columns.isEmpty()) {
            return ""
        }

        val clause = StringBuilder()
        clause.append("PRIMARY KEY (")
        for (i in columns.indices) {
            clause.append(columns[i])
            if (i != (columns.size - 1)) {
                clause.append(",")
            }
        }
        clause.append(")")
        return clause.toString()
    }

    @BeforeEach
    @Throws(Exception::class)
    open fun setup() {
        testdb = createTestDatabase()
        if (supportsSchemas()) {
            createSchemas()
        }
        if (testdb.databaseDriver == DatabaseDriver.ORACLE) {
            testdb.with("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD'")
        }
        testdb
            ?.with(
                createTableQuery(
                    getFullyQualifiedTableName(TABLE_NAME),
                    COLUMN_CLAUSE_WITH_PK,
                    primaryKeyClause(listOf("id")),
                ),
            )
            ?.with(
                "INSERT INTO %s(id, name, updated_at) VALUES (1, 'picard', '2004-10-19')",
                getFullyQualifiedTableName(TABLE_NAME),
            )
            ?.with(
                "INSERT INTO %s(id, name, updated_at) VALUES (2, 'crusher', '2005-10-19')",
                getFullyQualifiedTableName(TABLE_NAME),
            )
            ?.with(
                "INSERT INTO %s(id, name, updated_at) VALUES (3, 'vash', '2006-10-19')",
                getFullyQualifiedTableName(TABLE_NAME),
            )
            ?.with(
                createTableQuery(
                    getFullyQualifiedTableName(TABLE_NAME_WITHOUT_PK),
                    COLUMN_CLAUSE_WITHOUT_PK,
                    "",
                ),
            )
            ?.with(
                "INSERT INTO %s(id, name, updated_at) VALUES (1, 'picard', '2004-10-19')",
                getFullyQualifiedTableName(TABLE_NAME_WITHOUT_PK),
            )
            ?.with(
                "INSERT INTO %s(id, name, updated_at) VALUES (2, 'crusher', '2005-10-19')",
                getFullyQualifiedTableName(TABLE_NAME_WITHOUT_PK),
            )
            ?.with(
                "INSERT INTO %s(id, name, updated_at) VALUES (3, 'vash', '2006-10-19')",
                getFullyQualifiedTableName(TABLE_NAME_WITHOUT_PK),
            )
            ?.with(
                createTableQuery(
                    getFullyQualifiedTableName(TABLE_NAME_COMPOSITE_PK),
                    COLUMN_CLAUSE_WITH_COMPOSITE_PK,
                    primaryKeyClause(listOf("first_name", "last_name")),
                ),
            )
            ?.with(
                "INSERT INTO %s(first_name, last_name, updated_at) VALUES ('first', 'picard', '2004-10-19')",
                getFullyQualifiedTableName(TABLE_NAME_COMPOSITE_PK),
            )
            ?.with(
                "INSERT INTO %s(first_name, last_name, updated_at) VALUES ('second', 'crusher', '2005-10-19')",
                getFullyQualifiedTableName(TABLE_NAME_COMPOSITE_PK),
            )
            ?.with(
                "INSERT INTO %s(first_name, last_name, updated_at) VALUES ('third', 'vash', '2006-10-19')",
                getFullyQualifiedTableName(TABLE_NAME_COMPOSITE_PK),
            )
    }

    protected open fun maybeSetShorterConnectionTimeout(config: JsonNode?) {
        // Optionally implement this to speed up test cases which will result in a connection
        // timeout.
    }

    protected open fun assertStreamStatusTraceMessageIndex(
        idx: Int,
        allMessages: List<AirbyteMessage>,
        expectedStreamStatus: AirbyteStreamStatusTraceMessage
    ) {
        var actualMessage = allMessages[idx]
        Assertions.assertEquals(AirbyteMessage.Type.TRACE, actualMessage.type)
        var traceMessage = actualMessage.trace
        Assertions.assertNotNull(traceMessage.streamStatus)
        Assertions.assertEquals(expectedStreamStatus, traceMessage.streamStatus)
    }

    fun createAirbteStreanStatusTraceMessage(
        namespace: String,
        streamName: String,
        status: AirbyteStreamStatus
    ): AirbyteStreamStatusTraceMessage {
        return AirbyteStreamStatusTraceMessage()
            .withStreamDescriptor(StreamDescriptor().withNamespace(namespace).withName(streamName))
            .withStatus(status)
    }

    @AfterEach
    fun tearDown() {
        testdb.close()
    }

    @Test
    @Throws(Exception::class)
    open fun testSpec() {
        val actual = source().spec()
        val resourceString = MoreResources.readResource("spec.json")
        val expected = Jsons.deserialize(resourceString, ConnectorSpecification::class.java)

        Assertions.assertEquals(expected, actual)
    }

    @Test
    @Throws(Exception::class)
    fun testCheckSuccess() {
        val actual = source().check(config())
        val expected =
            AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED)
        Assertions.assertEquals(expected, actual)
    }

    @Test
    @Throws(Exception::class)
    protected fun testCheckFailure() {
        val config = config()
        maybeSetShorterConnectionTimeout(config)
        (config as ObjectNode).put(JdbcUtils.PASSWORD_KEY, "fake")
        val actual = source().check(config)
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, actual!!.status)
    }

    @Test
    @Throws(Exception::class)
    fun testDiscover() {
        val actual = filterOutOtherSchemas(source().discover(config()))
        val expected = getCatalog(defaultNamespace)
        Assertions.assertEquals(expected.streams.size, actual.streams.size)
        actual.streams.forEach(
            Consumer { actualStream: AirbyteStream ->
                val expectedStream =
                    expected.streams.firstOrNull { stream: AirbyteStream ->
                        stream.namespace == actualStream.namespace &&
                            stream.name == actualStream.name
                    }
                Assertions.assertTrue(
                    expectedStream != null,
                    String.format("Unexpected stream %s", actualStream.name),
                )
                Assertions.assertEquals(expectedStream, actualStream)
            }
        )
    }

    @Test
    @Throws(Exception::class)
    protected fun testDiscoverWithNonCursorFields() {
        testdb
            .with(
                CREATE_TABLE_WITHOUT_CURSOR_TYPE_QUERY,
                getFullyQualifiedTableName(TABLE_NAME_WITHOUT_CURSOR_TYPE),
                COL_CURSOR,
            )
            .with(
                INSERT_TABLE_WITHOUT_CURSOR_TYPE_QUERY,
                getFullyQualifiedTableName(TABLE_NAME_WITHOUT_CURSOR_TYPE),
            )
        val actual = filterOutOtherSchemas(source().discover(config()))
        val stream =
            actual.streams.first { s: AirbyteStream ->
                s.name.equals(TABLE_NAME_WITHOUT_CURSOR_TYPE, ignoreCase = true)
            }
        Assertions.assertEquals(
            TABLE_NAME_WITHOUT_CURSOR_TYPE.lowercase(Locale.getDefault()),
            stream.name.lowercase(Locale.getDefault()),
        )
        Assertions.assertEquals(1, stream.supportedSyncModes.size)
        Assertions.assertEquals(SyncMode.FULL_REFRESH, stream.supportedSyncModes[0])
    }

    @Test
    @Throws(Exception::class)
    protected fun testDiscoverWithNullableCursorFields() {
        testdb
            .with(
                CREATE_TABLE_WITH_NULLABLE_CURSOR_TYPE_QUERY,
                getFullyQualifiedTableName(TABLE_NAME_WITH_NULLABLE_CURSOR_TYPE),
                COL_CURSOR,
            )
            .with(
                INSERT_TABLE_WITH_NULLABLE_CURSOR_TYPE_QUERY,
                getFullyQualifiedTableName(TABLE_NAME_WITH_NULLABLE_CURSOR_TYPE),
            )
        val actual = filterOutOtherSchemas(source().discover(config()))
        val stream =
            actual.streams
                .filter { s: AirbyteStream ->
                    s.name.equals(TABLE_NAME_WITH_NULLABLE_CURSOR_TYPE, ignoreCase = true)
                }
                .first()
        Assertions.assertEquals(
            TABLE_NAME_WITH_NULLABLE_CURSOR_TYPE.lowercase(Locale.getDefault()),
            stream.name.lowercase(Locale.getDefault()),
        )
        Assertions.assertEquals(2, stream.supportedSyncModes.size)
        Assertions.assertTrue(stream.supportedSyncModes.contains(SyncMode.FULL_REFRESH))
        Assertions.assertTrue(stream.supportedSyncModes.contains(SyncMode.INCREMENTAL))
    }

    protected fun filterOutOtherSchemas(catalog: AirbyteCatalog): AirbyteCatalog {
        if (supportsSchemas()) {
            val filteredCatalog = Jsons.clone(catalog)
            filteredCatalog.streams =
                filteredCatalog.streams.filter { stream: AirbyteStream ->
                    TEST_SCHEMAS.any { schemaName: String ->
                        stream.namespace.startsWith(schemaName)
                    }
                }
            return filteredCatalog
        } else {
            return catalog
        }
    }

    protected open fun supportResumeableFullRefreshWithoutPk(): Boolean? {
        return false
    }

    @Test
    @Throws(Exception::class)
    protected fun testDiscoverWithMultipleSchemas() {
        // clickhouse and mysql do not have a concept of schemas, so this test does not make sense
        // for them.
        when (testdb.databaseDriver) {
            DatabaseDriver.MYSQL,
            DatabaseDriver.CLICKHOUSE,
            DatabaseDriver.TERADATA -> return
            else -> {}
        }
        // add table and data to a separate schema.
        testdb
            .with(
                "CREATE TABLE %s(id VARCHAR(200) NOT NULL, name VARCHAR(200) NOT NULL)",
                RelationalDbQueryUtils.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME),
            )
            .with(
                "INSERT INTO %s(id, name) VALUES ('1','picard')",
                RelationalDbQueryUtils.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME),
            )
            .with(
                "INSERT INTO %s(id, name) VALUES ('2', 'crusher')",
                RelationalDbQueryUtils.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME),
            )
            .with(
                "INSERT INTO %s(id, name) VALUES ('3', 'vash')",
                RelationalDbQueryUtils.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME),
            )

        val actual = source().discover(config())

        val expected = getCatalog(defaultNamespace)
        val catalogStreams: MutableList<AirbyteStream> = ArrayList()
        catalogStreams.addAll(expected.streams)
        catalogStreams.add(
            CatalogHelpers.createAirbyteStream(
                    TABLE_NAME,
                    SCHEMA_NAME2,
                    Field.of(COL_ID, JsonSchemaType.STRING),
                    Field.of(COL_NAME, JsonSchemaType.STRING),
                )
                .withSupportedSyncModes(
                    java.util.List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL),
                )
                .withIsResumable(supportResumeableFullRefreshWithoutPk()),
        )
        expected.streams = catalogStreams
        // sort streams by name so that we are comparing lists with the same order.
        val schemaTableCompare =
            Comparator.comparing { stream: AirbyteStream -> stream.namespace + "." + stream.name }
        expected.streams.sortWith(schemaTableCompare)
        actual.streams.sortWith(schemaTableCompare)
        Assertions.assertEquals(expected, filterOutOtherSchemas(actual))
    }

    @Test
    @Throws(Exception::class)
    fun testReadSuccess() {
        val catalog = getConfiguredCatalogWithOneStream(defaultNamespace)
        val actualMessages = MoreIterators.toList(source().read(config(), catalog, null))

        setEmittedAtToNull(actualMessages)
        val expectedMessagesResult: MutableList<AirbyteMessage> = ArrayList(testMessages)
        val actualRecordMessages = filterRecords(actualMessages)

        MatcherAssert.assertThat(
            expectedMessagesResult,
            Matchers.containsInAnyOrder<Any>(*actualRecordMessages.toTypedArray()),
        )
        MatcherAssert.assertThat(
            actualRecordMessages,
            Matchers.containsInAnyOrder<Any>(*expectedMessagesResult.toTypedArray()),
        )
    }

    // This validation only applies to resumable full refresh syncs.
    protected open fun validateFullRefreshStateMessageReadSuccess(
        stateMessages: List<AirbyteStateMessage>
    ) {}

    @Test
    @Throws(Exception::class)
    protected open fun testReadOneColumn() {
        val catalog =
            CatalogHelpers.createConfiguredAirbyteCatalog(
                streamName(),
                defaultNamespace,
                Field.of(COL_ID, JsonSchemaType.NUMBER),
            )
        var actualMessages = MoreIterators.toList(source().read(config(), catalog, null))

        assertStreamStatusTraceMessageIndex(
            0,
            actualMessages,
            createAirbteStreanStatusTraceMessage(
                defaultNamespace,
                streamName(),
                AirbyteStreamStatus.STARTED
            )
        )
        assertStreamStatusTraceMessageIndex(
            actualMessages.size - 1,
            actualMessages,
            createAirbteStreanStatusTraceMessage(
                defaultNamespace,
                streamName(),
                AirbyteStreamStatus.COMPLETE
            )
        )

        setEmittedAtToNull(actualMessages)

        val expectedMessages: MutableList<AirbyteMessage> = airbyteMessagesReadOneColumn

        expectedMessages.addFirst(
            AirbyteTraceMessageUtility.makeStreamStatusTraceAirbyteMessage(
                AirbyteStreamStatusHolder(
                    AirbyteStreamNameNamespacePair(streamName(), defaultNamespace),
                    AirbyteStreamStatus.STARTED
                )
            )
        )

        expectedMessages.addLast(
            AirbyteTraceMessageUtility.makeStreamStatusTraceAirbyteMessage(
                AirbyteStreamStatusHolder(
                    AirbyteStreamNameNamespacePair(streamName(), defaultNamespace),
                    AirbyteStreamStatus.COMPLETE
                )
            )
        )
        setTraceEmittedAtToNull(actualMessages)
        setTraceEmittedAtToNull(expectedMessages)

        actualMessages = removeStateMessage(actualMessages)

        Assertions.assertEquals(expectedMessages.size, actualMessages.size)
        Assertions.assertTrue(expectedMessages.containsAll(actualMessages))
        Assertions.assertTrue(actualMessages.containsAll(expectedMessages))
    }

    private fun removeStateMessage(airbyteMessages: List<AirbyteMessage>): List<AirbyteMessage> {
        var mutableListMessages = airbyteMessages.toMutableList()
        mutableListMessages.removeIf { message -> message.type == AirbyteMessage.Type.STATE }
        return mutableListMessages
    }

    protected open val airbyteMessagesReadOneColumn: MutableList<AirbyteMessage>
        get() {
            val expectedMessages =
                testMessages
                    .map { `object`: AirbyteMessage -> Jsons.clone(`object`) }
                    .onEach { m: AirbyteMessage ->
                        (m.record.data as ObjectNode).remove(COL_NAME)
                        (m.record.data as ObjectNode).remove(COL_UPDATED_AT)
                        (m.record.data as ObjectNode).replace(
                            COL_ID,
                            convertIdBasedOnDatabase(m.record.data[COL_ID].asInt()),
                        )
                    }
                    .toMutableList()
            return expectedMessages
        }

    @Test
    @Throws(Exception::class)
    protected fun testReadMultipleTables() {
        val catalog = getConfiguredCatalogWithOneStream(defaultNamespace)
        val expectedMessages: MutableList<AirbyteMessage> = ArrayList(testMessages)

        for (i in 2..9) {
            val streamName2 = streamName() + i
            val tableName = getFullyQualifiedTableName(TABLE_NAME + i)
            testdb
                .with(createTableQuery(tableName, "id INTEGER, name VARCHAR(200)", ""))
                .with("INSERT INTO %s(id, name) VALUES (1,'picard')", tableName)
                .with("INSERT INTO %s(id, name) VALUES (2, 'crusher')", tableName)
                .with("INSERT INTO %s(id, name) VALUES (3, 'vash')", tableName)
            catalog.streams.add(
                CatalogHelpers.createConfiguredAirbyteStream(
                    streamName2,
                    defaultNamespace,
                    Field.of(COL_ID, JsonSchemaType.NUMBER),
                    Field.of(COL_NAME, JsonSchemaType.STRING),
                ),
            )

            expectedMessages.addAll(getAirbyteMessagesSecondSync(streamName2))
        }

        val actualMessages = MoreIterators.toList(source().read(config(), catalog, null))
        val actualRecordMessages = filterRecords(actualMessages)

        setEmittedAtToNull(actualMessages)

        Assertions.assertEquals(expectedMessages.size, actualRecordMessages.size)
        Assertions.assertTrue(expectedMessages.containsAll(actualRecordMessages))
        Assertions.assertTrue(actualRecordMessages.containsAll(expectedMessages))
    }

    @Test
    @Throws(Exception::class)
    protected fun testReadBothIncrementalAndFullRefreshStreams() {
        val catalog = getConfiguredCatalogWithOneStream(defaultNamespace)
        val expectedMessages: MutableList<AirbyteMessage> = ArrayList(testMessages)

        val streamName2 = streamName() + 2
        val tableName = getFullyQualifiedTableName(TABLE_NAME + 2)
        testdb!!
            .with(createTableQuery(tableName, "id INTEGER, name VARCHAR(200)", ""))
            .with("INSERT INTO %s(id, name) VALUES (1,'picard')", tableName)
            .with("INSERT INTO %s(id, name) VALUES (2, 'crusher')", tableName)
            .with("INSERT INTO %s(id, name) VALUES (3, 'vash')", tableName)

        val airbyteStream2 =
            CatalogHelpers.createConfiguredAirbyteStream(
                streamName2,
                defaultNamespace,
                Field.of(COL_ID, JsonSchemaType.NUMBER),
                Field.of(COL_NAME, JsonSchemaType.STRING),
            )
        airbyteStream2.syncMode = SyncMode.INCREMENTAL
        airbyteStream2.cursorField = java.util.List.of(COL_ID)
        airbyteStream2.destinationSyncMode = DestinationSyncMode.APPEND
        catalog.streams.add(airbyteStream2)

        expectedMessages.addAll(getAirbyteMessagesSecondSync(streamName2))

        val actualMessages = MoreIterators.toList(source()!!.read(config(), catalog, null))

        assertStreamStatusTraceMessageIndex(
            0,
            actualMessages,
            createAirbteStreanStatusTraceMessage(
                defaultNamespace,
                streamName2,
                AirbyteStreamStatus.STARTED
            )
        )
        assertStreamStatusTraceMessageIndex(
            actualMessages.size - 7,
            actualMessages,
            createAirbteStreanStatusTraceMessage(
                defaultNamespace,
                streamName2,
                AirbyteStreamStatus.COMPLETE
            )
        )
        assertStreamStatusTraceMessageIndex(
            actualMessages.size - 6,
            actualMessages,
            createAirbteStreanStatusTraceMessage(
                defaultNamespace,
                streamName(),
                AirbyteStreamStatus.STARTED
            )
        )
        assertStreamStatusTraceMessageIndex(
            actualMessages.size - 1,
            actualMessages,
            createAirbteStreanStatusTraceMessage(
                defaultNamespace,
                streamName(),
                AirbyteStreamStatus.COMPLETE
            )
        )

        val actualRecordMessages = filterRecords(actualMessages)

        setEmittedAtToNull(actualMessages)

        Assertions.assertEquals(expectedMessages.size, actualRecordMessages.size)
        Assertions.assertTrue(expectedMessages.containsAll(actualRecordMessages))
        Assertions.assertTrue(actualRecordMessages.containsAll(expectedMessages))
    }

    protected open fun getAirbyteMessagesSecondSync(streamName: String?): List<AirbyteMessage> {
        return testMessages
            .map { `object`: AirbyteMessage -> Jsons.clone(`object`) }
            .onEach { m: AirbyteMessage ->
                m.record.stream = streamName
                m.record.namespace = defaultNamespace
                (m.record.data as ObjectNode).remove(COL_UPDATED_AT)
                (m.record.data as ObjectNode).replace(
                    COL_ID,
                    convertIdBasedOnDatabase(m.record.data[COL_ID].asInt()),
                )
            }
    }

    @Test
    @Throws(Exception::class)
    protected fun testTablesWithQuoting() {
        val streamForTableWithSpaces = createTableWithSpaces()

        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        getConfiguredCatalogWithOneStream(defaultNamespace).streams[0],
                        streamForTableWithSpaces,
                    ),
                )
        val actualMessages = MoreIterators.toList(source().read(config(), catalog, null))
        val actualRecordMessages = filterRecords(actualMessages)

        setEmittedAtToNull(actualMessages)

        val expectedMessages: MutableList<AirbyteMessage> = ArrayList(testMessages)
        expectedMessages.addAll(getAirbyteMessagesForTablesWithQuoting(streamForTableWithSpaces))

        Assertions.assertEquals(expectedMessages.size, actualRecordMessages.size)
        Assertions.assertTrue(expectedMessages.containsAll(actualRecordMessages))
        Assertions.assertTrue(actualRecordMessages.containsAll(expectedMessages))
    }

    @Test
    @Throws(Exception::class)
    protected fun testTablesWithResumableFullRefreshStates() {

        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        getConfiguredCatalogWithOneStream(defaultNamespace).streams[0],
                    ),
                )
        val actualMessages = MoreIterators.toList(source()!!.read(config(), catalog, null))
        val actualRecordMessages = filterRecords(actualMessages)

        setEmittedAtToNull(actualMessages)

        val expectedMessages: MutableList<AirbyteMessage> = ArrayList(testMessages)

        Assertions.assertEquals(expectedMessages.size, actualRecordMessages.size)
        Assertions.assertTrue(expectedMessages.containsAll(actualRecordMessages))
        Assertions.assertTrue(actualRecordMessages.containsAll(expectedMessages))

        val stateMessages = extractStateMessage(actualMessages)
        validateFullRefreshStateMessageReadSuccess(stateMessages)
    }

    protected open fun getAirbyteMessagesForTablesWithQuoting(
        streamForTableWithSpaces: ConfiguredAirbyteStream
    ): List<AirbyteMessage> {
        return testMessages
            .map { `object`: AirbyteMessage -> Jsons.clone(`object`) }
            .onEach { m: AirbyteMessage ->
                m.record.stream = streamForTableWithSpaces.stream.name
                (m.record.data as ObjectNode).set<JsonNode>(
                    COL_LAST_NAME_WITH_SPACE,
                    (m.record.data as ObjectNode).remove(COL_NAME),
                )
                (m.record.data as ObjectNode).remove(COL_UPDATED_AT)
                (m.record.data as ObjectNode).replace(
                    COL_ID,
                    convertIdBasedOnDatabase(m.record.data[COL_ID].asInt()),
                )
            }
    }

    @Test
    fun testReadFailure() {
        val spiedAbStream =
            Mockito.spy(getConfiguredCatalogWithOneStream(defaultNamespace).streams[0])
        val catalog = ConfiguredAirbyteCatalog().withStreams(java.util.List.of(spiedAbStream))
        Mockito.doCallRealMethod().doThrow(RuntimeException()).`when`(spiedAbStream).stream

        Assertions.assertThrows(RuntimeException::class.java) {
            source().read(config(), catalog, null)
        }
    }

    @Test
    @Throws(Exception::class)
    fun testIncrementalNoPreviousState() {
        incrementalCursorCheck(COL_ID, null, "3", testMessages)
    }

    @Test
    @Throws(Exception::class)
    fun testIncrementalIntCheckCursor() {
        incrementalCursorCheck(COL_ID, "2", "3", java.util.List.of(testMessages[2]))
    }

    @Test
    @Throws(Exception::class)
    fun testIncrementalStringCheckCursor() {
        incrementalCursorCheck(
            COL_NAME,
            "patent",
            "vash",
            java.util.List.of(testMessages[0], testMessages[2]),
        )
    }

    @Test
    @Throws(Exception::class)
    fun testIncrementalStringCheckCursorSpaceInColumnName() {
        val streamWithSpaces = createTableWithSpaces()

        val expectedRecordMessages =
            getAirbyteMessagesCheckCursorSpaceInColumnName(streamWithSpaces)
        incrementalCursorCheck(
            COL_LAST_NAME_WITH_SPACE,
            COL_LAST_NAME_WITH_SPACE,
            "patent",
            "vash",
            expectedRecordMessages,
            streamWithSpaces,
        )
    }

    protected open fun getAirbyteMessagesCheckCursorSpaceInColumnName(
        streamWithSpaces: ConfiguredAirbyteStream
    ): List<AirbyteMessage> {
        val firstMessage = testMessages[0]
        firstMessage.record.stream = streamWithSpaces.stream.name
        (firstMessage.record.data as ObjectNode).remove(COL_UPDATED_AT)
        (firstMessage.record.data as ObjectNode).set<JsonNode>(
            COL_LAST_NAME_WITH_SPACE,
            (firstMessage.record.data as ObjectNode).remove(COL_NAME),
        )

        val secondMessage = testMessages[2]
        secondMessage.record.stream = streamWithSpaces.stream.name
        (secondMessage.record.data as ObjectNode).remove(COL_UPDATED_AT)
        (secondMessage.record.data as ObjectNode).set<JsonNode>(
            COL_LAST_NAME_WITH_SPACE,
            (secondMessage.record.data as ObjectNode).remove(COL_NAME),
        )

        return java.util.List.of(firstMessage, secondMessage)
    }

    @Test
    @Throws(Exception::class)
    fun testIncrementalDateCheckCursor() {
        incrementalDateCheck()
    }

    @Throws(Exception::class)
    protected open fun incrementalDateCheck() {
        incrementalCursorCheck(
            COL_UPDATED_AT,
            "2005-10-18",
            "2006-10-19",
            java.util.List.of(testMessages[1], testMessages[2]),
        )
    }

    @Test
    @Throws(Exception::class)
    fun testIncrementalCursorChanges() {
        incrementalCursorCheck(
            COL_ID,
            COL_NAME, // cheesing this value a little bit. in the correct implementation this
            // initial cursor value should
            // be ignored because the cursor field changed. setting it to a value that if used, will
            // cause
            // records to (incorrectly) be filtered out.
            "data",
            "vash",
            testMessages,
        )
    }

    @Test
    @Throws(Exception::class)
    protected open fun testReadOneTableIncrementallyTwice() {
        val config = config()
        val namespace = defaultNamespace
        val configuredCatalog = getConfiguredCatalogWithOneStream(namespace)
        configuredCatalog.streams.forEach(
            Consumer { airbyteStream: ConfiguredAirbyteStream ->
                airbyteStream.syncMode = SyncMode.INCREMENTAL
                airbyteStream.cursorField = java.util.List.of(COL_ID)
                airbyteStream.destinationSyncMode = DestinationSyncMode.APPEND
            },
        )

        val actualMessagesFirstSync =
            MoreIterators.toList(
                source()!!.read(
                    config,
                    configuredCatalog,
                    createEmptyState(streamName(), namespace),
                ),
            )

        assertStreamStatusTraceMessageIndex(
            0,
            actualMessagesFirstSync,
            createAirbteStreanStatusTraceMessage(
                defaultNamespace,
                streamName(),
                AirbyteStreamStatus.STARTED
            )
        )
        assertStreamStatusTraceMessageIndex(
            actualMessagesFirstSync.size - 1,
            actualMessagesFirstSync,
            createAirbteStreanStatusTraceMessage(
                defaultNamespace,
                streamName(),
                AirbyteStreamStatus.COMPLETE
            )
        )

        val stateAfterFirstSyncOptional =
            actualMessagesFirstSync
                .filter { r: AirbyteMessage -> r.type == AirbyteMessage.Type.STATE }
                .first()

        executeStatementReadIncrementallyTwice()

        val actualMessagesSecondSync =
            MoreIterators.toList(
                source()!!.read(
                    config,
                    configuredCatalog,
                    extractState(stateAfterFirstSyncOptional),
                ),
            )

        assertStreamStatusTraceMessageIndex(
            0,
            actualMessagesSecondSync,
            createAirbteStreanStatusTraceMessage(
                defaultNamespace,
                streamName(),
                AirbyteStreamStatus.STARTED
            )
        )
        assertStreamStatusTraceMessageIndex(
            actualMessagesSecondSync.size - 1,
            actualMessagesSecondSync,
            createAirbteStreanStatusTraceMessage(
                defaultNamespace,
                streamName(),
                AirbyteStreamStatus.COMPLETE
            )
        )

        Assertions.assertEquals(
            2,
            actualMessagesSecondSync
                .filter { r: AirbyteMessage -> r.type == AirbyteMessage.Type.RECORD }
                .count()
                .toInt(),
        )
        val expectedMessages: MutableList<AirbyteMessage> =
            getExpectedAirbyteMessagesSecondSync(namespace)

        setEmittedAtToNull(actualMessagesSecondSync)

        expectedMessages.addFirst(
            AirbyteTraceMessageUtility.makeStreamStatusTraceAirbyteMessage(
                AirbyteStreamStatusHolder(
                    AirbyteStreamNameNamespacePair(
                        configuredCatalog.streams[0].stream.name,
                        defaultNamespace
                    ),
                    AirbyteStreamStatus.STARTED
                )
            )
        )

        expectedMessages.addLast(
            AirbyteTraceMessageUtility.makeStreamStatusTraceAirbyteMessage(
                AirbyteStreamStatusHolder(
                    AirbyteStreamNameNamespacePair(
                        configuredCatalog.streams[0].stream.name,
                        defaultNamespace
                    ),
                    AirbyteStreamStatus.COMPLETE
                )
            )
        )
        setTraceEmittedAtToNull(actualMessagesSecondSync)
        setTraceEmittedAtToNull(expectedMessages)
        Assertions.assertEquals(expectedMessages.size, actualMessagesSecondSync.size)
        Assertions.assertTrue(expectedMessages.containsAll(actualMessagesSecondSync))
        Assertions.assertTrue(actualMessagesSecondSync.containsAll(expectedMessages))
    }

    protected open fun executeStatementReadIncrementallyTwice() {
        testdb
            ?.with(
                "INSERT INTO %s (id, name, updated_at) VALUES (4, 'riker', '2006-10-19')",
                getFullyQualifiedTableName(TABLE_NAME),
            )
            ?.with(
                "INSERT INTO %s (id, name, updated_at) VALUES (5, 'data', '2006-10-19')",
                getFullyQualifiedTableName(TABLE_NAME),
            )
    }

    protected open fun getExpectedAirbyteMessagesSecondSync(
        namespace: String?
    ): MutableList<AirbyteMessage> {
        val expectedMessages: MutableList<AirbyteMessage> = ArrayList()
        expectedMessages.add(
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream(streamName())
                        .withNamespace(namespace)
                        .withData(
                            Jsons.jsonNode(
                                java.util.Map.of(
                                    COL_ID,
                                    ID_VALUE_4,
                                    COL_NAME,
                                    "riker",
                                    COL_UPDATED_AT,
                                    "2006-10-19",
                                ),
                            ),
                        ),
                ),
        )
        expectedMessages.add(
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream(streamName())
                        .withNamespace(namespace)
                        .withData(
                            Jsons.jsonNode(
                                java.util.Map.of(
                                    COL_ID,
                                    ID_VALUE_5,
                                    COL_NAME,
                                    "data",
                                    COL_UPDATED_AT,
                                    "2006-10-19",
                                ),
                            ),
                        ),
                ),
        )
        val state =
            DbStreamState()
                .withStreamName(streamName())
                .withStreamNamespace(namespace)
                .withCursorField(java.util.List.of(COL_ID))
                .withCursor("5")
                .withCursorRecordCount(1L)
        expectedMessages.addAll(createExpectedTestMessages(java.util.List.of(state), 2L))
        return expectedMessages
    }

    @Test
    @Throws(Exception::class)
    protected open fun testReadMultipleTablesIncrementally() {
        val tableName2 = TABLE_NAME + 2
        val streamName2 = streamName() + 2
        val fqTableName2 = getFullyQualifiedTableName(tableName2)
        testdb
            .with(createTableQuery(fqTableName2, "id INTEGER, name VARCHAR(200)", ""))
            .with("INSERT INTO %s(id, name) VALUES (1,'picard')", fqTableName2)
            .with("INSERT INTO %s(id, name) VALUES (2, 'crusher')", fqTableName2)
            .with("INSERT INTO %s(id, name) VALUES (3, 'vash')", fqTableName2)

        val namespace = defaultNamespace
        val configuredCatalog = getConfiguredCatalogWithOneStream(namespace)
        configuredCatalog.streams.add(
            CatalogHelpers.createConfiguredAirbyteStream(
                streamName2,
                namespace,
                Field.of(COL_ID, JsonSchemaType.NUMBER),
                Field.of(COL_NAME, JsonSchemaType.STRING),
            ),
        )
        configuredCatalog.streams.forEach(
            Consumer { airbyteStream: ConfiguredAirbyteStream ->
                airbyteStream.syncMode = SyncMode.INCREMENTAL
                airbyteStream.cursorField = java.util.List.of(COL_ID)
                airbyteStream.destinationSyncMode = DestinationSyncMode.APPEND
            },
        )

        val actualMessagesFirstSync =
            MoreIterators.toList(
                source()!!.read(
                    config(),
                    configuredCatalog,
                    createEmptyState(streamName(), namespace),
                ),
            )

        // get last state message.
        val stateAfterFirstSyncOptional =
            actualMessagesFirstSync.last { r: AirbyteMessage ->
                r.type == AirbyteMessage.Type.STATE
            }

        // we know the second streams messages are the same as the first minus the updated at
        // column. so we
        // cheat and generate the expected messages off of the first expected messages.
        val secondStreamExpectedMessages = getAirbyteMessagesSecondStreamWithNamespace(streamName2)

        // Represents the state after the first stream has been updated
        val expectedStateStreams1 =
            java.util.List.of(
                DbStreamState()
                    .withStreamName(streamName())
                    .withStreamNamespace(namespace)
                    .withCursorField(java.util.List.of(COL_ID))
                    .withCursor("3")
                    .withCursorRecordCount(1L),
                DbStreamState()
                    .withStreamName(streamName2)
                    .withStreamNamespace(namespace)
                    .withCursorField(java.util.List.of(COL_ID)),
            )

        // Represents the state after both streams have been updated
        val expectedStateStreams2 =
            java.util.List.of(
                DbStreamState()
                    .withStreamName(streamName())
                    .withStreamNamespace(namespace)
                    .withCursorField(java.util.List.of(COL_ID))
                    .withCursor("3")
                    .withCursorRecordCount(1L),
                DbStreamState()
                    .withStreamName(streamName2)
                    .withStreamNamespace(namespace)
                    .withCursorField(java.util.List.of(COL_ID))
                    .withCursor("3")
                    .withCursorRecordCount(1L),
            )

        val expectedMessagesFirstSync: MutableList<AirbyteMessage> = ArrayList(testMessages)
        expectedMessagesFirstSync.add(
            createStateMessage(expectedStateStreams1[0], expectedStateStreams1, 3L),
        )
        expectedMessagesFirstSync.addAll(secondStreamExpectedMessages)
        expectedMessagesFirstSync.add(
            createStateMessage(expectedStateStreams2[1], expectedStateStreams2, 3L),
        )

        setEmittedAtToNull(actualMessagesFirstSync)

        Assertions.assertEquals(expectedMessagesFirstSync.size, actualMessagesFirstSync.size)
        Assertions.assertTrue(expectedMessagesFirstSync.containsAll(actualMessagesFirstSync))
        Assertions.assertTrue(actualMessagesFirstSync.containsAll(expectedMessagesFirstSync))
    }

    protected open fun getAirbyteMessagesSecondStreamWithNamespace(
        streamName2: String?
    ): List<AirbyteMessage> {
        return testMessages
            .map { `object`: AirbyteMessage -> Jsons.clone(`object`) }
            .onEach { m: AirbyteMessage ->
                m.record.stream = streamName2
                (m.record.data as ObjectNode).remove(COL_UPDATED_AT)
                (m.record.data as ObjectNode).replace(
                    COL_ID,
                    convertIdBasedOnDatabase(m.record.data[COL_ID].asInt()),
                )
            }
    }

    // when initial and final cursor fields are the same.
    @Throws(Exception::class)
    protected fun incrementalCursorCheck(
        cursorField: String,
        initialCursorValue: String?,
        endCursorValue: String,
        expectedRecordMessages: List<AirbyteMessage>
    ) {
        incrementalCursorCheck(
            cursorField,
            cursorField,
            initialCursorValue,
            endCursorValue,
            expectedRecordMessages,
        )
    }

    // See https://github.com/airbytehq/airbyte/issues/14732 for rationale and details.
    @Test
    @Throws(Exception::class)
    fun testIncrementalWithConcurrentInsertion() {
        val namespace = defaultNamespace
        val fullyQualifiedTableName = getFullyQualifiedTableName(TABLE_NAME_AND_TIMESTAMP)
        val columnDefinition =
            String.format(
                "name VARCHAR(200) NOT NULL, %s %s NOT NULL",
                COL_TIMESTAMP,
                COL_TIMESTAMP_TYPE,
            )

        // 1st sync
        testdb
            .with(createTableQuery(fullyQualifiedTableName, columnDefinition, ""))
            .with(
                INSERT_TABLE_NAME_AND_TIMESTAMP_QUERY,
                fullyQualifiedTableName,
                "a",
                "2021-01-01 00:00:00",
            )
            .with(
                INSERT_TABLE_NAME_AND_TIMESTAMP_QUERY,
                fullyQualifiedTableName,
                "b",
                "2021-01-01 00:00:00",
            )

        val configuredCatalog =
            CatalogHelpers.toDefaultConfiguredCatalog(
                AirbyteCatalog()
                    .withStreams(
                        java.util.List.of(
                            CatalogHelpers.createAirbyteStream(
                                TABLE_NAME_AND_TIMESTAMP,
                                namespace,
                                Field.of(COL_NAME, JsonSchemaType.STRING),
                                Field.of(
                                    COL_TIMESTAMP,
                                    JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE,
                                ),
                            ),
                        ),
                    ),
            )

        configuredCatalog.streams.forEach(
            Consumer { airbyteStream: ConfiguredAirbyteStream ->
                airbyteStream.syncMode = SyncMode.INCREMENTAL
                airbyteStream.cursorField = java.util.List.of(COL_TIMESTAMP)
                airbyteStream.destinationSyncMode = DestinationSyncMode.APPEND
            },
        )

        val firstSyncActualMessages =
            MoreIterators.toList(
                source()!!.read(
                    config(),
                    configuredCatalog,
                    createEmptyState(TABLE_NAME_AND_TIMESTAMP, namespace),
                ),
            )

        // cursor after 1st sync: 2021-01-01 00:00:00, count 2
        val firstSyncStateOptional =
            firstSyncActualMessages
                .filter { r: AirbyteMessage -> r.type == AirbyteMessage.Type.STATE }
                .first()
        val firstSyncState = getStateData(firstSyncStateOptional, TABLE_NAME_AND_TIMESTAMP)
        Assertions.assertEquals(
            firstSyncState["cursor_field"].elements().next().asText(),
            COL_TIMESTAMP,
        )
        Assertions.assertTrue(firstSyncState["cursor"].asText().contains("2021-01-01"))
        Assertions.assertTrue(firstSyncState["cursor"].asText().contains("00:00:00"))
        Assertions.assertEquals(2L, firstSyncState["cursor_record_count"].asLong())

        val firstSyncNames =
            firstSyncActualMessages
                .filter { r: AirbyteMessage -> r.type == AirbyteMessage.Type.RECORD }
                .map { r: AirbyteMessage -> r.record.data[COL_NAME].asText() }

        // some databases don't make insertion order guarantee when equal ordering value
        if (
            testdb.databaseDriver == DatabaseDriver.TERADATA ||
                testdb.databaseDriver == DatabaseDriver.ORACLE
        ) {
            MatcherAssert.assertThat(
                listOf("a", "b"),
                Matchers.containsInAnyOrder<Any>(*firstSyncNames.toTypedArray()),
            )
        } else {
            Assertions.assertEquals(listOf("a", "b"), firstSyncNames)
        }

        // 2nd sync
        testdb.with(
            INSERT_TABLE_NAME_AND_TIMESTAMP_QUERY,
            fullyQualifiedTableName,
            "c",
            "2021-01-02 00:00:00",
        )

        val secondSyncActualMessages =
            MoreIterators.toList(
                source()!!.read(
                    config(),
                    configuredCatalog,
                    createState(TABLE_NAME_AND_TIMESTAMP, namespace, firstSyncState),
                ),
            )

        // cursor after 2nd sync: 2021-01-02 00:00:00, count 1
        val secondSyncStateOptional =
            secondSyncActualMessages
                .filter { r: AirbyteMessage -> r.type == AirbyteMessage.Type.STATE }
                .first()
        val secondSyncState = getStateData(secondSyncStateOptional, TABLE_NAME_AND_TIMESTAMP)
        Assertions.assertEquals(
            secondSyncState["cursor_field"].elements().next().asText(),
            COL_TIMESTAMP,
        )
        Assertions.assertTrue(secondSyncState["cursor"].asText().contains("2021-01-02"))
        Assertions.assertTrue(secondSyncState["cursor"].asText().contains("00:00:00"))
        Assertions.assertEquals(1L, secondSyncState["cursor_record_count"].asLong())

        val secondSyncNames =
            secondSyncActualMessages
                .filter { r: AirbyteMessage -> r.type == AirbyteMessage.Type.RECORD }
                .map { r: AirbyteMessage -> r.record.data[COL_NAME].asText() }

        Assertions.assertEquals(listOf("c"), secondSyncNames)

        // 3rd sync has records with duplicated cursors
        testdb
            .with(
                INSERT_TABLE_NAME_AND_TIMESTAMP_QUERY,
                fullyQualifiedTableName,
                "d",
                "2021-01-02 00:00:00",
            )
            .with(
                INSERT_TABLE_NAME_AND_TIMESTAMP_QUERY,
                fullyQualifiedTableName,
                "e",
                "2021-01-02 00:00:00",
            )
            .with(
                INSERT_TABLE_NAME_AND_TIMESTAMP_QUERY,
                fullyQualifiedTableName,
                "f",
                "2021-01-03 00:00:00",
            )

        val thirdSyncActualMessages =
            MoreIterators.toList(
                source()!!.read(
                    config(),
                    configuredCatalog,
                    createState(TABLE_NAME_AND_TIMESTAMP, namespace, secondSyncState),
                ),
            )

        // Cursor after 3rd sync is: 2021-01-03 00:00:00, count 1.
        val thirdSyncStateOptional =
            thirdSyncActualMessages
                .filter { r: AirbyteMessage -> r.type == AirbyteMessage.Type.STATE }
                .first()
        val thirdSyncState = getStateData(thirdSyncStateOptional, TABLE_NAME_AND_TIMESTAMP)
        Assertions.assertEquals(
            thirdSyncState["cursor_field"].elements().next().asText(),
            COL_TIMESTAMP,
        )
        Assertions.assertTrue(thirdSyncState["cursor"].asText().contains("2021-01-03"))
        Assertions.assertTrue(thirdSyncState["cursor"].asText().contains("00:00:00"))
        Assertions.assertEquals(1L, thirdSyncState["cursor_record_count"].asLong())

        // The c, d, e, f are duplicated records from this sync, because the cursor
        // record count in the database is different from that in the state.
        val thirdSyncExpectedNames =
            thirdSyncActualMessages
                .filter { r: AirbyteMessage -> r.type == AirbyteMessage.Type.RECORD }
                .map { r: AirbyteMessage -> r.record.data[COL_NAME].asText() }

        // teradata doesn't make insertion order guarantee when equal ordering value
        if (testdb.databaseDriver == DatabaseDriver.TERADATA) {
            MatcherAssert.assertThat(
                listOf("c", "d", "e", "f"),
                Matchers.containsInAnyOrder<Any>(*thirdSyncExpectedNames.toTypedArray()),
            )
        } else {
            Assertions.assertEquals(listOf("c", "d", "e", "f"), thirdSyncExpectedNames)
        }
    }

    protected open fun getStateData(airbyteMessage: AirbyteMessage, streamName: String): JsonNode {
        for (stream in airbyteMessage.state.data["streams"]) {
            if (stream["stream_name"].asText() == streamName) {
                return stream
            }
        }
        throw IllegalArgumentException("Stream not found in state message: $streamName")
    }

    @Throws(Exception::class)
    private fun incrementalCursorCheck(
        initialCursorField: String,
        cursorField: String,
        initialCursorValue: String?,
        endCursorValue: String,
        expectedRecordMessages: List<AirbyteMessage>
    ) {
        incrementalCursorCheck(
            initialCursorField,
            cursorField,
            initialCursorValue,
            endCursorValue,
            expectedRecordMessages,
            getConfiguredCatalogWithOneStream(defaultNamespace).streams[0],
        )
    }

    @Throws(Exception::class)
    protected open fun incrementalCursorCheck(
        initialCursorField: String?,
        cursorField: String,
        initialCursorValue: String?,
        endCursorValue: String?,
        expectedRecordMessages: List<AirbyteMessage>,
        airbyteStream: ConfiguredAirbyteStream
    ) {
        airbyteStream.syncMode = SyncMode.INCREMENTAL
        airbyteStream.cursorField = java.util.List.of(cursorField)
        airbyteStream.destinationSyncMode = DestinationSyncMode.APPEND

        val configuredCatalog =
            ConfiguredAirbyteCatalog().withStreams(java.util.List.of(airbyteStream))

        val dbStreamState = buildStreamState(airbyteStream, initialCursorField, initialCursorValue)

        val actualMessages =
            MoreIterators.toList(
                source()!!.read(
                    config(),
                    configuredCatalog,
                    Jsons.jsonNode(createState(java.util.List.of(dbStreamState))),
                ),
            )

        setEmittedAtToNull(actualMessages)

        val expectedStreams =
            java.util.List.of(buildStreamState(airbyteStream, cursorField, endCursorValue))

        val expectedMessages: MutableList<AirbyteMessage> = ArrayList(expectedRecordMessages)
        expectedMessages.addAll(
            createExpectedTestMessages(expectedStreams, expectedRecordMessages.size.toLong()),
        )

        expectedMessages.addFirst(
            AirbyteTraceMessageUtility.makeStreamStatusTraceAirbyteMessage(
                AirbyteStreamStatusHolder(
                    AirbyteStreamNameNamespacePair(
                        airbyteStream.stream.name,
                        airbyteStream.stream.namespace
                    ),
                    AirbyteStreamStatus.STARTED
                )
            )
        )

        expectedMessages.addLast(
            AirbyteTraceMessageUtility.makeStreamStatusTraceAirbyteMessage(
                AirbyteStreamStatusHolder(
                    AirbyteStreamNameNamespacePair(
                        airbyteStream.stream.name,
                        airbyteStream.stream.namespace
                    ),
                    AirbyteStreamStatus.COMPLETE
                )
            )
        )
        setTraceEmittedAtToNull(actualMessages)
        setTraceEmittedAtToNull(expectedMessages)
        Assertions.assertEquals(expectedMessages.size, actualMessages.size)
        Assertions.assertTrue(expectedMessages.containsAll(actualMessages))
        Assertions.assertTrue(actualMessages.containsAll(expectedMessages))
    }

    protected open fun buildStreamState(
        configuredAirbyteStream: ConfiguredAirbyteStream,
        cursorField: String?,
        cursorValue: String?
    ): DbStreamState {
        return DbStreamState()
            .withStreamName(configuredAirbyteStream.stream.name)
            .withStreamNamespace(configuredAirbyteStream.stream.namespace)
            .withCursorField(java.util.List.of(cursorField))
            .withCursor(cursorValue)
            .withCursorRecordCount(1L)
    }

    // get catalog and perform a defensive copy.
    protected fun getConfiguredCatalogWithOneStream(
        defaultNamespace: String?
    ): ConfiguredAirbyteCatalog {
        val catalog = CatalogHelpers.toDefaultConfiguredCatalog(getCatalog(defaultNamespace))
        // Filter to only keep the main stream name as configured stream
        catalog.withStreams(
            catalog.streams
                .filter { s: ConfiguredAirbyteStream -> s.stream.name == streamName() }
                .toMutableList()
        )
        return catalog
    }

    protected open fun getCatalog(defaultNamespace: String?): AirbyteCatalog {
        return AirbyteCatalog()
            .withStreams(
                mutableListOf(
                    CatalogHelpers.createAirbyteStream(
                            TABLE_NAME,
                            defaultNamespace,
                            Field.of(COL_ID, JsonSchemaType.INTEGER),
                            Field.of(COL_NAME, JsonSchemaType.STRING),
                            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING),
                        )
                        .withSupportedSyncModes(
                            java.util.List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL),
                        )
                        .withSourceDefinedPrimaryKey(java.util.List.of(java.util.List.of(COL_ID))),
                    CatalogHelpers.createAirbyteStream(
                            TABLE_NAME_WITHOUT_PK,
                            defaultNamespace,
                            Field.of(COL_ID, JsonSchemaType.INTEGER),
                            Field.of(COL_NAME, JsonSchemaType.STRING),
                            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING),
                        )
                        .withSupportedSyncModes(
                            java.util.List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL),
                        )
                        .withSourceDefinedPrimaryKey(emptyList()),
                    CatalogHelpers.createAirbyteStream(
                            TABLE_NAME_COMPOSITE_PK,
                            defaultNamespace,
                            Field.of(COL_FIRST_NAME, JsonSchemaType.STRING),
                            Field.of(COL_LAST_NAME, JsonSchemaType.STRING),
                            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING),
                        )
                        .withSupportedSyncModes(
                            java.util.List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL),
                        )
                        .withSourceDefinedPrimaryKey(
                            java.util.List.of(
                                java.util.List.of(COL_FIRST_NAME),
                                java.util.List.of(COL_LAST_NAME),
                            ),
                        ),
                ),
            )
    }

    protected open val testMessages: List<AirbyteMessage>
        get() =
            java.util.List.of(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withStream(streamName())
                            .withNamespace(defaultNamespace)
                            .withData(
                                Jsons.jsonNode(
                                    java.util.Map.of(
                                        COL_ID,
                                        ID_VALUE_1,
                                        COL_NAME,
                                        "picard",
                                        COL_UPDATED_AT,
                                        "2004-10-19",
                                    ),
                                ),
                            ),
                    ),
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withStream(streamName())
                            .withNamespace(defaultNamespace)
                            .withData(
                                Jsons.jsonNode(
                                    java.util.Map.of(
                                        COL_ID,
                                        ID_VALUE_2,
                                        COL_NAME,
                                        "crusher",
                                        COL_UPDATED_AT,
                                        "2005-10-19",
                                    ),
                                ),
                            ),
                    ),
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withStream(streamName())
                            .withNamespace(defaultNamespace)
                            .withData(
                                Jsons.jsonNode(
                                    java.util.Map.of(
                                        COL_ID,
                                        ID_VALUE_3,
                                        COL_NAME,
                                        "vash",
                                        COL_UPDATED_AT,
                                        "2006-10-19",
                                    ),
                                ),
                            ),
                    ),
            )

    protected open fun createExpectedTestMessages(
        states: List<DbStreamState>,
        numRecords: Long
    ): List<AirbyteMessage> {
        return states.map { s: DbStreamState ->
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(
                            AirbyteStreamState()
                                .withStreamDescriptor(
                                    StreamDescriptor()
                                        .withNamespace(s.streamNamespace)
                                        .withName(s.streamName)
                                )
                                .withStreamState(Jsons.jsonNode(s))
                        )
                        .withData(Jsons.jsonNode(DbState().withCdc(false).withStreams(states)))
                        .withSourceStats(
                            AirbyteStateStats().withRecordCount(numRecords.toDouble())
                        ),
                )
        }
    }

    protected open fun createState(states: List<DbStreamState>): List<AirbyteStateMessage> {
        return states.map { s: DbStreamState ->
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                .withStream(
                    AirbyteStreamState()
                        .withStreamDescriptor(
                            StreamDescriptor()
                                .withNamespace(s.streamNamespace)
                                .withName(s.streamName)
                        )
                        .withStreamState(Jsons.jsonNode(s)),
                )
        }
    }

    @Throws(SQLException::class)
    protected fun createTableWithSpaces(): ConfiguredAirbyteStream {
        val tableNameWithSpaces = TABLE_NAME_WITH_SPACES + "2"
        val streamName2 = tableNameWithSpaces

        testdb.getDataSource()!!.connection.use { connection ->
            val identifierQuoteString = connection.metaData.identifierQuoteString
            connection
                .createStatement()
                .execute(
                    createTableQuery(
                        getFullyQualifiedTableName(
                            RelationalDbQueryUtils.enquoteIdentifier(
                                tableNameWithSpaces,
                                identifierQuoteString,
                            ),
                        ),
                        "id INTEGER, " +
                            RelationalDbQueryUtils.enquoteIdentifier(
                                COL_LAST_NAME_WITH_SPACE,
                                identifierQuoteString,
                            ) +
                            " VARCHAR(200)",
                        "",
                    ),
                )
            connection
                .createStatement()
                .execute(
                    String.format(
                        "INSERT INTO %s(id, %s) VALUES (1,'picard')",
                        getFullyQualifiedTableName(
                            RelationalDbQueryUtils.enquoteIdentifier(
                                tableNameWithSpaces,
                                identifierQuoteString,
                            ),
                        ),
                        RelationalDbQueryUtils.enquoteIdentifier(
                            COL_LAST_NAME_WITH_SPACE,
                            identifierQuoteString,
                        ),
                    ),
                )
            connection
                .createStatement()
                .execute(
                    String.format(
                        "INSERT INTO %s(id, %s) VALUES (2, 'crusher')",
                        getFullyQualifiedTableName(
                            RelationalDbQueryUtils.enquoteIdentifier(
                                tableNameWithSpaces,
                                identifierQuoteString,
                            ),
                        ),
                        RelationalDbQueryUtils.enquoteIdentifier(
                            COL_LAST_NAME_WITH_SPACE,
                            identifierQuoteString,
                        ),
                    ),
                )
            connection
                .createStatement()
                .execute(
                    String.format(
                        "INSERT INTO %s(id, %s) VALUES (3, 'vash')",
                        getFullyQualifiedTableName(
                            RelationalDbQueryUtils.enquoteIdentifier(
                                tableNameWithSpaces,
                                identifierQuoteString,
                            ),
                        ),
                        RelationalDbQueryUtils.enquoteIdentifier(
                            COL_LAST_NAME_WITH_SPACE,
                            identifierQuoteString,
                        ),
                    ),
                )
        }
        return CatalogHelpers.createConfiguredAirbyteStream(
            streamName2,
            defaultNamespace,
            Field.of(COL_ID, JsonSchemaType.NUMBER),
            Field.of(COL_LAST_NAME_WITH_SPACE, JsonSchemaType.STRING),
        )
    }

    fun getFullyQualifiedTableName(tableName: String): String {
        return RelationalDbQueryUtils.getFullyQualifiedTableName(defaultSchemaName, tableName)
    }

    protected fun createSchemas() {
        if (supportsSchemas()) {
            for (schemaName in TEST_SCHEMAS) {
                testdb.with("CREATE SCHEMA %s;", schemaName)
            }
        }
    }

    private fun convertIdBasedOnDatabase(idValue: Int): JsonNode {
        return when (testdb.databaseDriver) {
            DatabaseDriver.ORACLE,
            DatabaseDriver.SNOWFLAKE -> Jsons.jsonNode(BigDecimal.valueOf(idValue.toLong()))
            else -> Jsons.jsonNode(idValue)
        }
    }

    private val defaultSchemaName: String?
        get() = if (supportsSchemas()) SCHEMA_NAME else null

    protected val defaultNamespace: String
        get() =
            when (testdb.databaseDriver) {
                DatabaseDriver.MYSQL,
                DatabaseDriver.CLICKHOUSE,
                DatabaseDriver.TERADATA -> testdb.databaseName
                else -> SCHEMA_NAME
            }

    /**
     * Creates empty state with the provided stream name and namespace.
     *
     * @param streamName The stream name.
     * @param streamNamespace The stream namespace.
     * @return [JsonNode] representation of the generated empty state.
     */
    protected fun createEmptyState(streamName: String?, streamNamespace: String?): JsonNode {
        val airbyteStateMessage =
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                .withStream(
                    AirbyteStreamState()
                        .withStreamDescriptor(
                            StreamDescriptor().withName(streamName).withNamespace(streamNamespace),
                        ),
                )
        return Jsons.jsonNode(java.util.List.of(airbyteStateMessage))
    }

    protected fun createState(
        streamName: String?,
        streamNamespace: String?,
        stateData: JsonNode?
    ): JsonNode {
        val airbyteStateMessage =
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                .withStream(
                    AirbyteStreamState()
                        .withStreamDescriptor(
                            StreamDescriptor().withName(streamName).withNamespace(streamNamespace),
                        )
                        .withStreamState(stateData),
                )
        return Jsons.jsonNode(java.util.List.of(airbyteStateMessage))
    }

    protected fun extractState(airbyteMessage: AirbyteMessage): JsonNode {
        return Jsons.jsonNode(java.util.List.of(airbyteMessage.state))
    }

    protected fun createStateMessage(
        streamNamespace: String,
        streamName: String,
        jsonStreamState: JsonNode,
        recordCount: Long
    ): AirbyteMessage {
        return AirbyteMessage()
            .withType(AirbyteMessage.Type.STATE)
            .withState(
                AirbyteStateMessage()
                    .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                    .withStream(
                        AirbyteStreamState()
                            .withStreamDescriptor(
                                StreamDescriptor()
                                    .withNamespace(streamNamespace)
                                    .withName(streamName),
                            )
                            .withStreamState(jsonStreamState),
                    )
                    .withSourceStats(AirbyteStateStats().withRecordCount(recordCount.toDouble())),
            )
    }

    protected fun createStateMessage(
        dbStreamState: DbStreamState,
        legacyStates: List<DbStreamState>?,
        recordCount: Long
    ): AirbyteMessage {
        return AirbyteMessage()
            .withType(AirbyteMessage.Type.STATE)
            .withState(
                AirbyteStateMessage()
                    .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                    .withStream(
                        AirbyteStreamState()
                            .withStreamDescriptor(
                                StreamDescriptor()
                                    .withNamespace(dbStreamState.streamNamespace)
                                    .withName(dbStreamState.streamName),
                            )
                            .withStreamState(Jsons.jsonNode(dbStreamState)),
                    )
                    .withData(Jsons.jsonNode(DbState().withCdc(false).withStreams(legacyStates)))
                    .withSourceStats(AirbyteStateStats().withRecordCount(recordCount.toDouble())),
            )
    }

    protected fun extractSpecificFieldFromCombinedMessages(
        messages: List<AirbyteMessage>,
        streamName: String,
        field: String?
    ): List<String> {
        return extractStateMessage(messages)
            .filter { s: AirbyteStateMessage -> s.stream.streamDescriptor.name == streamName }
            .map { s: AirbyteStateMessage ->
                if (s.stream.streamState[field] != null) s.stream.streamState[field].asText()
                else ""
            }
    }

    protected fun filterRecords(messages: List<AirbyteMessage>): List<AirbyteMessage> {
        return messages.filter { r: AirbyteMessage -> r.type == AirbyteMessage.Type.RECORD }
    }

    protected fun extractStateMessage(messages: List<AirbyteMessage>): List<AirbyteStateMessage> {
        return messages
            .filter { r: AirbyteMessage -> r.type == AirbyteMessage.Type.STATE }
            .map { obj: AirbyteMessage -> obj.state }
    }

    protected fun extractStateMessage(
        messages: List<AirbyteMessage>,
        streamName: String
    ): List<AirbyteStateMessage> {
        return messages
            .filter { r: AirbyteMessage ->
                r.type == AirbyteMessage.Type.STATE &&
                    r.state.stream.streamDescriptor.name == streamName
            }
            .map { obj: AirbyteMessage -> obj.state }
    }

    protected fun createRecord(
        stream: String?,
        namespace: String?,
        data: Map<Any, Any>
    ): AirbyteMessage {
        return AirbyteMessage()
            .withType(AirbyteMessage.Type.RECORD)
            .withRecord(
                AirbyteRecordMessage()
                    .withData(Jsons.jsonNode(data))
                    .withStream(stream)
                    .withNamespace(namespace),
            )
    }

    companion object {
        @JvmField val SCHEMA_NAME: String = "jdbc_integration_test1"
        @JvmField val SCHEMA_NAME2: String = "jdbc_integration_test2"
        @JvmField val TEST_SCHEMAS: Set<String> = java.util.Set.of(SCHEMA_NAME, SCHEMA_NAME2)

        @JvmField val TABLE_NAME: String = "id_and_name"
        @JvmField val TABLE_NAME_WITH_SPACES: String = "id and name"
        @JvmField val TABLE_NAME_WITHOUT_PK: String = "id_and_name_without_pk"
        @JvmField val TABLE_NAME_COMPOSITE_PK: String = "full_name_composite_pk"
        @JvmField val TABLE_NAME_WITHOUT_CURSOR_TYPE: String = "table_without_cursor_type"
        @JvmField val TABLE_NAME_WITH_NULLABLE_CURSOR_TYPE: String = "table_with_null_cursor_type"

        // this table is used in testing incremental sync with concurrent insertions
        @JvmField val TABLE_NAME_AND_TIMESTAMP: String = "name_and_timestamp"

        @JvmField val COL_ID: String = "id"
        @JvmField val COL_NAME: String = "name"
        @JvmField val COL_UPDATED_AT: String = "updated_at"
        @JvmField val COL_FIRST_NAME: String = "first_name"
        @JvmField val COL_LAST_NAME: String = "last_name"
        @JvmField val COL_LAST_NAME_WITH_SPACE: String = "last name"
        @JvmField val COL_CURSOR: String = "cursor_field"
        @JvmField val COL_TIMESTAMP: String = "timestamp"
        @JvmField val ID_VALUE_1: Number = 1
        @JvmField val ID_VALUE_2: Number = 2
        @JvmField val ID_VALUE_3: Number = 3
        @JvmField val ID_VALUE_4: Number = 4
        @JvmField val ID_VALUE_5: Number = 5

        @JvmField val DROP_SCHEMA_QUERY: String = "DROP SCHEMA IF EXISTS %s CASCADE"
        @JvmField
        val CREATE_TABLE_WITH_NULLABLE_CURSOR_TYPE_QUERY: String =
            "CREATE TABLE %s (%s VARCHAR(20));"
        @JvmField
        val INSERT_TABLE_WITH_NULLABLE_CURSOR_TYPE_QUERY: String =
            "INSERT INTO %s VALUES('Hello world :)');"
        @JvmField
        val INSERT_TABLE_NAME_AND_TIMESTAMP_QUERY: String =
            "INSERT INTO %s (name, timestamp) VALUES ('%s', '%s')"

        @JvmField protected var COL_TIMESTAMP_TYPE: String = "TIMESTAMP"
        @JvmField
        protected var COLUMN_CLAUSE_WITH_PK: String =
            "id INTEGER, name VARCHAR(200) NOT NULL, updated_at DATE NOT NULL"
        @JvmField
        protected var COLUMN_CLAUSE_WITHOUT_PK: String =
            "id INTEGER, name VARCHAR(200) NOT NULL, updated_at DATE NOT NULL"
        @JvmField
        protected var COLUMN_CLAUSE_WITH_COMPOSITE_PK: String =
            "first_name VARCHAR(200) NOT NULL, last_name VARCHAR(200) NOT NULL, updated_at DATE NOT NULL"

        @JvmField
        var CREATE_TABLE_WITHOUT_CURSOR_TYPE_QUERY: String = "CREATE TABLE %s (%s bit NOT NULL);"
        @JvmField var INSERT_TABLE_WITHOUT_CURSOR_TYPE_QUERY: String = "INSERT INTO %s VALUES(0);"

        @JvmStatic
        protected fun setEmittedAtToNull(messages: Iterable<AirbyteMessage>) {
            for (actualMessage in messages) {
                if (actualMessage.record != null) {
                    actualMessage.record.emittedAt = null
                }
            }
        }

        @JvmStatic
        protected fun setTraceEmittedAtToNull(traceMessages: Iterable<AirbyteMessage>) {
            for (traceMessage in traceMessages) {
                if (traceMessage.trace != null) {
                    traceMessage.trace.emittedAt = null
                }
            }
        }
    }
}
