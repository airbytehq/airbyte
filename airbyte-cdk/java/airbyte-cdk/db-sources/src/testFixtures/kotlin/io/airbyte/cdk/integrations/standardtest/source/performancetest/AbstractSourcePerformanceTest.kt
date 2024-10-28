/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.source.performancetest

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.Lists
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.*
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.stream.Stream
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.TestInstance
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

private val LOGGER = KotlinLogging.logger {}

/** This abstract class contains common methods for Performance tests. */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
abstract class AbstractSourcePerformanceTest : AbstractSourceBasePerformanceTest() {
    override var config: JsonNode? = null
    /**
     * The column name will be used for a PK column in the test tables. Override it if default name
     * is not valid for your source.
     */
    protected val idColumnName: String = "id"

    /**
     * Setup the test database. All tables and data described in the registered tests will be put
     * there.
     *
     * @throws Exception
     * - might throw any exception during initialization.
     */
    @Throws(Exception::class) protected abstract fun setupDatabase(dbName: String?)

    override fun tearDown(testEnv: TestDestinationEnv?) {}

    /**
     * This is a data provider for performance tests, Each argument's group would be ran as a
     * separate test. Set the "testArgs" in test class of your DB in @BeforeTest method.
     *
     * 1st arg - a name of DB that will be used in jdbc connection string. 2nd arg - a schemaName
     * that will be ised as a NameSpace in Configured Airbyte Catalog. 3rd arg - a number of
     * expected records retrieved in each stream. 4th arg - a number of columns in each stream\table
     * that will be used for Airbyte Cataloq configuration 5th arg - a number of streams to read in
     * configured airbyte Catalog. Each stream\table in DB should be names like "test_0",
     * "test_1",..., test_n.
     *
     * Example: Stream.of( Arguments.of("test1000tables240columns200recordsDb", "dbo", 200, 240,
     * 1000), Arguments.of("test5000tables240columns200recordsDb", "dbo", 200, 240, 1000),
     * Arguments.of("newregular25tables50000records", "dbo", 50052, 8, 25),
     * Arguments.of("newsmall1000tableswith10000rows", "dbo", 10011, 8, 1000) );
     */
    protected abstract fun provideParameters(): Stream<Arguments>?

    @ParameterizedTest
    @MethodSource("provideParameters")
    @Throws(Exception::class)
    fun testPerformance(
        dbName: String?,
        schemaName: String?,
        numberOfDummyRecords: Int,
        numberOfColumns: Int,
        numberOfStreams: Int
    ) {
        setupDatabase(dbName)

        val catalog = getConfiguredCatalog(schemaName, numberOfStreams, numberOfColumns)
        val mapOfExpectedRecordsCount =
            prepareMapWithExpectedRecords(numberOfStreams, numberOfDummyRecords)
        val checkStatusMap =
            runReadVerifyNumberOfReceivedMsgs(catalog, null, mapOfExpectedRecordsCount)
        validateNumberOfReceivedMsgs(checkStatusMap)
    }

    protected fun validateNumberOfReceivedMsgs(checkStatusMap: Map<String, Int>) {
        // Iterate through all streams map and check for streams where
        val failedStreamsMap = checkStatusMap.filterValues { it != 0 }

        if (failedStreamsMap.isNotEmpty()) {
            Assertions.fail<Any>("Non all messages were delivered. $failedStreamsMap")
        }
        LOGGER.info("Finished all checks, no issues found for {} of streams", checkStatusMap.size)
    }

    protected fun prepareMapWithExpectedRecords(
        streamNumber: Int,
        expectedRecordsNumberInEachStream: Int
    ): MutableMap<String, Int> {
        val resultMap: MutableMap<String, Int> = HashMap() // streamName&expected records in stream

        for (currentStream in 0 until streamNumber) {
            val streamName = String.format(testStreamNameTemplate, currentStream)
            resultMap[streamName] = expectedRecordsNumberInEachStream
        }
        return resultMap
    }

    /**
     * Configures streams for all registered data type tests.
     *
     * @return configured catalog
     */
    protected fun getConfiguredCatalog(
        nameSpace: String?,
        numberOfStreams: Int,
        numberOfColumns: Int
    ): ConfiguredAirbyteCatalog {
        val streams: MutableList<ConfiguredAirbyteStream> = ArrayList()

        for (currentStream in 0 until numberOfStreams) {
            // CREATE TABLE test.test_1_int(id INTEGER PRIMARY KEY, test_column int)

            val fields: MutableList<Field> = ArrayList()

            fields.add(Field.of(this.idColumnName, JsonSchemaType.NUMBER))
            for (currentColumnNumber in 0 until numberOfColumns) {
                fields.add(Field.of(testColumnName + currentColumnNumber, JsonSchemaType.STRING))
            }

            val airbyteStream =
                CatalogHelpers.createAirbyteStream(
                        String.format(testStreamNameTemplate, currentStream),
                        nameSpace,
                        fields
                    )
                    .withSourceDefinedCursor(true)
                    .withSourceDefinedPrimaryKey(
                        java.util.List.of<List<String>>(
                            java.util.List.of<String>(this.idColumnName)
                        )
                    )
                    .withSupportedSyncModes(
                        Lists.newArrayList<SyncMode>(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
                    )

            val configuredAirbyteStream =
                ConfiguredAirbyteStream()
                    .withSyncMode(SyncMode.INCREMENTAL)
                    .withCursorField(Lists.newArrayList<String>(this.idColumnName))
                    .withDestinationSyncMode(DestinationSyncMode.APPEND)
                    .withStream(airbyteStream)

            streams.add(configuredAirbyteStream)
        }

        return ConfiguredAirbyteCatalog().withStreams(streams)
    }

    companion object {}
}
