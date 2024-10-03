package io.airbyte.cdk.integrations.standardtest.destination

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.collect.ImmutableMap
import com.google.common.collect.Lists
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataArgumentsProvider
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataTypeTestArgumentProvider
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.util.ArgumentProviderUtil
import io.airbyte.commons.jackson.MoreMappers
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.resources.MoreResources
import io.airbyte.configoss.OperatorDbt
import io.airbyte.configoss.StandardCheckConnectionOutput
import io.airbyte.configoss.WorkerDestinationConfig
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.*
import io.airbyte.workers.exception.TestHarnessException
import io.airbyte.workers.general.DbtTransformationRunner
import io.airbyte.workers.helper.EntrypointEnvChecker
import io.airbyte.workers.normalization.DefaultNormalizationRunner
import io.github.oshai.kotlinlogging.KotlinLogging
import org.junit.jupiter.api.*
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ArgumentsSource
import java.io.IOException
import java.nio.file.Files
import java.time.*
import java.util.*
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger
import java.util.function.Consumer
import kotlin.test.assertNotNull

private val LOGGER = KotlinLogging.logger {}

abstract class DestinationAcceptanceTest(
    verifyIndividualStateAndCounts: Boolean = false,
    useV2Fields: Boolean = false,
    supportsChangeCapture: Boolean = false,
    expectNumericTimestamps: Boolean = false,
    expectSchemalessObjectsCoercedToStrings: Boolean = false,
    expectUnionsPromotedToDisjointRecords: Boolean = false
): BaseDestinationAcceptanceTest(
    verifyIndividualStateAndCounts = verifyIndividualStateAndCounts,
    useV2Fields = useV2Fields,
    supportsChangeCapture = supportsChangeCapture,
    expectNumericTimestamps = expectNumericTimestamps,
    expectSchemalessObjectsCoercedToStrings = expectSchemalessObjectsCoercedToStrings,
    expectUnionsPromotedToDisjointRecords = expectUnionsPromotedToDisjointRecords
) {

    /** Verify that when the integrations returns a valid spec. */
    @Test
    @Throws(TestHarnessException::class)
    fun testGetSpec() {
        Assertions.assertNotNull(runSpec())
    }

    /**
     * Verify that when given valid credentials, that check connection returns a success response.
     * Assume that the [BaseDestinationAcceptanceTest.getConfig] is valid.
     */
    @Test
    @Throws(Exception::class)
    fun testCheckConnection() {
        Assertions.assertEquals(
            StandardCheckConnectionOutput.Status.SUCCEEDED,
            runCheck(getConfig()).status
        )
    }

    /**
     * Verify that when given invalid credentials, that check connection returns a failed response.
     * Assume that the [BaseDestinationAcceptanceTest.getFailCheckConfig] is invalid.
     */
    @Test
    @Throws(Exception::class)
    fun testCheckConnectionInvalidCredentials() {
        Assertions.assertEquals(
            StandardCheckConnectionOutput.Status.FAILED,
            runCheck(getFailCheckConfig()).status
        )
    }

    /**
     * Verify that the integration successfully writes records. Tests a wide variety of messages and
     * schemas (aspirationally, anyway).
     */
    @ParameterizedTest
    @ArgumentsSource(DataArgumentsProvider::class)
    @Throws(Exception::class)
    fun testSync(messagesFilename: String, catalogFilename: String) {
        val catalog =
            Jsons.deserialize(
                MoreResources.readResource(catalogFilename),
                AirbyteCatalog::class.java
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        configuredCatalog.streams.forEach {
            it.withSyncId(42).withGenerationId(12).withMinimumGenerationId(12)
        }
        val messages: List<AirbyteMessage> =
            MoreResources.readResource(messagesFilename).trim().lines().map {
                Jsons.deserialize(it, AirbyteMessage::class.java)
            }

        val config = getConfig()
        val defaultSchema = getDefaultSchema(config)
        runSyncAndVerifyStateOutput(config, messages, configuredCatalog, false)
        retrieveRawRecordsAndAssertSameMessages(catalog, messages, defaultSchema)
    }

    /**
     * This serves to test MSSQL 2100 limit parameters in a single query. this means that for
     * Airbyte insert data need to limit to ~ 700 records (3 columns for the raw tables) = 2100
     * params
     */
    @ParameterizedTest
    @ArgumentsSource(DataArgumentsProvider::class)
    @Throws(Exception::class)
    fun testSyncWithLargeRecordBatch(messagesFilename: String, catalogFilename: String) {
        val catalog =
            Jsons.deserialize(
                MoreResources.readResource(catalogFilename),
                AirbyteCatalog::class.java
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        configuredCatalog.streams.forEach {
            it.withSyncId(42).withGenerationId(12).withMinimumGenerationId(12)
        }
        val messages: List<AirbyteMessage> =
            MoreResources.readResource(messagesFilename).trim().lines().map {
                Jsons.deserialize(it, AirbyteMessage::class.java)
            }

        /* Replicate the runs of messages and state hundreds of times, but keep trace messages at the end. */
        val lotsOfRecordAndStateBlocks =
            Collections.nCopies(
                400,
                messages.filter { it.type == AirbyteMessage.Type.RECORD || it.type == AirbyteMessage.Type.STATE }
            )
        val traceMessages = messages.filter { it.type == AirbyteMessage.Type.TRACE }
        val concatenated = lotsOfRecordAndStateBlocks.flatten() + traceMessages

        val config = getConfig()
        runSyncAndVerifyStateOutput(config, concatenated, configuredCatalog, false)
    }

    /** Verify that the integration overwrites the first sync with the second sync. */
    @Test
    @Throws(Exception::class)
    fun testSecondSync() {
        if (!implementsOverwrite()) {
            LOGGER.info { "Destination's spec.json does not support overwrite sync mode." }
            return
        }

        val catalog =
            Jsons.deserialize<AirbyteCatalog>(
                MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getCatalogFileVersion(
                        getProtocolVersion()
                    )
                ),
                AirbyteCatalog::class.java
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        configuredCatalog.streams.forEach {
            it.withSyncId(42).withGenerationId(12).withMinimumGenerationId(12)
        }
        val firstSyncMessages: List<AirbyteMessage> =
            MoreResources.readResource(
                DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getMessageFileVersion(
                    getProtocolVersion()
                )
            )
                .trim()
                .lines()
                .map { Jsons.deserialize<AirbyteMessage>(it, AirbyteMessage::class.java) }

        val config = getConfig()
        runSyncAndVerifyStateOutput(config, firstSyncMessages, configuredCatalog, false)

        // We need to make sure that other streams\tables\files in the same location will not be
        // affected\deleted\overridden by our activities during first, second or any future sync.
        // So let's create a dummy data that will be checked after all sync. It should remain the
        // same
        val dummyCatalog =
            Jsons.deserialize<AirbyteCatalog>(
                MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getCatalogFileVersion(
                        getProtocolVersion()
                    )
                ),
                AirbyteCatalog::class.java
            )
        dummyCatalog.streams[0].name = DUMMY_CATALOG_NAME
        val configuredDummyCatalog = CatalogHelpers.toDefaultConfiguredCatalog(dummyCatalog)
        configuredDummyCatalog.streams.forEach {
            it.withSyncId(42).withGenerationId(20).withMinimumGenerationId(20)
        }
        // update messages to set new dummy stream name
        firstSyncMessages
            .filter { message: AirbyteMessage -> message.record != null }
            .forEach { message: AirbyteMessage -> message.record.stream = DUMMY_CATALOG_NAME }
        firstSyncMessages
            .filter { message: AirbyteMessage -> message.type == AirbyteMessage.Type.TRACE }
            .forEach { message: AirbyteMessage ->
                message.trace.streamStatus.streamDescriptor.name = DUMMY_CATALOG_NAME
            }
        // sync dummy data
        runSyncAndVerifyStateOutput(config, firstSyncMessages, configuredDummyCatalog, false)

        // Run second sync
        val configuredCatalog2 = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        configuredCatalog2.streams.forEach {
            it.withSyncId(43).withGenerationId(13).withMinimumGenerationId(13)
        }
        val descriptor = StreamDescriptor().withName(catalog.streams[0].name)
        val secondSyncMessages: List<AirbyteMessage> =
            Lists.newArrayList(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withStream(catalog.streams[0].name)
                            .withEmittedAt(Instant.now().toEpochMilli())
                            .withData(
                                Jsons.jsonNode(
                                    ImmutableMap.builder<Any, Any>()
                                        .put("id", 1)
                                        .put("currency", "USD")
                                        .put(
                                            "date",
                                            "2020-03-31T00:00:00Z"
                                        ) // TODO(sherifnada) hack: write decimals with sigfigs
                                        // because Snowflake stores 10.1 as "10" which
                                        // fails destination tests
                                        .put("HKD", 10.1)
                                        .put("NZD", 700.1)
                                        .build()
                                )
                            )
                    ),
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.STATE)
                    .withState(
                        AirbyteStateMessage()
                            .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                            .withGlobal(
                                AirbyteGlobalState()
                                    .withSharedState(
                                        Jsons.jsonNode(ImmutableMap.of("checkpoint", 2))
                                    )
                            )
                    ),
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.TRACE)
                    .withTrace(
                        AirbyteTraceMessage()
                            .withType(AirbyteTraceMessage.Type.STREAM_STATUS)
                            .withEmittedAt(1234.0)
                            .withStreamStatus(
                                AirbyteStreamStatusTraceMessage()
                                    .withStreamDescriptor(descriptor)
                                    .withStatus(
                                        AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE
                                    )
                            )
                    )
            )

        runSyncAndVerifyStateOutput(config, secondSyncMessages, configuredCatalog2, false)
        val defaultSchema = getDefaultSchema(config)
        retrieveRawRecordsAndAssertSameMessages(catalog, secondSyncMessages, defaultSchema)

        // verify that other streams in the same location were not affected. If something fails
        // here,
        // then this need to be fixed in connectors logic to override only required streams
        retrieveRawRecordsAndAssertSameMessages(dummyCatalog, firstSyncMessages, defaultSchema)
    }

    /**
     * Tests that we are able to read over special characters properly when processing line breaks
     * in destinations.
     */
    @Test
    @Throws(Exception::class)
    open fun testLineBreakCharacters() {
        val catalog =
            Jsons.deserialize<AirbyteCatalog>(
                MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getCatalogFileVersion(
                        getProtocolVersion()
                    )
                ),
                AirbyteCatalog::class.java
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        configuredCatalog.streams.forEach {
            it.withSyncId(42).withGenerationId(12).withMinimumGenerationId(12)
        }
        val config = getConfig()

        val secondSyncMessages: List<AirbyteMessage> =
            Lists.newArrayList(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withStream(catalog.streams[0].name)
                            .withEmittedAt(Instant.now().toEpochMilli())
                            .withData(
                                Jsons.jsonNode(
                                    ImmutableMap.builder<Any, Any>()
                                        .put("id", 1)
                                        .put("currency", "USD\u2028")
                                        .put(
                                            "date",
                                            "2020-03-\n31T00:00:00Z\r"
                                        ) // TODO(sherifnada) hack: write decimals with sigfigs
                                        // because Snowflake stores 10.1 as "10" which
                                        // fails destination tests
                                        .put("HKD", 10.1)
                                        .put("NZD", 700.1)
                                        .build()
                                )
                            )
                    ),
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.STATE)
                    .withState(
                        AirbyteStateMessage()
                            .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                            .withGlobal(
                                AirbyteGlobalState()
                                    .withSharedState(
                                        Jsons.jsonNode(ImmutableMap.of("checkpoint", 2))
                                    )
                            )
                    ),
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.TRACE)
                    .withTrace(
                        AirbyteTraceMessage()
                            .withType(AirbyteTraceMessage.Type.STREAM_STATUS)
                            .withEmittedAt(1234.0)
                            .withStreamStatus(
                                AirbyteStreamStatusTraceMessage()
                                    .withStreamDescriptor(
                                        StreamDescriptor().withName(catalog.streams[0].name)
                                    )
                                    .withStatus(
                                        AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE
                                    )
                            )
                    )
            )

        runSyncAndVerifyStateOutput(config, secondSyncMessages, configuredCatalog, false)
        val defaultSchema = getDefaultSchema(config)
        retrieveRawRecordsAndAssertSameMessages(catalog, secondSyncMessages, defaultSchema)
    }

    @Test
    fun normalizationFromDefinitionValueShouldBeCorrect() {
        if (normalizationFromDefinition()) {
            var normalizationRunnerFactorySupportsDestinationImage: Boolean
            try {
                DefaultNormalizationRunner(
                    processFactory,
                    getNormalizationImageName(),
                    getNormalizationIntegrationType()
                )
                normalizationRunnerFactorySupportsDestinationImage = true
            } catch (e: IllegalStateException) {
                normalizationRunnerFactorySupportsDestinationImage = false
            }
            Assertions.assertEquals(
                normalizationFromDefinition(),
                normalizationRunnerFactorySupportsDestinationImage
            )
        }
    }

    /**
     * Verify that the integration successfully writes records incrementally. The second run should
     * append records to the datastore instead of overwriting the previous run.
     */
    @Test
    @Throws(Exception::class)
    fun testIncrementalSync() {
        if (!implementsAppend()) {
            LOGGER.info {
                "Destination's spec.json does not include '\"supportsIncremental\" ; true'"
            }
            return
        }

        val catalog =
            Jsons.deserialize<AirbyteCatalog>(
                MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getCatalogFileVersion(
                        getProtocolVersion()
                    )
                ),
                AirbyteCatalog::class.java
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)

        configuredCatalog.streams.forEach {
            it.withSyncMode(SyncMode.INCREMENTAL)
                .withDestinationSyncMode(DestinationSyncMode.APPEND)
                .withSyncId(42)
                .withGenerationId(12)
                .withMinimumGenerationId(0)
        }

        val firstSyncMessages: List<AirbyteMessage> =
            MoreResources.readResource(
                DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getMessageFileVersion(
                    getProtocolVersion()
                )
            )
                .trim()
                .lines()
                .map { Jsons.deserialize(it, AirbyteMessage::class.java) }

        val config = getConfig()
        runSyncAndVerifyStateOutput(config, firstSyncMessages, configuredCatalog, false)
        val descriptor = StreamDescriptor()
        descriptor.name = catalog.streams[0].name
        val secondSyncMessages: List<AirbyteMessage> =
            Lists.newArrayList(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withStream(catalog.streams[0].name)
                            .withEmittedAt(Instant.now().toEpochMilli())
                            .withData(
                                Jsons.jsonNode(
                                    ImmutableMap.builder<Any, Any>()
                                        .put("id", 1)
                                        .put("currency", "USD")
                                        .put(
                                            "date",
                                            "2020-03-31T00:00:00Z"
                                        ) // TODO(sherifnada) hack: write decimals with sigfigs
                                        // because Snowflake stores 10.1 as "10" which
                                        // fails destination tests
                                        .put("HKD", 10.1)
                                        .put("NZD", 700.1)
                                        .build()
                                )
                            )
                    ),
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.STATE)
                    .withState(
                        AirbyteStateMessage()
                            .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                            .withGlobal(
                                AirbyteGlobalState()
                                    .withSharedState(
                                        Jsons.jsonNode(ImmutableMap.of("checkpoint", 2))
                                    )
                            )
                    ),
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.TRACE)
                    .withTrace(
                        AirbyteTraceMessage()
                            .withType(AirbyteTraceMessage.Type.STREAM_STATUS)
                            .withEmittedAt(1234.0)
                            .withStreamStatus(
                                AirbyteStreamStatusTraceMessage()
                                    .withStreamDescriptor(descriptor)
                                    .withStatus(
                                        AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE
                                    )
                            )
                    )
            )

        runSyncAndVerifyStateOutput(config, secondSyncMessages, configuredCatalog, false)

        val expectedMessagesAfterSecondSync: MutableList<AirbyteMessage> = ArrayList()
        expectedMessagesAfterSecondSync.addAll(firstSyncMessages)
        expectedMessagesAfterSecondSync.addAll(secondSyncMessages)

        val defaultSchema = getDefaultSchema(config)
        retrieveRawRecordsAndAssertSameMessages(
            catalog,
            expectedMessagesAfterSecondSync,
            defaultSchema
        )
    }

    @ArgumentsSource(DataArgumentsProvider::class)
    @Test
    @Throws(Exception::class)
    fun testIncrementalSyncWithNormalizationDropOneColumn() {
        if (!normalizationFromDefinition() || !supportIncrementalSchemaChanges()) {
            return
        }

        val catalog =
            Jsons.deserialize<AirbyteCatalog>(
                MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getCatalogFileVersion(
                        ProtocolVersion.V0
                    )
                ),
                AirbyteCatalog::class.java
            )

        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        configuredCatalog.streams.forEach { s ->
            s.withSyncMode(SyncMode.INCREMENTAL)
            s.withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
            s.withCursorField(emptyList())
            // use composite primary key of various types (string, float)
            s.withPrimaryKey(
                java.util.List.of(
                    listOf("id"),
                    listOf("currency"),
                    listOf("date"),
                    listOf("NZD"),
                    listOf("USD")
                )
            )
        }

        var messages =
            MoreResources.readResource(
                DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getMessageFileVersion(
                    ProtocolVersion.V0
                )
            )
                .lines()
                .map { Jsons.deserialize(it, AirbyteMessage::class.java) }
                .toMutableList()

        val config = getConfig()
        runSyncAndVerifyStateOutput(config, messages, configuredCatalog, true)

        val defaultSchema = getDefaultSchema(config)
        var actualMessages = retrieveNormalizedRecords(catalog, defaultSchema)
        assertSameMessages(messages, actualMessages, true)

        // remove one field
        val jsonSchema = configuredCatalog.streams[0].stream.jsonSchema
        (jsonSchema.findValue("properties") as ObjectNode).remove("HKD")
        // insert more messages
        // NOTE: we re-read the messages because `assertSameMessages` above pruned the emittedAt
        // timestamps.
        messages =
            MoreResources.readResource(
                DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getMessageFileVersion(
                    ProtocolVersion.V0
                )
            )
                .lines()
                .map { Jsons.deserialize(it, AirbyteMessage::class.java) }
                .toMutableList()
        messages.addLast(
            Jsons.deserialize(
                "{\"type\": \"RECORD\", \"record\": {\"stream\": \"exchange_rate\", \"emitted_at\": 1602637989500, \"data\": { \"id\": 2, \"currency\": \"EUR\", \"date\": \"2020-09-02T00:00:00Z\", \"NZD\": 1.14, \"USD\": 10.16}}}\n",
                AirbyteMessage::class.java
            )
        )

        runSyncAndVerifyStateOutput(config, messages, configuredCatalog, true)

        // assert the removed field is missing on the new messages
        actualMessages = retrieveNormalizedRecords(catalog, defaultSchema)

        // We expect all the of messages to be missing the removed column after normalization.
        val expectedMessages =
            messages.map { message: AirbyteMessage ->
                if (message.record != null) {
                    (message.record.data as ObjectNode).remove("HKD")
                }
                message
            }

        assertSameMessages(expectedMessages, actualMessages, true)
    }

    /**
     * Verify that the integration successfully writes records successfully both raw and normalized.
     * Tests a wide variety of messages an schemas (aspirationally, anyway).
     */
    @ParameterizedTest
    @ArgumentsSource(DataArgumentsProvider::class)
    @Throws(Exception::class)
    // Normalization is a pretty slow process. Increase our test timeout.
    @Timeout(value = 300, unit = TimeUnit.SECONDS)
    open fun testSyncWithNormalization(messagesFilename: String, catalogFilename: String) {
        if (!normalizationFromDefinition()) {
            return
        }

        val catalog =
            Jsons.deserialize(
                MoreResources.readResource(catalogFilename),
                AirbyteCatalog::class.java
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        val messages =
            MoreResources.readResource(messagesFilename).trim().lines().map {
                Jsons.deserialize(it, AirbyteMessage::class.java)
            }

        val config = getConfig()
        runSyncAndVerifyStateOutput(config, messages, configuredCatalog, true)

        val defaultSchema = getDefaultSchema(config)
        val actualMessages = retrieveNormalizedRecords(catalog, defaultSchema)
        assertSameMessages(messages, actualMessages, true)
    }

    /**
     * Verify that the integration successfully writes records successfully both raw and normalized
     * and run dedupe transformations.
     *
     * Although this test assumes append-dedup requires normalization, and almost all our
     * Destinations do so, this is not necessarily true. This explains [.implementsAppendDedup].
     */
    @Test
    @Throws(Exception::class)
    open fun testIncrementalDedupeSync() {
        if (!implementsAppendDedup()) {
            LOGGER.info {
                "Destination's spec.json does not include 'append_dedupe' in its '\"supportedDestinationSyncModes\"'"
            }
            return
        }

        val catalog =
            Jsons.deserialize<AirbyteCatalog>(
                MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getCatalogFileVersion(
                        getProtocolVersion()
                    )
                ),
                AirbyteCatalog::class.java
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        configuredCatalog.streams.forEach { s ->
            s.withSyncMode(SyncMode.INCREMENTAL)
            s.withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
            s.withCursorField(emptyList())
            // use composite primary key of various types (string, float)
            s.withPrimaryKey(
                java.util.List.of(listOf("id"), listOf("currency"), listOf("date"), listOf("NZD"))
            )
        }

        val firstSyncMessages =
            MoreResources.readResource(
                DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getMessageFileVersion(
                    getProtocolVersion()
                )
            )
                .lines()
                .filter { it.isNotEmpty() }
                .map { Jsons.deserialize(it, AirbyteMessage::class.java) }
        val config = getConfig()
        runSyncAndVerifyStateOutput(
            config,
            firstSyncMessages,
            configuredCatalog,
            supportsNormalization()
        )

        val secondSyncMessages: List<AirbyteMessage> =
            Lists.newArrayList(
                io.airbyte.protocol.models.v0
                    .AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withStream(catalog.streams[0].name)
                            .withEmittedAt(Instant.now().toEpochMilli())
                            .withData(
                                Jsons.jsonNode(
                                    ImmutableMap.builder<Any, Any>()
                                        .put("id", 2)
                                        .put("currency", "EUR")
                                        .put("date", "2020-09-01T00:00:00Z")
                                        .put("HKD", 10.5)
                                        .put("NZD", 1.14)
                                        .build()
                                )
                            )
                    ),
                io.airbyte.protocol.models.v0
                    .AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withStream(catalog.streams[0].name)
                            .withEmittedAt(Instant.now().toEpochMilli() + 100L)
                            .withData(
                                Jsons.jsonNode(
                                    ImmutableMap.builder<Any, Any>()
                                        .put("id", 1)
                                        .put("currency", "USD")
                                        .put("date", "2020-09-01T00:00:00Z")
                                        .put("HKD", 5.4)
                                        .put("NZD", 1.14)
                                        .build()
                                )
                            )
                    ),
                io.airbyte.protocol.models.v0
                    .AirbyteMessage()
                    .withType(AirbyteMessage.Type.STATE)
                    .withState(
                        AirbyteStateMessage()
                            .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                            .withGlobal(
                                AirbyteGlobalState()
                                    .withSharedState(
                                        Jsons.jsonNode(ImmutableMap.of("checkpoint", 2))
                                    )
                            )
                    )
            )
        runSyncAndVerifyStateOutput(config, secondSyncMessages, configuredCatalog, false)

        val expectedMessagesAfterSecondSync: MutableList<AirbyteMessage> = ArrayList()
        expectedMessagesAfterSecondSync.addAll(firstSyncMessages)
        expectedMessagesAfterSecondSync.addAll(secondSyncMessages)

        val latestMessagesOnly =
            expectedMessagesAfterSecondSync
                .filter { it.type == AirbyteMessage.Type.RECORD && it.record != null }
                .groupBy {
                    it.record.data["id"].asText() +
                            it.record.data["currency"].asText() +
                            it.record.data["date"].asText() +
                            it.record.data["NZD"].asText()
                }
                .mapValues { it.value.maxBy { it.record.emittedAt } }
        // Filter expectedMessagesAfterSecondSync and keep latest messages only (keep same message
        // order)
        val expectedMessages =
            expectedMessagesAfterSecondSync
                .filter { it.type == AirbyteMessage.Type.RECORD && it.record != null }
                .filter {
                    val key =
                        it.record.data["id"].asText() +
                                it.record.data["currency"].asText() +
                                it.record.data["date"].asText() +
                                it.record.data["NZD"].asText()
                    (it.record.emittedAt == latestMessagesOnly[key]!!.record.emittedAt)
                }

        val defaultSchema = getDefaultSchema(config)
        retrieveRawRecordsAndAssertSameMessages(
            catalog,
            expectedMessagesAfterSecondSync,
            defaultSchema
        )
        if (normalizationFromDefinition()) {
            val actualMessages = retrieveNormalizedRecords(catalog, defaultSchema)
            assertSameMessages(expectedMessages, actualMessages, true)
        }
    }

    protected open val maxRecordValueLimit: Int
        /** @return the max limit length allowed for values in the destination. */
        get() = 1000000000

    @Test
    @Throws(Exception::class)
    open fun testCustomDbtTransformations() {
        if (!dbtFromDefinition()) {
            return
        }

        val config = getConfig()

        // This may throw IllegalStateException "Requesting normalization, but it is not included in
        // the
        // normalization mappings"
        // We indeed require normalization implementation of the 'transform_config' function for
        // this
        // destination,
        // because we make sure to install required dbt dependency in the normalization docker image
        // in
        // order to run
        // this test successfully and that we are able to convert a destination 'config.json' into a
        // dbt
        // 'profiles.yml'
        // (we don't actually rely on normalization running anything else here though)
        val runner =
            DbtTransformationRunner(
                processFactory,
                DefaultNormalizationRunner(
                    processFactory,
                    getNormalizationImageName(),
                    getNormalizationIntegrationType()
                )
            )
        runner.start()
        val transformationRoot = Files.createDirectories(jobRoot.resolve("transform"))
        val dbtConfig =
            OperatorDbt() // Forked from https://github.com/dbt-labs/jaffle_shop because they made a
                // change that would have
                // required a dbt version upgrade
                // https://github.com/dbt-labs/jaffle_shop/commit/b1680f3278437c081c735b7ea71c2ff9707bc75f#diff-27386df54b2629c1191d8342d3725ed8678413cfa13b5556f59d69d33fae5425R20
                // We're actually two commits upstream of that, because the previous commit
                // (https://github.com/dbt-labs/jaffle_shop/commit/ec36ae177ab5cb79da39ff8ab068c878fbac13a0) also
                // breaks something
                // TODO once we're on DBT 1.x, switch this back to using the main branch
                .withGitRepoUrl("https://github.com/airbytehq/jaffle_shop.git")
                .withGitRepoBranch("pre_dbt_upgrade")
                .withDockerImage(getNormalizationImageName())
        //
        // jaffle_shop is a fictional ecommerce store maintained by fishtownanalytics/dbt.
        //
        // This dbt project transforms raw data from an app database into a customers and orders
        // model ready
        // for analytics.
        // The repo is a self-contained playground dbt project, useful for testing out scripts, and
        // communicating some of the core dbt concepts:
        //
        // 1. First, it tests if connection to the destination works.
        dbtConfig.withDbtArguments("debug")
        if (!runner.run(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig)) {
            throw TestHarnessException("dbt debug Failed.")
        }
        // 2. Install any dependencies packages, if any
        dbtConfig.withDbtArguments("deps")
        if (!runner.transform(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig)) {
            throw TestHarnessException("dbt deps Failed.")
        }
        // 3. It contains seeds that includes some (fake) raw data from a fictional app as CSVs data
        // sets.
        // This materializes the CSVs as tables in your target schema.
        // Note that a typical dbt project does not require this step since dbt assumes your raw
        // data is
        // already in your warehouse.
        dbtConfig.withDbtArguments("seed")
        if (!runner.transform(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig)) {
            throw TestHarnessException("dbt seed Failed.")
        }
        // 4. Run the models:
        // Note: If this steps fails, it might mean that you need to make small changes to the SQL
        // in the
        // models folder to adjust for the flavor of SQL of your target database.
        dbtConfig.withDbtArguments("run")
        if (!runner.transform(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig)) {
            throw TestHarnessException("dbt run Failed.")
        }
        // 5. Test the output of the models and tables have been properly populated:
        dbtConfig.withDbtArguments("test")
        if (!runner.transform(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig)) {
            throw TestHarnessException("dbt test Failed.")
        }
        // 6. Generate dbt documentation for the project:
        // This step is commented out because it takes a long time, but is not vital for Airbyte
        // dbtConfig.withDbtArguments("docs generate");
        // if (!runner.transform(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig))
        // {
        // throw new WorkerException("dbt docs generate Failed.");
        // }
        runner.close()
    }

    @Test
    @Throws(Exception::class)
    fun testCustomDbtTransformationsFailure() {
        if (!normalizationFromDefinition() || !dbtFromDefinition()) {
            // we require normalization implementation for this destination, because we make sure to
            // install
            // required dbt dependency in the normalization docker image in order to run this test
            // successfully
            // (we don't actually rely on normalization running anything here though)
            return
        }

        val config = getConfig()

        val runner =
            DbtTransformationRunner(
                processFactory,
                DefaultNormalizationRunner(
                    processFactory,
                    getNormalizationImageName(),
                    getNormalizationIntegrationType()
                )
            )
        runner.start()
        val transformationRoot = Files.createDirectories(jobRoot.resolve("transform"))
        val dbtConfig =
            OperatorDbt()
                .withGitRepoUrl("https://github.com/fishtown-analytics/dbt-learn-demo.git")
                .withGitRepoBranch("main")
                .withDockerImage("fishtownanalytics/dbt:0.19.1")
                .withDbtArguments("debug")
        if (!runner.run(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig)) {
            throw TestHarnessException("dbt debug Failed.")
        }

        dbtConfig.withDbtArguments("test")
        Assertions.assertFalse(
            runner.transform(JOB_ID, JOB_ATTEMPT, transformationRoot, config, null, dbtConfig),
            "dbt test should fail, as we haven't run dbt run on this project yet"
        )
    }

    /** Verify the destination uses the namespace field if it is set. */
    @Test
    @Throws(Exception::class)
    fun testSyncUsesAirbyteStreamNamespaceIfNotNull() {
        if (!implementsNamespaces()) {
            return
        }

        // TODO(davin): make these tests part of the catalog file.
        val catalog =
            Jsons.deserialize<AirbyteCatalog>(
                MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getCatalogFileVersion(
                        getProtocolVersion()
                    )
                ),
                AirbyteCatalog::class.java
            )
        // A unique namespace is required to avoid test isolation problems.
        val namespace = TestingNamespaces.generate("source_namespace")
        testSchemas.add(namespace)

        catalog.streams.forEach(Consumer { stream: AirbyteStream -> stream.namespace = namespace })
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)

        val messages =
            MoreResources.readResource(
                DataArgumentsProvider.EXCHANGE_RATE_CONFIG.getMessageFileVersion(
                    getProtocolVersion()
                )
            )
                .trim()
                .lines()
                .map { Jsons.deserialize(it, AirbyteMessage::class.java) }
        val messagesWithNewNamespace = getRecordMessagesWithNewNamespace(messages, namespace)

        val config = getConfig()
        val defaultSchema = getDefaultSchema(config)
        runSyncAndVerifyStateOutput(config, messagesWithNewNamespace, configuredCatalog, false)
        retrieveRawRecordsAndAssertSameMessages(catalog, messagesWithNewNamespace, defaultSchema)
    }

    /** Verify a destination is able to write tables with the same name to different namespaces. */
    @Test
    @Throws(Exception::class)
    fun testSyncWriteSameTableNameDifferentNamespace() {
        if (!implementsNamespaces()) {
            return
        }

        // TODO(davin): make these tests part of the catalog file.
        val catalog =
            Jsons.deserialize<AirbyteCatalog>(
                MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getCatalogFileVersion(
                        getProtocolVersion()
                    )
                ),
                AirbyteCatalog::class.java
            )
        val namespace1 = TestingNamespaces.generate("source_namespace")
        testSchemas.add(namespace1)
        catalog.streams.forEach(Consumer { stream: AirbyteStream -> stream.namespace = namespace1 })

        val diffNamespaceStreams = ArrayList<AirbyteStream>()
        val namespace2 = TestingNamespaces.generate("diff_source_namespace")
        testSchemas.add(namespace2)
        val mapper = MoreMappers.initMapper()
        for (stream in catalog.streams) {
            val clonedStream =
                mapper.readValue(mapper.writeValueAsString(stream), AirbyteStream::class.java)
            clonedStream.namespace = namespace2
            diffNamespaceStreams.add(clonedStream)
        }
        catalog.streams.addAll(diffNamespaceStreams)

        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        val messageFile: String =
            DataArgumentsProvider.EXCHANGE_RATE_CONFIG.getMessageFileVersion(getProtocolVersion())
        val ns1Messages =
            MoreResources.readResource(messageFile).trim().lines().map {
                Jsons.deserialize(it, AirbyteMessage::class.java)
            }
        val ns1MessagesAtNamespace1 = getRecordMessagesWithNewNamespace(ns1Messages, namespace1)
        val ns2Messages: List<AirbyteMessage> =
            MoreResources.readResource(messageFile).trim().lines().map {
                Jsons.deserialize(it, AirbyteMessage::class.java)
            }
        val ns2MessagesAtNamespace2 = getRecordMessagesWithNewNamespace(ns2Messages, namespace2)

        val allMessages = ArrayList(ns1MessagesAtNamespace1)
        allMessages.addAll(ns2MessagesAtNamespace2)

        val config = getConfig()
        val defaultSchema = getDefaultSchema(config)
        runSyncAndVerifyStateOutput(config, allMessages, configuredCatalog, false)
        retrieveRawRecordsAndAssertSameMessages(catalog, allMessages, defaultSchema)
    }

    /**
     * The goal of this test is to verify the expected conversions of a namespace as it appears in
     * the catalog to how it appears in the destination. Each database has its own rules, so this
     * test runs through several "edge" case sorts of names and checks the behavior.
     *
     * @param testCaseId
     * - the id of each test case in namespace_test_cases.json so that we can handle an individual
     * case specially for a specific database.
     * @param namespaceInCatalog
     * - namespace as it would appear in the catalog
     * @param namespaceInDst
     * - namespace as we would expect it to appear in the destination (this may be overridden for
     * different databases).
     * @throws Exception
     * - broad catch of exception to hydrate log information with additional test case context.
     */
    @ParameterizedTest
    @ArgumentsSource(NamespaceTestCaseProvider::class)
    @Throws(Exception::class)
    fun testNamespaces(testCaseId: String?, namespaceInCatalog: String, namespaceInDst: String?) {
        val nameTransformer = getNameTransformer()
        nameTransformer.ifPresent { namingConventionTransformer: NamingConventionTransformer ->
            assertNamespaceNormalization(
                testCaseId,
                namespaceInDst,
                namingConventionTransformer.getNamespace(namespaceInCatalog)
            )
        }

        if (!implementsNamespaces() || !supportNamespaceTest()) {
            return
        }

        val catalog =
            Jsons.deserialize<AirbyteCatalog>(
                MoreResources.readResource(
                    DataArgumentsProvider.Companion.NAMESPACE_CONFIG.getCatalogFileVersion(
                        getProtocolVersion()
                    )
                ),
                AirbyteCatalog::class.java
            )
        catalog.streams.forEach(
            Consumer { stream: AirbyteStream -> stream.namespace = namespaceInCatalog }
        )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)

        val messages =
            MoreResources.readResource(
                DataArgumentsProvider.NAMESPACE_CONFIG.getMessageFileVersion(
                    getProtocolVersion()
                )
            )
                .lines()
                .map { Jsons.deserialize(it, AirbyteMessage::class.java) }
        val messagesWithNewNamespace =
            getRecordMessagesWithNewNamespace(messages, namespaceInCatalog)

        val config = getConfig()
        try {
            runSyncAndVerifyStateOutput(config, messagesWithNewNamespace, configuredCatalog, false)
            // Add to the list of schemas to clean up.
            testSchemas.add(namespaceInCatalog)
        } catch (e: Exception) {
            throw IOException(
                String.format(
                    "[Test Case %s] Destination failed to sync data to namespace %s, see \"namespace_test_cases.json for details\"",
                    testCaseId,
                    namespaceInCatalog
                ),
                e
            )
        }
    }

    /**
     * In order to launch a source on Kubernetes in a pod, we need to be able to wrap the
     * entrypoint. The source connector must specify its entrypoint in the AIRBYTE_ENTRYPOINT
     * variable. This test ensures that the entrypoint environment variable is set.
     */
    @Test
    @Throws(Exception::class)
    fun testEntrypointEnvVar() {
        val entrypoint =
            EntrypointEnvChecker.getEntrypointEnvVariable(
                processFactory,
                JOB_ID,
                JOB_ATTEMPT,
                jobRoot,
                imageName
            )

        assertNotNull(entrypoint)
        Assertions.assertFalse(entrypoint.isBlank())
    }

    /**
     * Verify that destination doesn't fail if new fields arrive in the data after initial schema
     * discovery and sync.
     *
     * @throws Exception
     */
    @Test
    @Throws(Exception::class)
    open fun testSyncNotFailsWithNewFields() {
        if (!implementsOverwrite()) {
            LOGGER.info { "Destination's spec.json does not support overwrite sync mode." }
            return
        }

        val catalog =
            Jsons.deserialize<AirbyteCatalog>(
                MoreResources.readResource(
                    DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG.getCatalogFileVersion(
                        getProtocolVersion()
                    )
                ),
                AirbyteCatalog::class.java
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        configuredCatalog.streams.forEach {
            it.withSyncId(42).withGenerationId(12).withMinimumGenerationId(12)
        }

        val firstSyncMessages =
            MoreResources.readResource(
                DataArgumentsProvider.EXCHANGE_RATE_CONFIG.getMessageFileVersion(
                    getProtocolVersion()
                )
            )
                .trim()
                .lines()
                .map { Jsons.deserialize(it, AirbyteMessage::class.java) }
        val config = getConfig()
        runSyncAndVerifyStateOutput(config, firstSyncMessages, configuredCatalog, false)
        val stream = catalog.streams[0]

        // Run second sync with new fields on the message
        val configuredCatalog2 = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        configuredCatalog2.streams.forEach {
            it.withSyncId(43).withGenerationId(13).withMinimumGenerationId(13)
        }
        val descriptor = StreamDescriptor()
        descriptor.name = stream.name
        val secondSyncMessagesWithNewFields: MutableList<AirbyteMessage> =
            Lists.newArrayList(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withStream(stream.name)
                            .withEmittedAt(Instant.now().toEpochMilli())
                            .withData(
                                Jsons.jsonNode(
                                    ImmutableMap.builder<Any, Any>()
                                        .put("id", 1)
                                        .put("currency", "USD")
                                        .put("date", "2020-03-31T00:00:00Z")
                                        .put("newFieldString", "Value for new field")
                                        .put("newFieldNumber", 3)
                                        .put("HKD", 10.1)
                                        .put("NZD", 700.1)
                                        .build()
                                )
                            )
                    ),
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.STATE)
                    .withState(
                        AirbyteStateMessage()
                            .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                            .withGlobal(
                                AirbyteGlobalState()
                                    .withSharedState(
                                        Jsons.jsonNode(ImmutableMap.of("checkpoint", 2))
                                    )
                            )
                    ),
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.TRACE)
                    .withTrace(
                        AirbyteTraceMessage()
                            .withType(AirbyteTraceMessage.Type.STREAM_STATUS)
                            .withEmittedAt(1234.0)
                            .withStreamStatus(
                                AirbyteStreamStatusTraceMessage()
                                    .withStreamDescriptor(descriptor)
                                    .withStatus(
                                        AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE
                                    )
                            )
                    )
            )

        // Run sync and verify that all message were written without failing
        runSyncAndVerifyStateOutput(
            config,
            secondSyncMessagesWithNewFields,
            configuredCatalog2,
            false
        )
        val destinationOutput =
            retrieveRecords(testEnv, stream.name, getDefaultSchema(config)!!, stream.jsonSchema)
        // Remove state message
        secondSyncMessagesWithNewFields.removeIf { airbyteMessage: AirbyteMessage ->
            airbyteMessage.type == AirbyteMessage.Type.STATE || airbyteMessage.type == AirbyteMessage.Type.TRACE
        }
        Assertions.assertEquals(secondSyncMessagesWithNewFields.size, destinationOutput.size)
    }

    private fun getData(record: JsonNode): JsonNode {
        if (record.has(JavaBaseConstants.COLUMN_NAME_DATA))
            return record.get(JavaBaseConstants.COLUMN_NAME_DATA)
        return record
    }

    private fun getMeta(record: JsonNode): ObjectNode {
        val meta = record.get(JavaBaseConstants.COLUMN_NAME_AB_META)

        val asString = if (meta.isTextual) meta.asText() else Jsons.serialize(meta)
        val asMeta = Jsons.deserialize(asString)

        return asMeta as ObjectNode
    }

    @Test
    @Throws(Exception::class)
    open fun testAirbyteFields() {
        val configuredCatalog =
            Jsons.deserialize(
                MoreResources.readResource("v0/users_with_generation_id_configured_catalog.json"),
                ConfiguredAirbyteCatalog::class.java
            )
        val config = getConfig()
        val messages =
            MoreResources.readResource("v0/users_with_generation_id_messages.txt")
                .trim()
                .lines()
                .map { Jsons.deserialize(it, AirbyteMessage::class.java) }
        val preRunTime = Instant.now()
        runSyncAndVerifyStateOutput(config, messages, configuredCatalog, false)
        val generationId = configuredCatalog.streams[0].generationId
        val stream = configuredCatalog.streams[0].stream
        val destinationOutput =
            retrieveRecords(
                testEnv,
                "users",
                getDefaultSchema(config)!! /* ignored */,
                stream.jsonSchema
            )

        // Resolve common field keys.
        val abIdKey: String =
            if (useV2Fields) JavaBaseConstants.COLUMN_NAME_AB_RAW_ID
            else JavaBaseConstants.COLUMN_NAME_AB_ID
        val abTsKey =
            if (useV2Fields) JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT
            else JavaBaseConstants.COLUMN_NAME_EMITTED_AT

        // Validate airbyte fields as much as possible
        val uuidRegex = "[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}"
        val zippedMessages = messages.take(destinationOutput.size).zip(destinationOutput)
        zippedMessages.forEach { (message, record) ->
            // Ensure the id is UUID4 format (best we can do without mocks)
            Assertions.assertTrue(record.get(abIdKey).asText().matches(Regex(uuidRegex)))
            Assertions.assertEquals(message.record.emittedAt, record.get(abTsKey).asLong())

            if (useV2Fields) {
                // Generation id should match the one from the catalog
                Assertions.assertEquals(
                    generationId,
                    record.get(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID).asLong()
                )
            }
        }

        // Regardless of whether change failures are capatured, all v2
        // destinations should pass upstream changes through and set sync id.
        if (useV2Fields) {
            val metas = destinationOutput.map { getMeta(it) }
            val syncIdsAllValid = metas.map { it["sync_id"].asLong() }.all { it == 100L }
            Assertions.assertTrue(syncIdsAllValid)

            val changes = metas[2]["changes"].elements().asSequence().toList()
            Assertions.assertEquals(changes.size, 1)
            Assertions.assertEquals(changes[0]["field"].asText(), "name")
            Assertions.assertEquals(
                changes[0]["change"].asText(),
                AirbyteRecordMessageMetaChange.Change.TRUNCATED.value()
            )
            Assertions.assertEquals(
                changes[0]["reason"].asText(),
                AirbyteRecordMessageMetaChange.Reason.SOURCE_FIELD_SIZE_LIMITATION.value()
            )
        }

        // Specifically verify that bad fields were captures for supporting formats
        // (ie, Avro and Parquet)
        if (supportsChangeCapture) {
            // Expect the second message id field to have been nulled due to type conversion error.
            val badRow = destinationOutput[1]
            val data = getData(badRow)

            Assertions.assertTrue(data["id"] == null || data["id"].isNull)
            val changes = getMeta(badRow)["changes"].elements().asSequence().toList()

            Assertions.assertEquals(1, changes.size)
            Assertions.assertEquals("id", changes[0]["field"].asText())
            Assertions.assertEquals(
                AirbyteRecordMessageMetaChange.Change.NULLED.value(),
                changes[0]["change"].asText()
            )
            Assertions.assertEquals(
                AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR.value(),
                changes[0]["reason"].asText()
            )

            // Expect the third message to have added a new change to an old one
            val badRowWithPreviousChange = destinationOutput[3]
            val dataWithPreviousChange = getData(badRowWithPreviousChange)
            Assertions.assertTrue(
                dataWithPreviousChange["id"] == null || dataWithPreviousChange["id"].isNull
            )
            val twoChanges =
                getMeta(badRowWithPreviousChange)["changes"].elements().asSequence().toList()
            Assertions.assertEquals(2, twoChanges.size)
        }
    }

    private fun toTimeTypeMap(
        schemaMap: Map<String, JsonNode>,
        format: String
    ): Map<String, Map<String, Boolean>> {
        return schemaMap.mapValues { schema ->
            schema.value["properties"]
                .fields()
                .asSequence()
                .filter { (_, value) -> value["format"]?.asText() == format }
                .map { (key, value) ->
                    val hasTimeZone =
                        !(value.has("airbyte_type") &&
                                value["airbyte_type"]!!.asText().endsWith("without_timezone"))
                    key to hasTimeZone
                }
                .toMap()
        }
    }

    @Test
    open fun testAirbyteTimeTypes() {
        val configuredCatalog =
            Jsons.deserialize(
                MoreResources.readResource("v0/every_time_type_configured_catalog.json"),
                ConfiguredAirbyteCatalog::class.java
            )
        val config = getConfig()
        val messages =
            MoreResources.readResource("v0/every_time_type_messages.txt").trim().lines().map {
                Jsons.deserialize(it, AirbyteMessage::class.java)
            }

        val expectedByStream =
            messages.filter { it.type == AirbyteMessage.Type.RECORD }.groupBy { it.record.stream }
        val schemasByStreamName =
            configuredCatalog.streams
                .associateBy { it.stream.name }
                .mapValues { it.value.stream.jsonSchema }
        val dateFieldMeta = toTimeTypeMap(schemasByStreamName, "date")
        val datetimeFieldMeta = toTimeTypeMap(schemasByStreamName, "date-time")
        val timeFieldMeta = toTimeTypeMap(schemasByStreamName, "time")

        runSyncAndVerifyStateOutput(config, messages, configuredCatalog, false)
        for (stream in configuredCatalog.streams) {
            val name = stream.stream.name
            val schema = stream.stream.jsonSchema
            val records =
                retrieveRecordsDataOnly(
                    testEnv,
                    stream.stream.name,
                    getDefaultSchema(config)!!, /* ignored */
                    schema
                )
            val actual = records.map { node -> pruneAndMaybeFlatten(node) }
            val expected =
                expectedByStream[stream.stream.name]!!.map {
                    if (expectNumericTimestamps) {
                        val node = MoreMappers.initMapper().createObjectNode()
                        it.record.data.fields().forEach { (k, v) ->
                            if (dateFieldMeta[name]!!.containsKey(k)) {
                                val daysSinceEpoch = LocalDate.parse(v.asText()).toEpochDay()
                                node.put(k, daysSinceEpoch.toInt())
                            } else if (datetimeFieldMeta[name]!!.containsKey(k)) {
                                val hasTimeZone = datetimeFieldMeta[name]!![k]!!
                                val millisSinceEpoch =
                                    if (hasTimeZone) {
                                        Instant.parse(v.asText()).toEpochMilli() * 1000L
                                    } else {
                                        LocalDateTime.parse(v.asText())
                                            .toInstant(ZoneOffset.UTC)
                                            .toEpochMilli() * 1000L
                                    }
                                node.put(k, millisSinceEpoch)
                            } else if (timeFieldMeta[name]!!.containsKey(k)) {
                                val hasTimeZone = timeFieldMeta[name]!![k]!!
                                val timeOfDayMicros =
                                    if (hasTimeZone) {
                                        val offsetTime = OffsetTime.parse(v.asText())
                                        val microsLocal =
                                            offsetTime.toLocalTime().toNanoOfDay() / 1000L
                                        val microsUTC =
                                            microsLocal -
                                                    offsetTime.offset.totalSeconds * 1_000_000L
                                        if (microsUTC < 0) {
                                            microsUTC + 24L * 60L * 60L * 1_000_000L
                                        } else {
                                            microsUTC
                                        }
                                    } else {
                                        LocalTime.parse(v.asText()).toNanoOfDay() / 1000L
                                    }
                                node.put(k, timeOfDayMicros)
                            } else {
                                node.set(k, v)
                            }
                        }
                        node
                    } else {
                        it.record.data
                    }
                }

            Assertions.assertEquals(expected, actual)
        }
    }

    @Test
    fun testProblematicTypes() {
        // Kind of a hack, since we'd prefer to test this not happen on some destinations,
        // but verifiying that for CSV is painful.
        Assumptions.assumeTrue(
            expectSchemalessObjectsCoercedToStrings || expectUnionsPromotedToDisjointRecords
        )

        // Run the sync
        val configuredCatalog =
            Jsons.deserialize(
                MoreResources.readResource("v0/problematic_types_configured_catalog.json"),
                ConfiguredAirbyteCatalog::class.java
            )
        val config = getConfig()
        val messagesIn =
            MoreResources.readResource("v0/problematic_types_messages_in.txt").trim().lines().map {
                Jsons.deserialize(it, AirbyteMessage::class.java)
            }

        runSyncAndVerifyStateOutput(config, messagesIn, configuredCatalog, false)

        // Collect destination data, using the correct transformed schema
        val destinationSchemaStr =
            if (!expectUnionsPromotedToDisjointRecords) {
                MoreResources.readResource("v0/problematic_types_coerced_schemaless_schema.json")
            } else {
                MoreResources.readResource("v0/problematic_types_disjoint_union_schema.json")
            }
        val destinationSchema = Jsons.deserialize(destinationSchemaStr, JsonNode::class.java)
        val actual =
            retrieveRecordsDataOnly(
                testEnv,
                "problematic_types",
                getDefaultSchema(config)!!,
                destinationSchema
            )

        // Validate data
        val expectedMessages =
            if (!expectUnionsPromotedToDisjointRecords) {
                MoreResources.readResource(
                    "v0/problematic_types_coerced_schemaless_messages_out.txt"
                )
            } else { // expectSchemalessObjectsCoercedToStrings
                MoreResources.readResource(
                    "v0/problematic_types_disjoint_union_messages_out.txt"
                )
            }
                .trim()
                .lines()
                .map { Jsons.deserialize(it, JsonNode::class.java) }
        actual.forEachIndexed { i, record: JsonNode ->
            Assertions.assertEquals(expectedMessages[i], record, "Record $i")
        }
    }

    /**
     * This test MUST be disabled by default, but you may uncomment it and use when need to
     * reproduce a performance issue for destination. This test helps you to emulate lot's of stream
     * and messages in each simply changing the "streamsSize" args to set a number of tables\streams
     * and the "messagesNumber" to a messages number that would be written in each stream. !!! Do
     * NOT forget to manually remove all generated objects !!! Hint: To check the destination
     * container output run "docker ps" command in console to find the container's id. Then run
     * "docker container attach your_containers_id" (ex. docker container attach 18cc929f44c8) to
     * see the container's output
     */
    @Test
    @Disabled
    @Throws(Exception::class)
    fun testStressPerformance() {
        val streamsSize = 5 // number of generated streams
        val messagesNumber = 300 // number of msg to be written to each generated stream

        // Each stream will have an id and name fields
        val USERS_STREAM_NAME = "users" // stream's name prefix. Will get "user0", "user1", etc.
        val ID = "id"
        val NAME = "name"

        // generate schema\catalogs
        val configuredAirbyteStreams: MutableList<AirbyteStream> = ArrayList()
        for (i in 0 until streamsSize) {
            configuredAirbyteStreams.add(
                CatalogHelpers.createAirbyteStream(
                    USERS_STREAM_NAME + i,
                    Field.of(NAME, JsonSchemaType.STRING),
                    Field.of(ID, JsonSchemaType.STRING)
                )
            )
        }
        val testCatalog = AirbyteCatalog().withStreams(configuredAirbyteStreams)
        val configuredTestCatalog = CatalogHelpers.toDefaultConfiguredCatalog(testCatalog)

        val config = getConfig()
        val destinationConfig =
            WorkerDestinationConfig()
                .withConnectionId(UUID.randomUUID())
                .withCatalog(
                    convertProtocolObject(
                        configuredTestCatalog,
                        io.airbyte.protocol.models.ConfiguredAirbyteCatalog::class.java
                    )
                )
                .withDestinationConnectionConfiguration(config)
        val destination = destination

        // Start destination
        destination.start(destinationConfig, jobRoot, emptyMap())

        val currentStreamNumber = AtomicInteger(0)
        val currentRecordNumberForStream = AtomicInteger(0)

        // this is just a current state logger. Useful when running long hours tests to see the
        // progress
        val countPrinter = Thread {
            while (true) {
                println(
                    "currentStreamNumber=" +
                            currentStreamNumber +
                            ", currentRecordNumberForStream=" +
                            currentRecordNumberForStream +
                            ", " +
                            Instant.now()
                )
                try {
                    Thread.sleep(10000)
                } catch (e: InterruptedException) {
                    e.printStackTrace()
                }
            }
        }
        countPrinter.start()

        // iterate through streams
        for (streamCounter in 0 until streamsSize) {
            LOGGER.info { "Started new stream processing with #$streamCounter" }
            // iterate through msm inside a particular stream
            // Generate messages and put it to stream
            for (msgCounter in 0 until messagesNumber) {
                val msg =
                    io.airbyte.protocol.models.v0
                        .AirbyteMessage()
                        .withType(AirbyteMessage.Type.RECORD)
                        .withRecord(
                            AirbyteRecordMessage()
                                .withStream(USERS_STREAM_NAME + streamCounter)
                                .withData(
                                    Jsons.jsonNode(
                                        ImmutableMap.builder<Any, Any>()
                                            .put(NAME, LOREM_IPSUM)
                                            .put(ID, streamCounter.toString() + "_" + msgCounter)
                                            .build()
                                    )
                                )
                                .withEmittedAt(Instant.now().toEpochMilli())
                        )
                try {
                    destination.accept(
                        convertProtocolObject(
                            msg,
                            io.airbyte.protocol.models.AirbyteMessage::class.java
                        )
                    )
                } catch (e: Exception) {
                    LOGGER.error { "Failed to write a RECORD message: $e" }
                    throw RuntimeException(e)
                }

                currentRecordNumberForStream.set(msgCounter)
            }

            // send state message here, it's required
            val msgState =
                io.airbyte.protocol.models.v0
                    .AirbyteMessage()
                    .withType(AirbyteMessage.Type.STATE)
                    .withState(
                        AirbyteStateMessage()
                            .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                            .withGlobal(
                                AirbyteGlobalState()
                                    .withSharedState(
                                        Jsons.jsonNode(
                                            ImmutableMap.builder<Any, Any>()
                                                .put("start_date", "2020-09-02")
                                                .build()
                                        )
                                    )
                            )
                    )
            try {
                destination.accept(
                    convertProtocolObject(
                        msgState,
                        io.airbyte.protocol.models.AirbyteMessage::class.java
                    )
                )
            } catch (e: Exception) {
                LOGGER.error { "Failed to write a STATE message: $e" }
                throw RuntimeException(e)
            }

            currentStreamNumber.set(streamCounter)
        }

        LOGGER.info {
            String.format(
                "Added %s messages to each of %s streams",
                currentRecordNumberForStream,
                currentStreamNumber
            )
        }
        // Close destination
        destination.notifyEndOfInput()
    }

    @ParameterizedTest
    @ArgumentsSource(DataTypeTestArgumentProvider::class)
    @Throws(Exception::class)
    open fun testDataTypeTestWithNormalization(
        messagesFilename: String,
        catalogFilename: String,
        testCompatibility: DataTypeTestArgumentProvider.TestCompatibility
    ) {
        if (!checkTestCompatibility(testCompatibility)) {
            return
        }

        val catalog = readCatalogFromFile(catalogFilename)
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        configuredCatalog.streams.forEach {
            it.withSyncId(42).withGenerationId(12).withMinimumGenerationId(12)
        }
        val messages = readMessagesFromFile(messagesFilename)

        runAndCheck(catalog, configuredCatalog, messages)
    }

    @Test
    @Throws(Exception::class)
    fun testSyncNumberNanDataType() {
        // NaN/Infinity protocol supports started from V1 version or higher
        val numericTypesSupport = specialNumericTypesSupportTest
        if (getProtocolVersion() == ProtocolVersion.V0 || !numericTypesSupport.supportNumberNan) {
            return
        }
        val catalog =
            readCatalogFromFile(
                ArgumentProviderUtil.prefixFileNameByVersion(
                    DataTypeTestArgumentProvider.Companion.NUMBER_TYPE_CATALOG,
                    getProtocolVersion()
                )
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        val messages =
            readMessagesFromFile(
                ArgumentProviderUtil.prefixFileNameByVersion(
                    DataTypeTestArgumentProvider.Companion.NAN_TYPE_MESSAGE,
                    getProtocolVersion()
                )
            )

        runAndCheck(catalog, configuredCatalog, messages)
    }

    @Test
    @Throws(Exception::class)
    fun testSyncIntegerNanDataType() {
        // NaN/Infinity protocol supports started from V1 version or higher
        val numericTypesSupport = specialNumericTypesSupportTest
        if (getProtocolVersion() == ProtocolVersion.V0 || !numericTypesSupport.supportIntegerNan) {
            return
        }
        val catalog =
            readCatalogFromFile(
                ArgumentProviderUtil.prefixFileNameByVersion(
                    DataTypeTestArgumentProvider.Companion.INTEGER_TYPE_CATALOG,
                    getProtocolVersion()
                )
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        val messages =
            readMessagesFromFile(
                ArgumentProviderUtil.prefixFileNameByVersion(
                    DataTypeTestArgumentProvider.Companion.NAN_TYPE_MESSAGE,
                    getProtocolVersion()
                )
            )

        runAndCheck(catalog, configuredCatalog, messages)
    }

    @Test
    @Throws(Exception::class)
    fun testSyncNumberInfinityDataType() {
        // NaN/Infinity protocol supports started from V1 version or higher
        val numericTypesSupport = specialNumericTypesSupportTest
        if (
            getProtocolVersion() == ProtocolVersion.V0 || !numericTypesSupport.supportNumberInfinity
        ) {
            return
        }
        val catalog =
            readCatalogFromFile(
                ArgumentProviderUtil.prefixFileNameByVersion(
                    DataTypeTestArgumentProvider.Companion.NUMBER_TYPE_CATALOG,
                    getProtocolVersion()
                )
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        val messages =
            readMessagesFromFile(
                ArgumentProviderUtil.prefixFileNameByVersion(
                    DataTypeTestArgumentProvider.Companion.INFINITY_TYPE_MESSAGE,
                    getProtocolVersion()
                )
            )

        runAndCheck(catalog, configuredCatalog, messages)
    }

    @Test
    @Throws(Exception::class)
    fun testSyncIntegerInfinityDataType() {
        // NaN/Infinity protocol supports started from V1 version or higher
        val numericTypesSupport = specialNumericTypesSupportTest
        if (
            getProtocolVersion() == ProtocolVersion.V0 ||
            !numericTypesSupport.supportIntegerInfinity
        ) {
            return
        }
        val catalog =
            readCatalogFromFile(
                ArgumentProviderUtil.prefixFileNameByVersion(
                    DataTypeTestArgumentProvider.Companion.INTEGER_TYPE_CATALOG,
                    getProtocolVersion()
                )
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        val messages =
            readMessagesFromFile(
                ArgumentProviderUtil.prefixFileNameByVersion(
                    DataTypeTestArgumentProvider.Companion.INFINITY_TYPE_MESSAGE,
                    getProtocolVersion()
                )
            )

        runAndCheck(catalog, configuredCatalog, messages)
    }

    companion object {
        private const val DUMMY_CATALOG_NAME = "DummyCatalog"

        private const val LOREM_IPSUM =
            ("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque malesuada lacinia aliquet. Nam feugiat mauris vel magna dignissim feugiat. Nam non dapibus sapien, ac mattis purus. Donec mollis libero erat, a rutrum ipsum pretium id. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Integer nec aliquam leo. Aliquam eu dictum augue, a ornare elit.\n" +
                    "\n" +
                    "Nulla viverra blandit neque. Nam blandit varius efficitur. Nunc at sapien blandit, malesuada lectus vel, tincidunt orci. Proin blandit metus eget libero facilisis interdum. Aenean luctus scelerisque orci, at scelerisque sem vestibulum in. Nullam ornare massa sed dui efficitur, eget volutpat lectus elementum. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Integer elementum mi vitae erat eleifend iaculis. Nullam eget tincidunt est, eget tempor est. Sed risus velit, iaculis vitae est in, volutpat consectetur odio. Aenean ut fringilla elit. Suspendisse non aliquet massa. Curabitur suscipit metus nunc, nec porttitor velit venenatis vel. Fusce vestibulum eleifend diam, lobortis auctor magna.\n" +
                    "\n" +
                    "Etiam maximus, mi feugiat pharetra mattis, nulla neque euismod metus, in congue nunc sem nec ligula. Curabitur aliquam, risus id convallis cursus, nunc orci sollicitudin enim, quis scelerisque nibh dui in ipsum. Suspendisse mollis, metus a dapibus scelerisque, sapien nulla pretium ipsum, non finibus sem orci et lectus. Aliquam dictum magna nisi, a consectetur urna euismod nec. In pulvinar facilisis nulla, id mollis libero pulvinar vel. Nam a commodo leo, eu commodo dolor. In hac habitasse platea dictumst. Curabitur auctor purus quis tortor laoreet efficitur. Quisque tincidunt, risus vel rutrum fermentum, libero urna dignissim augue, eget pulvinar nibh ligula ut tortor. Vivamus convallis non risus sed consectetur. Etiam accumsan enim ac nisl suscipit, vel congue lorem volutpat. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce non orci quis lacus rhoncus vestibulum nec ut magna. In varius lectus nec quam posuere finibus. Vivamus quis lectus vitae tortor sollicitudin fermentum.\n" +
                    "\n" +
                    "Pellentesque elementum vehicula egestas. Sed volutpat velit arcu, at imperdiet sapien consectetur facilisis. Suspendisse porttitor tincidunt interdum. Morbi gravida faucibus tortor, ut rutrum magna tincidunt a. Morbi eu nisi eget dui finibus hendrerit sit amet in augue. Aenean imperdiet lacus enim, a volutpat nulla placerat at. Suspendisse nibh ipsum, venenatis vel maximus ut, fringilla nec felis. Sed risus mi, egestas quis quam ullamcorper, pharetra vestibulum diam.\n" +
                    "\n" +
                    "Praesent finibus scelerisque elit, accumsan condimentum risus mattis vitae. Donec tristique hendrerit facilisis. Curabitur metus purus, venenatis non elementum id, finibus eu augue. Quisque posuere rhoncus ligula, et vehicula erat pulvinar at. Pellentesque vel quam vel lectus tincidunt congue quis id sapien. Ut efficitur mauris vitae pretium iaculis. Aliquam consectetur iaculis nisi vitae laoreet. Integer vel odio quis diam mattis tempor eget nec est. Donec iaculis facilisis neque, at dictum magna vestibulum ut. Sed malesuada non nunc ac consequat. Maecenas tempus lectus a nisl congue, ac venenatis diam viverra. Nam ac justo id nulla iaculis lobortis in eu ligula. Vivamus et ligula id sapien efficitur aliquet. Curabitur est justo, tempus vitae mollis quis, tincidunt vitae felis. Vestibulum molestie laoreet justo, nec mollis purus vulputate at.")
    }
}
