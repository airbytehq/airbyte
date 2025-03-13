/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.Lists
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.*
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.IOException
import java.sql.SQLException
import java.util.function.Consumer
import org.apache.commons.lang3.StringUtils
import org.jooq.DSLContext
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

private val LOGGER = KotlinLogging.logger {}

/**
 * This abstract class contains common helpers and boilerplate for comprehensively testing that all
 * data types in a source can be read and handled correctly by the connector and within Airbyte's
 * type system.
 */
abstract class AbstractSourceDatabaseTypeTest : AbstractSourceConnectorTest() {
    @JvmField protected val testDataHolders: MutableList<TestDataHolder> = ArrayList()
    @JvmField protected var database: Database? = null

    protected val idColumnName: String
        /**
         * The column name will be used for a PK column in the test tables. Override it if default
         * name is not valid for your source.
         *
         * @return Id column name
         */
        get() = "id"

    protected val testColumnName: String
        /**
         * The column name will be used for a test column in the test tables. Override it if default
         * name is not valid for your source.
         *
         * @return Test column name
         */
        get() = "test_column"

    /**
     * Setup the test database. All tables and data described in the registered tests will be put
     * there.
     *
     * @return configured test database
     * @throws Exception
     * - might throw any exception during initialization.
     */
    @Throws(Exception::class) protected abstract fun setupDatabase(): Database?

    /** Put all required tests here using method [.addDataTypeTestData] */
    protected abstract fun initTests()

    @Throws(Exception::class)
    override fun setupEnvironment(environment: TestDestinationEnv?) {
        database = setupDatabase()
        initTests()
        createTables()
        populateTables()
    }

    protected abstract val nameSpace: String

    /**
     * Test the 'discover' command. TODO (liren): Some existing databases may fail testDataTypes(),
     * so it is turned off by default. It should be enabled for all databases eventually.
     */
    protected open fun testCatalog(): Boolean {
        return false
    }

    /**
     * The test checks that the types from the catalog matches the ones discovered from the source.
     * This test is disabled by default. To enable it you need to overwrite testCatalog() function.
     */
    @Test
    @Throws(Exception::class)
    fun testDataTypes() {
        if (testCatalog()) {
            runDiscover()
            val streams = lastPersistedCatalog.streams.associateBy { it.name }

            // testDataHolders should be initialized using the `addDataTypeTestData` function
            testDataHolders.forEach(
                Consumer { testDataHolder: TestDataHolder ->
                    val airbyteStream = streams[testDataHolder.nameWithTestPrefix]
                    @Suppress("unchecked_cast")
                    val jsonSchemaTypeMap =
                        Jsons.deserialize(
                            airbyteStream!!.jsonSchema["properties"][testColumnName].toString(),
                            MutableMap::class.java
                        ) as Map<String, Any>
                    Assertions.assertEquals(
                        testDataHolder.airbyteType.jsonSchemaTypeMap,
                        jsonSchemaTypeMap,
                        "Expected column type for " + testDataHolder.nameWithTestPrefix
                    )
                }
            )
        }
    }

    /**
     * The test checks that connector can fetch prepared data without failure. It uses a prepared
     * catalog and read the source using that catalog. Then makes sure that the expected values are
     * the ones inserted in the source.
     */
    @Test
    @Throws(Exception::class)
    open fun testDataContent() {
        // Class used to make easier the error reporting
        class MissedRecords( // Stream that is missing any value
            var streamName:
                String?, // Which are the values that has not being gathered from the source
            var missedValues: List<String?>
        )

        class UnexpectedRecord(val streamName: String, val unexpectedValue: String?)

        val catalog = configuredCatalog
        val allMessages = runRead(catalog)

        val recordMessages =
            allMessages.filter { m: AirbyteMessage -> m.type == AirbyteMessage.Type.RECORD }

        val expectedValues: MutableMap<String, MutableList<String?>> = HashMap()
        val missedValuesByStream: MutableMap<String, ArrayList<MissedRecords>> = HashMap()
        val unexpectedValuesByStream: MutableMap<String, MutableList<UnexpectedRecord>> = HashMap()
        val testByName: MutableMap<String, TestDataHolder> = HashMap()

        // If there is no expected value in the test set we don't include it in the list to be
        // asserted
        // (even if the table contains records)
        testDataHolders.forEach(
            Consumer { testDataHolder: TestDataHolder ->
                if (!testDataHolder.expectedValues.isEmpty()) {
                    expectedValues[testDataHolder.nameWithTestPrefix] =
                        testDataHolder.expectedValues
                    testByName[testDataHolder.nameWithTestPrefix] = testDataHolder
                } else {
                    LOGGER.warn("Missing expected values for type: " + testDataHolder.sourceType)
                }
            }
        )

        for (message in recordMessages) {
            val streamName = message.record.stream
            val expectedValuesForStream = expectedValues[streamName]
            if (expectedValuesForStream != null) {
                val value = getValueFromJsonNode(message.record.data[testColumnName])
                if (!expectedValuesForStream.contains(value)) {
                    unexpectedValuesByStream.putIfAbsent(streamName, ArrayList())
                    unexpectedValuesByStream[streamName]!!.add(UnexpectedRecord(streamName, value))
                } else {
                    expectedValuesForStream.remove(value)
                }
            }
        }

        // Gather all the missing values, so we don't stop the test in the first missed one
        expectedValues.forEach { (streamName: String, values: List<String?>) ->
            if (values.isNotEmpty()) {
                missedValuesByStream.putIfAbsent(streamName, ArrayList())
                missedValuesByStream[streamName]!!.add(MissedRecords(streamName, values))
            }
        }

        val errorsByStream: MutableMap<String?, MutableList<String>> = HashMap()
        for (streamName in unexpectedValuesByStream.keys) {
            errorsByStream.putIfAbsent(streamName, ArrayList())
            val test = testByName.getValue(streamName)
            val unexpectedValues: List<UnexpectedRecord> = unexpectedValuesByStream[streamName]!!
            for (unexpectedValue in unexpectedValues) {
                errorsByStream[streamName]!!.add(
                    "The stream '${streamName}' checking type '${test.sourceType}' initialized " +
                        "at ${test.declarationLocation} got unexpected values: $unexpectedValue"
                )
            }
        }

        for (streamName in missedValuesByStream.keys) {
            errorsByStream.putIfAbsent(streamName, ArrayList())
            val test = testByName.getValue(streamName)
            val missedValues: List<MissedRecords> = missedValuesByStream[streamName]!!
            for (missedValue in missedValues) {
                errorsByStream[streamName]!!.add(
                    "The stream '$streamName' checking type '${test.sourceType}' initialized at " +
                        "${test.declarationLocation} is missing values: $missedValue"
                )
            }
        }

        val errorStrings: MutableList<String> = ArrayList()
        for (errors in errorsByStream.values) {
            errorStrings.add(StringUtils.join(errors, "\n"))
        }

        Assertions.assertTrue(errorsByStream.isEmpty(), StringUtils.join(errorStrings, "\n"))
    }

    @Throws(IOException::class)
    protected fun getValueFromJsonNode(jsonNode: JsonNode?): String? {
        if (jsonNode != null) {
            if (jsonNode.isArray) {
                return jsonNode.toString()
            }

            var value =
                (if (jsonNode.isBinary) jsonNode.binaryValue().contentToString()
                else jsonNode.asText())
            value = (if (value != null && value == "null") null else value)
            return value
        }
        return null
    }

    /**
     * Creates all tables and insert data described in the registered data type tests.
     *
     * @throws Exception might raise exception if configuration goes wrong or tables creation/insert
     * scripts failed.
     */
    @Throws(Exception::class)
    protected open fun createTables() {
        for (test in testDataHolders) {
            database!!.query<Any?> { ctx: DSLContext ->
                ctx.fetch(test.createSqlQuery)
                LOGGER.info("Table {} is created.", test.nameWithTestPrefix)
                null
            }
        }
    }

    @Throws(Exception::class)
    protected open fun populateTables() {
        for (test in testDataHolders) {
            database!!.query<Any?> { ctx: DSLContext ->
                test.insertSqlQueries.forEach(Consumer { sql: String -> ctx.fetch(sql) })
                LOGGER.info(
                    "Inserted {} rows in Ttable {}",
                    test.insertSqlQueries.size,
                    test.nameWithTestPrefix
                )
                null
            }
        }
    }

    protected val configuredCatalog: ConfiguredAirbyteCatalog
        /**
         * Configures streams for all registered data type tests.
         *
         * @return configured catalog
         */
        get() =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    testDataHolders.map { test: TestDataHolder ->
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withCursorField(Lists.newArrayList(idColumnName))
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withStream(
                                CatalogHelpers.createAirbyteStream(
                                        String.format("%s", test.nameWithTestPrefix),
                                        String.format("%s", nameSpace),
                                        Field.of(idColumnName, JsonSchemaType.INTEGER),
                                        Field.of(testColumnName, test.airbyteType)
                                    )
                                    .withSourceDefinedCursor(true)
                                    .withSourceDefinedPrimaryKey(
                                        java.util.List.of(java.util.List.of(idColumnName))
                                    )
                                    .withSupportedSyncModes(
                                        Lists.newArrayList(
                                            SyncMode.FULL_REFRESH,
                                            SyncMode.INCREMENTAL
                                        )
                                    )
                            )
                    }
                )

    /**
     * Register your test in the run scope. For each test will be created a table with one column of
     * specified type. Note! If you register more than one test with the same type name, they will
     * be run as independent tests with own streams.
     *
     * @param test comprehensive data type test
     */
    fun addDataTypeTestData(test: TestDataHolder) {
        testDataHolders.add(test)
        test.setTestNumber(
            testDataHolders.filter { t: TestDataHolder -> t.sourceType == test.sourceType }.count()
        )
        test.nameSpace = nameSpace
        test.setIdColumnName(idColumnName)
        test.setTestColumnName(testColumnName)
        test.setDeclarationLocation(Thread.currentThread().stackTrace)
    }

    private fun formatCollection(collection: Collection<String?>): String {
        return collection.joinToString(", ") { s: String? -> "`$s`" }
    }

    val markdownTestTable: String
        /**
         * Builds a table with all registered test cases with values using Markdown syntax (can be
         * used in the github).
         *
         * @return formatted list of test cases
         */
        get() {
            val table =
                StringBuilder()
                    .append(
                        "|**Data Type**|**Insert values**|**Expected values**|**Comment**|**Common test result**|\n"
                    )
                    .append("|----|----|----|----|----|\n")

            testDataHolders.forEach(
                Consumer { test: TestDataHolder ->
                    table.append(
                        String.format(
                            "| %s | %s | %s | %s | %s |\n",
                            test.sourceType,
                            formatCollection(test.values),
                            formatCollection(test.expectedValues),
                            "",
                            "Ok"
                        )
                    )
                }
            )
            return table.toString()
        }

    protected fun printMarkdownTestTable() {
        LOGGER.info(markdownTestTable)
    }

    @Throws(SQLException::class)
    protected fun createDummyTableWithData(database: Database): ConfiguredAirbyteStream {
        database.query<Any?> { ctx: DSLContext ->
            ctx.fetch(
                "CREATE TABLE " +
                    nameSpace +
                    ".random_dummy_table(id INTEGER PRIMARY KEY, test_column VARCHAR(63));"
            )
            ctx.fetch("INSERT INTO " + nameSpace + ".random_dummy_table VALUES (2, 'Random Data');")
            null
        }

        return ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(
                CatalogHelpers.createAirbyteStream(
                        "random_dummy_table",
                        nameSpace,
                        Field.of("id", JsonSchemaType.INTEGER),
                        Field.of("test_column", JsonSchemaType.STRING)
                    )
                    .withSourceDefinedCursor(true)
                    .withSupportedSyncModes(
                        Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
                    )
                    .withSourceDefinedPrimaryKey(java.util.List.of(listOf("id")))
            )
    }

    protected fun extractStateMessages(messages: List<AirbyteMessage>): List<AirbyteStateMessage> {
        return messages
            .filter { r: AirbyteMessage -> r.type == AirbyteMessage.Type.STATE }
            .map { obj: AirbyteMessage -> obj.state }
    }
}
