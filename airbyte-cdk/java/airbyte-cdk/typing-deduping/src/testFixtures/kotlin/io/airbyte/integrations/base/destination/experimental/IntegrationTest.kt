package io.airbyte.integrations.base.destination.experimental

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.base.Command
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.AirbyteMessage
import io.airbyte.protocol.models.AirbyteRecordMessage
import io.airbyte.protocol.models.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
import io.airbyte.protocol.models.AirbyteTraceMessage
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.ConfiguredAirbyteStream
import io.airbyte.protocol.models.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Duration
import java.time.Instant
import java.time.LocalDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit
import java.util.UUID
import org.apache.commons.lang3.RandomStringUtils
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.TestInfo
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode

private val logger = KotlinLogging.logger {}

@Execution(ExecutionMode.CONCURRENT)
abstract class IntegrationTest<Config>(
    // TODO which of these should be injectable vs manually instantiated?
    //   and if there's a mix, what's the best way to do that?
    // injectable - we want to switch between docker and jar tests
    private val destinationProcessFactory: DestinationProcessFactory<Config>,
    // Subclass is responsible for creating this config object
    // ... maybe we should somehow enforce that it has a randomized
    // default namespace, for destinations which support that concept
    private val config: Config,
    private val supportsRawData: Boolean = true,
    private val supportsFinalData: Boolean = true,
) {
    // IMO all destinations have at least one of these.
    // e.g. destination-s3 in avro mode _only_ has "final" records,
    // since we always write typed data.
    // We'll use the supportsRawData/supportsFinalData flags
    // to choose which one(s) to use.
    /**
     * Dump the records that we intend users to interact with. These should be
     * typed and deduped, assuming the destination supports those features.
     */
    abstract fun dumpFinalRecords(streamName: String, streamNamespace: String?): List<OutputRecord>
    /**
     * Some destinations persist "raw" data, which is typically an untyped,
     * append-only list of all records we've received. This function should
     * dump that data.
     */
    abstract fun dumpRawRecords(streamName: String, streamNamespace: String?): List<OutputRecord>

    // TODO we need separate methods for raw+final records (e.g. snowflake only upcases final table column names)
    // TODO do we ever need to pass more info into this method? e.g. the original stream schema
    abstract fun canonicalRecordToDestinationRecord(expectedRecord: ExpectedOutputRecord): ExpectedOutputRecord

    /**
     * Generic method to discover and delete old test data (files, tables, etc.).
     * We should define some standardized test naming scheme for this (e.g. all
     * test streams will have a namespace like `testns20240123someRandomCharacters%`)
     * to facilitate this.
     *
     * ... or we just write some cron for every destination, which monitors for
     * old schemas/etc. and deletes them once per week. Maybe that's better than
     * trying to do it inside the tests?
     */
    abstract fun cleanUpOldTestOutputs()

    private val randomSuffix = RandomStringUtils.randomAlphabetic(4)
    private val timestampString =
        LocalDateTime.ofInstant(Instant.now(), ZoneOffset.UTC)
            .format(DateTimeFormatter.ofPattern("YYYYMMDD"))
    // stream name doesn't need to be randomized, only the namespace.
    // we need braces because otherwise kotlin tries to find a val `timestampString_`
    val randomizedNamespace = "test${timestampString}$randomSuffix"

    // make this available by default, instead of needing to manually add it for every test case
    protected lateinit var testInfo: TestInfo

    @BeforeEach
    fun setup(testInfo: TestInfo) {
        this.testInfo = testInfo
    }

    fun dumpAndDiffRecords(
        canonicalExpectedRawRecords: List<ExpectedOutputRecord>,
        // TODO probably needs two lists (one for "with typecast nulling at root level", one
        //   for "with typecast nulling at all levels")
        canonicalExpectedFinalRecords: List<ExpectedOutputRecord>,
        streamName: String,
        streamNamespace: String?,
    ) {
        val expectedFinalRecords: List<ExpectedOutputRecord>
        val actualFinalRecords: List<OutputRecord>
        if (supportsFinalData) {
            // TODO we could inject some sort of backwards-mapping thing here
            actualFinalRecords = dumpFinalRecords(streamName, streamNamespace)
            expectedFinalRecords = canonicalExpectedRawRecords.map { canonicalRecordToDestinationRecord(it) }
        } else {
            actualFinalRecords = emptyList()
            expectedFinalRecords = emptyList()
        }

        // TODO similar thing for raw records

        TODO("use recorddiffer to diff the expected/actual records")
    }

    fun toProtocolMessages(
        records: List<InputRecord>,
        streamName: String,
        streamNamespace: String?,
        streamStatus: AirbyteStreamStatus? = AirbyteStreamStatus.COMPLETE
    ): List<AirbyteMessage> {
        val traceMessages: List<AirbyteMessage> =
            if (streamStatus != null) {
                listOf(
                    AirbyteMessage()
                        .withType(AirbyteMessage.Type.TRACE)
                        .withTrace(
                            AirbyteTraceMessage()
                                .withType(AirbyteTraceMessage.Type.STREAM_STATUS)
                                .withStreamStatus(
                                    AirbyteStreamStatusTraceMessage()
                                        .withStreamDescriptor(
                                            StreamDescriptor()
                                                .withName(streamName)
                                                .withNamespace(streamNamespace)
                                        ).withStatus(streamStatus)
                                )
                        )
                )
            } else {
                listOf()
            }
        return records.map { it.toAirbyteMessage(streamName, streamNamespace) } + traceMessages
    }

    fun runSync(
        stream: ConfiguredAirbyteStream,
        records: List<InputRecord>,
        streamStatus: AirbyteStreamStatus? = AirbyteStreamStatus.COMPLETE
    ) = runSync(
        ConfiguredAirbyteCatalog().withStreams(listOf(stream)),
        toProtocolMessages(
            records,
            stream.stream.name,
            stream.stream.namespace,
            streamStatus,
        ),
    )

    fun runSync(
        catalog: ConfiguredAirbyteCatalog,
        messages: List<AirbyteMessage>,
    ) {
        val destination = destinationProcessFactory.runDestination(
            Command.WRITE,
            config,
            catalog,
        )
        var destinationExited = false
        messages.forEach { inputMessage ->
            if (destinationExited) {
                throw IllegalStateException("Destination exited before it consumed all messages")
            }
            destination.sendMessage(inputMessage)
            destination.readMessages().forEach consumeDestinationOutput@ { outputMessage ->
                if (outputMessage == null) {
                    destinationExited = true
                    return@consumeDestinationOutput
                }
                // We could also e.g. capture state messages for verification
                if (outputMessage.type == AirbyteMessage.Type.LOG) {
                    logger.info { outputMessage.log.message }
                }
            }
        }
        while (true) {
            destination.readMessages().forEach { outputMessage ->
                if (outputMessage == null) {
                    return@forEach
                }
                if (outputMessage.type == AirbyteMessage.Type.LOG) {
                    logger.info { outputMessage.log.message }
                }
            }
            Thread.sleep(Duration.of(5, ChronoUnit.SECONDS))
        }
    }
}

interface DestinationProcess {
    fun sendMessage(message: AirbyteMessage)

    /**
     * Return all messages from the destination. When the destination exits, the last message
     * MUST be `null`.
     *
     * (mediocre interface, just for demo purposes)
     */
    fun readMessages(): List<AirbyteMessage?>

    fun waitUntilDone()
}

interface DestinationProcessFactory<Config> {
    fun runDestination(
        command: Command,
        config: Config,
        catalog: ConfiguredAirbyteCatalog,
    ): DestinationProcess
}

/**
 * A record that we want to insert into a destination. Basically just a clean version of
 * [io.airbyte.protocol.models.AirbyteRecordMessage].
 */
data class InputRecord(
    val extractedAt: Instant,
    val generationId: Long?,
    val data: JsonNode,
    val recordChanges: List<AirbyteRecordMessageMetaChange>?,
) {
    /**
     * Convenience constructors, so callers don't need to manually parse everything
     */
    constructor(
        extractedAt: Long,
        generationId: Long?,
        data: String,
        // TODO maybe easier to accept a string here and json deserialize to object
        recordChanges: List<AirbyteRecordMessageMetaChange>?,
    ): this(
        Instant.ofEpochMilli(extractedAt),
        generationId,
        Jsons.deserialize(data),
        recordChanges,
    )

    fun toAirbyteMessage(streamName: String, streamNamespace: String?): AirbyteMessage =
        AirbyteMessage()
            .withType(AirbyteMessage.Type.RECORD)
            .withRecord(
                AirbyteRecordMessage()
                    .withStream(streamName)
                    .withNamespace(streamNamespace)
                    .withEmittedAt(extractedAt.toEpochMilli())
                    .withData(data)
                    .withMeta(AirbyteRecordMessageMeta().withChanges(recordChanges))
            )
}

/**
 * A record that we read back from the destination.
 */
// TODO is it correct to strongly structure this, or should we just dump raw jsonnode?
//   (especially for when we don't have an explicit `data` subfield in the destination,
//   e.g. warehouse final tables, s3 avro files)
//   i.e. either destinations need to filter out the airbyte_* columns from the data blob,
//   or inject them into the expected record data blob
data class OutputRecord(
    val rawId: UUID,
    val extractedAt: Instant,
    val loadedAt: Instant?,
    val generationId: Long?,
    // strongly-typed map, e.g. ZonedDateTime for timestamp_with_timezone.
    // this makes destination test implementations easier.
    // values can be null, b/c e.g. warehouse destinations with a JSON column type
    // can be either SQL null, or JSON null, and we want to distinguish between those
    val data: Map<String, Any?>,
    val airbyteMeta: JsonNode?,
) {
    /**
     * Convenience constructor, so callers don't need to manually parse everything
     */
    constructor(
        rawId: String,
        extractedAt: Long,
        loadedAt: Long?,
        generationId: Long?,
        data: Map<String, Any?>,
        airbyteMeta: String?,
    ): this(
        UUID.fromString(rawId),
        Instant.ofEpochMilli(extractedAt),
        loadedAt?.let(Instant::ofEpochMilli),
        generationId,
        data,
        airbyteMeta?.let(Jsons::deserialize),
    )
}

// TODO this is almost identical to InputRecord, except that it has a full airbyteMeta
//   instead of just taking in changes - maybe merge them?
data class ExpectedOutputRecord(
    val extractedAt: Instant,
    val generationId: Long?,
    // see OutputRecord.data for explanation of why Map<String, Any?>
    val data: Map<String, Any?>,
    val airbyteMeta: JsonNode?,
) {
    /**
     * Convenience constructor, so callers don't need to manually parse everything
     */
    constructor(
        extractedAt: Long,
        generationId: Long?,
        data: Map<String, Any>,
        airbyteMeta: String?,
    ): this(
        Instant.ofEpochMilli(extractedAt),
        generationId,
        data,
        airbyteMeta?.let(Jsons::deserialize),
    )
}
