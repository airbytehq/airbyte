/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.ClockFactory
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteLogMessage
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.DynamicContainer
import org.junit.jupiter.api.DynamicNode
import org.junit.jupiter.api.DynamicTest
import org.junit.jupiter.api.function.Executable
import org.testcontainers.containers.GenericContainer

class DynamicDatatypeTestFactory<
    DB : GenericContainer<*>,
    CS : ConfigurationSpecification,
    C : SourceConfiguration,
    F : SourceConfigurationFactory<CS, C>,
    T : DatatypeTestCase,
>(
    val ops: DatatypeTestOperations<DB, CS, C, F, T>,
) {
    private val log = KotlinLogging.logger {}

    fun build(dbContainer: DB): Iterable<DynamicNode> {
        val actual = DiscoverAndReadAll(ops) { dbContainer }
        val discoverAndReadAllTest: DynamicNode =
            DynamicTest.dynamicTest("discover-and-read-all", actual)
        val testCases: List<DynamicNode> =
            ops.testCases.map { (id: String, testCase: T) ->
                DynamicContainer.dynamicContainer(id, dynamicTests(actual, testCase))
            }
        return listOf(discoverAndReadAllTest) + testCases
    }

    private fun dynamicTests(
        actual: DiscoverAndReadAll<DB, CS, C, F, T>,
        testCase: T
    ): List<DynamicTest> {
        val streamTests: List<DynamicTest> =
            if (!testCase.isStream) emptyList()
            else
                listOf(
                    DynamicTest.dynamicTest("discover-stream") {
                        discover(testCase, actual.streamCatalog[testCase.id])
                    },
                    DynamicTest.dynamicTest("records-stream") {
                        records(testCase, actual.streamMessagesByStream[testCase.id])
                    },
                )
        val globalTests: List<DynamicTest> =
            if (!ops.withGlobal || !testCase.isGlobal) emptyList()
            else
                listOf(
                    DynamicTest.dynamicTest("discover-global") {
                        discover(testCase, actual.globalCatalog[testCase.id])
                    },
                    DynamicTest.dynamicTest("records-global") {
                        records(testCase, actual.globalMessagesByStream[testCase.id])
                    },
                )
        return streamTests + globalTests
    }

    private fun discover(testCase: T, actualStream: AirbyteStream?) {
        Assertions.assertNotNull(actualStream)
        log.info {
            val streamJson: JsonNode = Jsons.valueToTree(actualStream)
            "test case ${testCase.id}: discovered stream $streamJson"
        }
        val jsonSchema: JsonNode = actualStream!!.jsonSchema?.get("properties")!!
        val actualSchema: JsonNode? = jsonSchema[testCase.fieldName]
        Assertions.assertNotNull(actualSchema)
        val expectedSchema: JsonNode = testCase.expectedAirbyteSchemaType.asJsonSchema()
        Assertions.assertEquals(expectedSchema, actualSchema)
    }

    private fun records(testCase: T, actualRead: BufferingOutputConsumer?) {
        Assertions.assertNotNull(actualRead)
        val actualRecords: List<AirbyteRecordMessage> = actualRead?.records() ?: emptyList()
        val actual: String =
            actualRecords
                .mapNotNull { actualFieldData(testCase, it) }
                .sorted()
                .joinToString(separator = ",", prefix = "[", postfix = "]")
        log.info { "test case ${testCase.id}: emitted records $actual" }
        val expected: String =
            testCase.expectedData
                .sorted()
                .joinToString(separator = ",", prefix = "[", postfix = "]")
        Assertions.assertEquals(expected, actual)
    }

    private fun actualFieldData(testCase: T, record: AirbyteRecordMessage): String? {
        val data: ObjectNode = record.data as? ObjectNode ?: return null
        val result: ObjectNode = data.deepCopy()
        for (fieldName in data.fieldNames()) {
            if (fieldName.equals(testCase.fieldName, ignoreCase = true)) continue
            result.remove(fieldName)
        }
        return Jsons.writeValueAsString(result)
    }
}

interface DatatypeTestOperations<
    DB : GenericContainer<*>,
    CS : ConfigurationSpecification,
    C : SourceConfiguration,
    F : SourceConfigurationFactory<CS, C>,
    T : DatatypeTestCase,
> {
    val withGlobal: Boolean
    val globalCursorMetaField: MetaField
    fun streamConfigSpec(container: DB): CS
    fun globalConfigSpec(container: DB): CS
    val configFactory: F
    val testCases: Map<String, T>
    fun createStreams(config: C)
    fun populateStreams(config: C)
}

interface DatatypeTestCase {
    val id: String
    val fieldName: String
    val isGlobal: Boolean
    val isStream: Boolean
    val expectedAirbyteSchemaType: AirbyteSchemaType
    val expectedData: List<String>
}

@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "control flow")
class DiscoverAndReadAll<
    DB : GenericContainer<*>,
    CS : ConfigurationSpecification,
    C : SourceConfiguration,
    F : SourceConfigurationFactory<CS, C>,
    T : DatatypeTestCase,
>(
    val ops: DatatypeTestOperations<DB, CS, C, F, T>,
    dbContainerSupplier: () -> DB,
) : Executable {
    private val log = KotlinLogging.logger {}
    private val dbContainer: DB by lazy { dbContainerSupplier() }

    // CDC DISCOVER and READ intermediate values and final results.
    // Intermediate values are present here as `lateinit var` instead of local variables
    // to make debugging of individual test cases easier.
    lateinit var globalConfigSpec: CS
    lateinit var globalConfig: C
    lateinit var globalCatalog: Map<String, AirbyteStream>
    lateinit var globalConfiguredCatalog: ConfiguredAirbyteCatalog
    lateinit var globalInitialReadOutput: BufferingOutputConsumer
    lateinit var globalCheckpoint: AirbyteStateMessage
    lateinit var globalSubsequentReadOutput: BufferingOutputConsumer
    lateinit var globalMessages: List<AirbyteMessage>
    lateinit var globalMessagesByStream: Map<String, BufferingOutputConsumer>
    // Same as above but for JDBC.
    lateinit var streamConfigSpec: CS
    lateinit var streamConfig: C
    lateinit var streamCatalog: Map<String, AirbyteStream>
    lateinit var streamConfiguredCatalog: ConfiguredAirbyteCatalog
    lateinit var streamReadOutput: BufferingOutputConsumer
    lateinit var streamMessages: List<AirbyteMessage>
    lateinit var streamMessagesByStream: Map<String, BufferingOutputConsumer>

    override fun execute() {
        log.info { "Generating stream-sync config." }
        streamConfigSpec = ops.streamConfigSpec(dbContainer)
        streamConfig = ops.configFactory.make(streamConfigSpec)
        log.info { "Creating empty datatype streams in source." }
        ops.createStreams(streamConfig)
        log.info { "Executing DISCOVER operation with stream-sync config." }
        streamCatalog = discover(streamConfigSpec)
        streamConfiguredCatalog =
            configuredCatalog(streamCatalog.filterKeys { ops.testCases[it]?.isStream == true })
        if (ops.withGlobal) {
            log.info { "Generating global-sync config." }
            globalConfigSpec = ops.globalConfigSpec(dbContainer)
            globalConfig = ops.configFactory.make(globalConfigSpec)
            log.info { "Executing DISCOVER operation with global-sync config." }
            globalCatalog = discover(globalConfigSpec)
            globalConfiguredCatalog =
                configuredCatalog(globalCatalog.filterKeys { ops.testCases[it]?.isGlobal == true })
            log.info { "Running initial global-sync READ operation." }
            globalInitialReadOutput =
                CliRunner.source("read", globalConfigSpec, globalConfiguredCatalog).run()
            Assertions.assertNotEquals(
                emptyList<AirbyteStateMessage>(),
                globalInitialReadOutput.states()
            )
            globalCheckpoint = globalInitialReadOutput.states().last()
            Assertions.assertEquals(
                emptyList<AirbyteRecordMessage>(),
                globalInitialReadOutput.records()
            )
            Assertions.assertEquals(emptyList<AirbyteLogMessage>(), globalInitialReadOutput.logs())
        }
        log.info { "Populating datatype streams in source." }
        ops.populateStreams(streamConfig)
        if (ops.withGlobal) {
            log.info { "Running subsequent global-sync READ operation." }
            globalSubsequentReadOutput =
                CliRunner.source(
                        "read",
                        globalConfigSpec,
                        globalConfiguredCatalog,
                        listOf(globalCheckpoint)
                    )
                    .run()
            Assertions.assertNotEquals(
                emptyList<AirbyteStateMessage>(),
                globalSubsequentReadOutput.states()
            )
            Assertions.assertNotEquals(
                emptyList<AirbyteRecordMessage>(),
                globalSubsequentReadOutput.records()
            )
            Assertions.assertEquals(
                emptyList<AirbyteLogMessage>(),
                globalSubsequentReadOutput.logs()
            )
            globalMessages = globalSubsequentReadOutput.messages()
            globalMessagesByStream = byStream(globalConfiguredCatalog, globalMessages)
        }
        log.info { "Running stream-sync READ operation." }
        streamReadOutput = CliRunner.source("read", streamConfigSpec, streamConfiguredCatalog).run()
        Assertions.assertNotEquals(emptyList<AirbyteStateMessage>(), streamReadOutput.states())
        Assertions.assertNotEquals(emptyList<AirbyteRecordMessage>(), streamReadOutput.records())
        Assertions.assertEquals(emptyList<AirbyteLogMessage>(), streamReadOutput.logs())
        streamMessages = streamReadOutput.messages()
        streamMessagesByStream = byStream(streamConfiguredCatalog, streamMessages)
        log.info { "Done." }
    }

    private fun discover(configSpec: CS): Map<String, AirbyteStream> {
        val output: BufferingOutputConsumer = CliRunner.source("discover", configSpec).run()
        val streams: Map<String, AirbyteStream> =
            output.catalogs().firstOrNull()?.streams?.filterNotNull()?.associateBy { it.name }
                ?: mapOf()
        Assertions.assertFalse(streams.isEmpty())
        return streams
    }

    private fun configuredCatalog(streams: Map<String, AirbyteStream>): ConfiguredAirbyteCatalog {
        val configuredStreams: List<ConfiguredAirbyteStream> =
            streams.values.map(CatalogHelpers::toDefaultConfiguredStream)
        for (configuredStream in configuredStreams) {
            if (
                configuredStream.stream.supportedSyncModes.contains(SyncMode.INCREMENTAL) &&
                    configuredStream.stream.sourceDefinedCursor == true
            ) {
                configuredStream.syncMode = SyncMode.INCREMENTAL
                configuredStream.cursorField = listOf(ops.globalCursorMetaField.id)
            } else {
                configuredStream.syncMode = SyncMode.FULL_REFRESH
            }
        }
        return ConfiguredAirbyteCatalog().withStreams(configuredStreams)
    }

    private fun byStream(
        configuredCatalog: ConfiguredAirbyteCatalog,
        messages: List<AirbyteMessage>
    ): Map<String, BufferingOutputConsumer> {
        val result: Map<String, BufferingOutputConsumer> =
            configuredCatalog.streams.associate {
                it.stream.name to BufferingOutputConsumer(ClockFactory().fixed())
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
