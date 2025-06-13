/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.EnvVarConstants
import io.airbyte.cdk.load.command.Property
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.config.NamespaceDefinitionType
import io.airbyte.cdk.load.config.NamespaceMappingConfig
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import io.airbyte.cdk.load.message.InputMessage
import io.airbyte.cdk.load.message.InputMessageOther
import io.airbyte.cdk.load.message.InputRecord
import io.airbyte.cdk.load.message.InputStreamCheckpoint
import io.airbyte.cdk.load.message.InputStreamComplete
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.airbyte.cdk.load.test.util.destination_process.DestinationProcessFactory
import io.airbyte.cdk.load.test.util.destination_process.DestinationUncleanExitException
import io.airbyte.cdk.load.test.util.destination_process.DockerizedDestination
import io.airbyte.protocol.models.v0.AirbyteAnalyticsTraceMessage
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import java.time.Instant
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicReference
import kotlin.test.assertEquals
import kotlin.test.fail
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import org.apache.commons.lang3.RandomStringUtils
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.TestInfo
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.api.extension.ExtendWith
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode
import uk.org.webcompere.systemstubs.environment.EnvironmentVariables
import uk.org.webcompere.systemstubs.jupiter.SystemStub
import uk.org.webcompere.systemstubs.jupiter.SystemStubsExtension

@Execution(ExecutionMode.CONCURRENT)
// Spotbugs doesn't let you suppress the actual lateinit property,
// so we have to suppress the entire class.
// Thanks, spotbugs.
@SuppressFBWarnings("NP_NONNULL_RETURN_VIOLATION", justification = "Micronaut DI")
@ExtendWith(SystemStubsExtension::class)
abstract class IntegrationTest(
    additionalMicronautEnvs: List<String>,
    val dataDumper: DestinationDataDumper,
    /** This object MUST be a singleton. It will be invoked exactly once per gradle run. */
    val destinationCleaner: DestinationCleaner,
    val recordMangler: ExpectedRecordMapper = NoopExpectedRecordMapper,
    val nameMapper: NameMapper = NoopNameMapper,
    /** See [RecordDiffer.nullEqualsUnset]. */
    val nullEqualsUnset: Boolean = false,
    val configUpdater: ConfigurationUpdater = FakeConfigurationUpdater,
    val micronautProperties: Map<Property, String> = emptyMap(),
    val dataChannelMedium: DataChannelMedium = DataChannelMedium.STDIO,
    val dataChannelFormat: DataChannelFormat = DataChannelFormat.PROTOBUF
) {
    // Intentionally don't inject the actual destination process - we need a full factory
    // because some tests want to run multiple syncs, so we need to run the destination
    // multiple times.
    val destinationProcessFactory = DestinationProcessFactory.get(additionalMicronautEnvs)

    @Suppress("DEPRECATION") private val randomSuffix = RandomStringUtils.randomAlphabetic(4)
    private val timestampString =
        LocalDateTime.ofInstant(Instant.now(), ZoneOffset.UTC)
            .format(randomizedNamespaceDateFormatter)
    // stream name doesn't need to be randomized, only the namespace.
    val randomizedNamespace = "test$timestampString$randomSuffix"

    // junit is a bit wonky with injecting TestInfo.
    // You can declare it as a constructor param, but you get a TestInfo instance
    // that doesn't know what test method it's running in.
    // You can also declare it as a param on the test function, but that's just
    // less convenient.
    // This is the only way to avoid copying the TestInfo stuff everywhere :/
    // (I don't think micronaut can inject this object, unfortunately)
    protected lateinit var testInfo: TestInfo
    protected lateinit var testPrettyName: String

    @BeforeEach
    fun getTestInfo(testInfo: TestInfo) {
        this.testInfo = testInfo
        testPrettyName = "${testInfo.testClass.get().simpleName}.${testInfo.displayName}"
        destinationProcessFactory.testName = testPrettyName
    }

    @AfterEach
    fun teardown() {
        // some tests (e.g. CheckIntegrationTest) hardcode the noop cleaner.
        // so just skip all the fancy logic if we detect it.
        if (destinationCleaner == NoopDestinationCleaner) {
            return
        }

        if (hasRunCleaner.compareAndSet(false, true)) {
            destinationCleaner.cleanup()
        }

        // Simple guardrail to prevent people from doing the wrong thing,
        // since it's not immediately intuitive.
        val firstCleaner = cleanerSeen.compareAndSet(null, destinationCleaner)
        val sameCleaner = cleanerSeen.compareAndSet(destinationCleaner, destinationCleaner)
        if (!(firstCleaner || sameCleaner)) {
            throw IllegalStateException(
                """
                Multiple DestinationCleaner instances detected. This is not supported. The cleaner MUST be a singleton.
                Cleaners detected:
                  $destinationCleaner
                  ${cleanerSeen.get()}
                """.trimIndent()
            )
        }
    }

    fun dumpAndDiffRecords(
        config: ConfigurationSpecification,
        canonicalExpectedRecords: List<OutputRecord>,
        stream: DestinationStream,
        primaryKey: List<List<String>>,
        cursor: List<String>?,
        reason: String? = null,
        allowUnexpectedRecord: Boolean = false,
    ) {
        val actualRecords: List<OutputRecord> = dataDumper.dumpRecords(config, stream)
        val expectedRecords: List<OutputRecord> =
            canonicalExpectedRecords.map { recordMangler.mapRecord(it, stream.schema) }
        val descriptor = recordMangler.mapStreamDescriptor(stream.descriptor)

        RecordDiffer(
                primaryKey = primaryKey.map { nameMapper.mapFieldName(it) },
                cursor = cursor?.let { nameMapper.mapFieldName(it) },
                nullEqualsUnset = nullEqualsUnset,
                allowUnexpectedRecord = allowUnexpectedRecord,
            )
            .diffRecords(expectedRecords, actualRecords)
            ?.let {
                var message =
                    "Incorrect records for ${descriptor.namespace}.${descriptor.name}:\n$it"
                if (reason != null) {
                    message = reason + "\n" + message
                }
                fail(message)
            }

        assertEquals(
            actualRecords.size,
            actualRecords.map { it.rawId }.toSet().size,
            "Expected each record to have a unique UUID",
        )
    }

    /**
     * Convenience wrapper for syncs that are expected to fail. Example usage:
     * ```
     * val failure = expectFailure {
     *   runSync(...)
     * }
     * assertContains(failure.message, "Invalid widget")
     * ```
     */
    fun expectFailure(
        failureType: AirbyteErrorTraceMessage.FailureType =
            AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR,
        f: () -> Unit,
    ): AirbyteErrorTraceMessage {
        val e = assertThrows<DestinationUncleanExitException> { f() }
        return e.traceMessages.first { it.failureType == failureType }
    }

    /** Convenience wrapper for [runSync] using a single stream. */
    fun runSync(
        configContents: String,
        stream: DestinationStream,
        messages: List<InputMessage>,
        streamStatus: AirbyteStreamStatus? = AirbyteStreamStatus.COMPLETE,
        useFileTransfer: Boolean = false,
        destinationProcessFactory: DestinationProcessFactory = this.destinationProcessFactory,
    ): List<AirbyteMessage> =
        runSync(
            configContents,
            DestinationCatalog(listOf(stream)),
            messages,
            streamStatus,
            useFileTransfer = useFileTransfer,
            destinationProcessFactory,
        )

    /**
     * Run a sync with the given config+stream+messages, sending a trace message at the end of the
     * sync with the given stream status for every stream. [messages] should not include
     * [AirbyteStreamStatus] messages unless [streamStatus] is set to `null` (unless you actually
     * want to send multiple stream status messages).
     */
    @OptIn(ExperimentalCoroutinesApi::class)
    fun runSync(
        configContents: String,
        catalog: DestinationCatalog,
        messages: List<InputMessage>,
        /**
         * If you set this to anything other than `COMPLETE`, you may run into a race condition.
         * It's recommended that you send an explicit state message in [messages], and run the sync
         * in a loop until it acks the state message, e.g.
         * ```
         * while (true) {
         *   val e = assertThrows<DestinationUncleanExitException> {
         *     runSync(
         *       ...,
         *       listOf(
         *         ...,
         *         StreamCheckpoint(...),
         *       ),
         *       ...
         *     )
         *   }
         *   if (e.stateMessages.isNotEmpty()) { break }
         * }
         * ```
         */
        streamStatus: AirbyteStreamStatus? = AirbyteStreamStatus.COMPLETE,
        useFileTransfer: Boolean = false,
        destinationProcessFactory: DestinationProcessFactory = this.destinationProcessFactory,
        namespaceMappingConfig: NamespaceMappingConfig? = null,
    ): List<AirbyteMessage> {
        check(streamStatus == null || streamStatus == AirbyteStreamStatus.COMPLETE) {
            "Invalid stream status: $streamStatus"
        }
        destinationProcessFactory.testName = testPrettyName

        val destination =
            destinationProcessFactory.createDestinationProcess(
                "write",
                configContents,
                catalog.asProtocolObject(),
                useFileTransfer = useFileTransfer,
                micronautProperties = micronautProperties,
                dataChannelMedium = dataChannelMedium,
                dataChannelFormat = dataChannelFormat,
                namespaceMappingConfig = namespaceMappingConfig
                        ?: NamespaceMappingConfig(
                            NamespaceDefinitionType.SOURCE,
                        ),
            )
        return runBlocking(Dispatchers.IO) {
            launch { destination.run() }
            messages.forEach { destination.sendMessage(it) }
            if (streamStatus != null) {
                catalog.streams.forEach {
                    val streamStatusMessage =
                        when (streamStatus) {
                            AirbyteStreamStatus.COMPLETE ->
                                InputStreamComplete(
                                    DestinationRecordStreamComplete(it, System.currentTimeMillis())
                                )
                            else ->
                                throw IllegalStateException(
                                    "Impossible: We checked that the stream status was valid at the start of this method. Somehow got $streamStatus."
                                )
                        }
                    destination.sendMessage(
                        streamStatusMessage,
                        broadcast = true,
                    )
                }
            }
            destination.shutdown()
            if (useFileTransfer) {
                destination.verifyFileDeleted()
            }
            destination.readMessages()
        }
    }

    enum class UncleanSyncEndBehavior {
        /**
         * End the sync normally (i.e. by closing stdin), but don't send a COMPLETE status message.
         */
        TERMINATE_WITH_NO_STREAM_STATUS,

        // TODO no test actually uses this right now, should we just remove it?
        UNPARSEABLE_MESSAGE,

        /** Forcibly kill the sync. */
        KILL,
    }

    /**
     * Run a sync until it acknowledges the given state message, then kill the sync. This method is
     * useful for tests that want to verify recovery-from-failure cases, e.g. truncate refresh
     * behaviors.
     *
     * A common pattern is to call [runSyncUntilStateAckAndExpectFailure], and then call
     * `dumpAndDiffRecords(..., allowUnexpectedRecord = true)` to verify that [records] were written
     * to the destination.
     *
     * This forces the connector to run with microbatching enabled - without that option, tests
     * using this method would take significantly longer, because they would need to push 100MB
     * (ish) to the destination before it would ack a state message.
     */
    fun runSyncUntilStateAckAndExpectFailure(
        configContents: String,
        stream: DestinationStream,
        records: List<InputRecord>,
        inputStateMessage: StreamCheckpoint,
        syncEndBehavior: UncleanSyncEndBehavior,
        useFileTransfer: Boolean = false,
        destinationProcessFactory: DestinationProcessFactory = this.destinationProcessFactory,
    ): AirbyteStateMessage {
        val destination =
            destinationProcessFactory.createDestinationProcess(
                "write",
                configContents,
                DestinationCatalog(listOf(stream)).asProtocolObject(),
                useFileTransfer,
                micronautProperties = micronautProperties + micronautPropertyEnableMicrobatching,
                dataChannelMedium = dataChannelMedium,
                dataChannelFormat = dataChannelFormat,
                namespaceMappingConfig = NamespaceMappingConfig(NamespaceDefinitionType.SOURCE),
            )
        var outputStateMessage: AirbyteStateMessage? = null
        fun doRun() =
            runBlocking(Dispatchers.IO) {
                launch { destination.run() }
                records.forEach { destination.sendMessage(it) }
                destination.sendMessage(InputStreamCheckpoint(inputStateMessage))
                val noopTraceMessage =
                    AirbyteMessage()
                        .withType(AirbyteMessage.Type.TRACE)
                        .withTrace(
                            AirbyteTraceMessage()
                                .withType(AirbyteTraceMessage.Type.ANALYTICS)
                                .withAnalytics(
                                    AirbyteAnalyticsTraceMessage().withType("foo").withValue("bar")
                                )
                                .withEmittedAt(System.currentTimeMillis().toDouble())
                        )

                while (true) {
                    destination.sendMessage(InputMessageOther(noopTraceMessage), false)
                    val returnedMessages = destination.readMessages()
                    if (returnedMessages.any { it.type == AirbyteMessage.Type.STATE }) {
                        outputStateMessage =
                            returnedMessages
                                .filter { it.type == AirbyteMessage.Type.STATE }
                                .map { it.state }
                                .first()
                        break
                    }
                    // don't just spam the input stream, give the destination time to actually
                    // process the messages we're pushing into it
                    delay(1)
                }
                when (syncEndBehavior) {
                    UncleanSyncEndBehavior.TERMINATE_WITH_NO_STREAM_STATUS -> destination.shutdown()
                    UncleanSyncEndBehavior.UNPARSEABLE_MESSAGE -> {
                        destination.sendMessage("{\"unparseable")
                        destination.shutdown()
                    }
                    UncleanSyncEndBehavior.KILL -> destination.kill()
                }
            }
        if (
            destination is DockerizedDestination && syncEndBehavior == UncleanSyncEndBehavior.KILL
        ) {
            // when you kill a docker process, it doesn't exit uncleanly apparently
            doRun()
        } else {
            // expect an exception. we're sending a stream incomplete or killing the
            // destination, so it's expected to crash
            assertThrows<DestinationUncleanExitException> { doRun() }
        }
        return outputStateMessage!!
    }

    fun updateConfig(config: String): String = configUpdater.update(config)

    companion object {
        const val NUM_SOCKETS = 2

        val randomizedNamespaceRegex = Regex("test(\\d{8})[A-Za-z]{4}.*")
        val randomizedNamespaceDateFormatter: DateTimeFormatter =
            DateTimeFormatter.ofPattern("yyyyMMdd")

        /**
         * When set, this property forces the CDK to invoke processRecords once per record. This
         * allows tests which depend on state acks to run quickly.
         */
        val micronautPropertyEnableMicrobatching: Map<Property, String> =
            mapOf(EnvVarConstants.RECORD_BATCH_SIZE to "1")

        /**
         * Given a randomizedNamespace (such as `test20241216abcd`), return whether the namespace
         * was created more than [retentionDays] days ago, and therefore should be deleted by a
         * [DestinationCleaner].
         */
        fun isNamespaceOld(namespace: String, retentionDays: Long = 30): Boolean {
            val cleanupCutoffDate = LocalDate.now().minusDays(retentionDays)
            val matchResult = randomizedNamespaceRegex.find(namespace)
            if (matchResult == null || matchResult.groups.isEmpty()) {
                return false
            }
            val namespaceCreationDate =
                LocalDate.parse(matchResult.groupValues[1], randomizedNamespaceDateFormatter)
            return namespaceCreationDate.isBefore(cleanupCutoffDate)
        }

        private val hasRunCleaner = AtomicBoolean(false)
        private val cleanerSeen = AtomicReference<DestinationCleaner>(null)

        // Connectors are calling System.getenv rather than using micronaut-y properties,
        // so we have to mock it out, instead of just setting more properties
        // inside NonDockerizedDestination.
        // This field has no effect on DockerizedDestination, which explicitly
        // sets env vars when invoking `docker run`.
        /**
         * You probably don't want to actually interact with this. This is generally intended to
         * support a specific legacy behavior. Prefer using micronaut properties when possible.
         */
        @SystemStub internal lateinit var nonDockerMockEnvVars: EnvironmentVariables

        @JvmStatic
        @BeforeAll
        fun setEnvVars() {
            nonDockerMockEnvVars.set("WORKER_JOB_ID", "0")
        }
    }
}
