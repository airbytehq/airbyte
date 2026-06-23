/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.test.fixtures.tests

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.ClockFactory
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.test.fixtures.cleanup.TestAssetResourceNamer
import io.airbyte.cdk.test.fixtures.connector.IntegrationTestOperations
import io.airbyte.cdk.test.fixtures.connector.TestDbExecutor
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.SyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.DynamicContainer
import org.junit.jupiter.api.DynamicNode
import org.junit.jupiter.api.DynamicTest
import org.junit.jupiter.api.TestFactory
import org.junit.jupiter.api.Timeout
import org.junit.jupiter.api.function.Executable

abstract class CursorBasedSyncTest {
    private val log = KotlinLogging.logger {}

    abstract val configSpec: ConfigurationSpecification
    abstract val executor: TestDbExecutor
    abstract val setupDdl: List<String>
    abstract val testCases: List<TestCase>

    @TestFactory
    @Timeout(300)
    fun tests(): Iterable<DynamicNode> {
        log.info { "Executing setup DDL statements." }
        for (stmt in setupDdl) {
            executor.executeUpdate(stmt)
        }
        log.info { "Inserting initial rows." }
        for (stmt in testCases.flatMap { it.initialDml }) {
            executor.executeUpdate(stmt)
        }
        val actual = DiscoverAndSyncAll(IntegrationTestOperations(configSpec), executor, testCases)
        val discoverAndSyncAllTest = DynamicTest.dynamicTest("discover-and-sync-all", actual)
        val testCaseNodes =
            testCases.map {
                DynamicContainer.dynamicContainer(it.testName, dynamicTests(actual, it))
            }
        return listOf(discoverAndSyncAllTest) + testCaseNodes
    }

    private fun dynamicTests(actual: DiscoverAndSyncAll, testCase: TestCase): List<DynamicTest> {
        return listOf(
            DynamicTest.dynamicTest("sync1-records") {
                assertRecords(
                    "sync1",
                    testCase,
                    actual.sync1MessagesByStream,
                    testCase.expectedSync1Values
                )
            },
            DynamicTest.dynamicTest("sync2-records") {
                assertRecords(
                    "sync2",
                    testCase,
                    actual.sync2MessagesByStream,
                    testCase.expectedSync2Values
                )
            },
        )
    }

    private fun assertRecords(
        syncLabel: String,
        testCase: TestCase,
        messagesByStream: Map<String, BufferingOutputConsumer>,
        expectedJsonValues: List<String>,
    ) {
        val consumer = messagesByStream[testCase.tableName.uppercase()]
        Assertions.assertNotNull(consumer)
        val actualRecords = extractCursorFieldData(consumer!!.records(), testCase.cursorField)
        val expectedRecords =
            expectedJsonValues.map { Jsons.readTree("""{"${testCase.cursorField}":$it}""") }
        log.info {
            "$syncLabel ${testCase.testName}: emitted records ${Jsons.writeValueAsString(sortedRecords(actualRecords))}"
        }
        Assertions.assertEquals(
            Jsons.writeValueAsString(sortedRecords(expectedRecords)),
            Jsons.writeValueAsString(sortedRecords(actualRecords)),
        )
    }

    private fun extractCursorFieldData(
        records: List<AirbyteRecordMessage>,
        cursorField: String,
    ): List<JsonNode> =
        records.mapNotNull { record ->
            val data = record.data as? ObjectNode ?: return@mapNotNull null
            data.deepCopy().apply {
                for (fieldName in data.fieldNames()) {
                    if (fieldName != cursorField) remove(fieldName)
                }
            }
        }

    private fun sortedRecords(records: List<JsonNode>): JsonNode =
        Jsons.createArrayNode().apply { addAll(records.sortedBy { it.toString() }) }

    class DiscoverAndSyncAll(
        private val ops: IntegrationTestOperations,
        private val executor: TestDbExecutor,
        private val testCases: List<TestCase>,
    ) : Executable {
        private val log = KotlinLogging.logger {}

        lateinit var sync1MessagesByStream: Map<String, BufferingOutputConsumer>
        lateinit var sync2MessagesByStream: Map<String, BufferingOutputConsumer>

        override fun execute() {
            log.info { "Running JDBC DISCOVER operation." }
            val streams = ops.discover()
            val catalog = configuredCatalog(streams)

            log.info { "Running JDBC READ (sync 1)." }
            val sync1Output = ops.read(catalog)
            Assertions.assertNotEquals(emptyList<AirbyteStateMessage>(), sync1Output.states())
            Assertions.assertNotEquals(emptyList<AirbyteRecordMessage>(), sync1Output.records())
            sync1MessagesByStream = byStream(sync1Output.messages())

            log.info { "Inserting additional rows." }
            for (stmt in testCases.flatMap { it.additionalDml }) {
                executor.executeUpdate(stmt)
            }

            log.info { "Running JDBC READ (sync 2)." }
            val sync2Output = ops.read(catalog, sync1Output.states())
            sync2MessagesByStream = byStream(sync2Output.messages())

            log.info { "Done." }
        }

        private fun configuredCatalog(
            streams: Map<String, AirbyteStream>
        ): ConfiguredAirbyteCatalog {
            val configuredStreams =
                testCases.mapNotNull { testCase ->
                    streams[testCase.tableName]?.let { stream ->
                        CatalogHelpers.toDefaultConfiguredStream(stream)
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withCursorField(listOf(testCase.cursorField))
                    }
                }
            return ConfiguredAirbyteCatalog().withStreams(configuredStreams)
        }

        private fun byStream(messages: List<AirbyteMessage>): Map<String, BufferingOutputConsumer> {
            val result =
                testCases.associate {
                    it.tableName.uppercase() to BufferingOutputConsumer(ClockFactory().fixed())
                }
            for (msg in messages) {
                result[streamName(msg) ?: continue]?.accept(msg)
            }
            return result
        }

        private fun streamName(msg: AirbyteMessage): String? =
            when (msg.type) {
                AirbyteMessage.Type.RECORD -> msg.record?.stream
                AirbyteMessage.Type.STATE -> msg.state?.stream?.streamDescriptor?.name
                AirbyteMessage.Type.TRACE ->
                    when (msg.trace?.type) {
                        AirbyteTraceMessage.Type.ERROR -> msg.trace?.error?.streamDescriptor?.name
                        AirbyteTraceMessage.Type.ESTIMATE -> msg.trace?.estimate?.name
                        AirbyteTraceMessage.Type.STREAM_STATUS ->
                            msg.trace?.streamStatus?.streamDescriptor?.name
                        AirbyteTraceMessage.Type.ANALYTICS -> null
                        null -> null
                    }
                else -> null
            }
    }

    data class TestCase(
        val namespace: String,
        val sqlType: String,
        val cursorField: String,
        // SQL literal → expected JSON output, inserted before sync 1; all must appear in sync 1
        val initialRows: Map<String, String>,
        // SQL literal → expected JSON output, inserted before sync 1 at the max cursor value;
        // must appear in both sync 1 and sync 2 due to the >= lower bound used by the bulk CDK
        val boundaryRows: Map<String, String> = emptyMap(),
        // SQL literal → expected JSON output, inserted between syncs; all must appear in sync 2
        val additionalRows: Map<String, String>,
        val testName: String =
            sqlType
                .replace("\\[]".toRegex(), " array")
                .replace("[^a-zA-Z0-9]".toRegex(), " ")
                .trim()
                .replace(" +".toRegex(), "_")
                .uppercase(),
    ) {
        companion object {
            val testAssetResourceNamer = TestAssetResourceNamer()
        }

        val tableName: String = testAssetResourceNamer.getName()

        val initialDml: List<String>
            get() =
                (initialRows.keys + boundaryRows.keys).map {
                    "INSERT INTO \"$namespace\".\"$tableName\" (\"$cursorField\") VALUES ($it)"
                }

        val additionalDml: List<String>
            get() =
                additionalRows.keys.map {
                    "INSERT INTO \"$namespace\".\"$tableName\" (\"$cursorField\") VALUES ($it)"
                }

        val expectedSync1Values: List<String>
            get() = initialRows.values.toList() + boundaryRows.values.toList()

        val expectedSync2Values: List<String>
            get() = boundaryRows.values.toList() + additionalRows.values.toList()
    }
}
