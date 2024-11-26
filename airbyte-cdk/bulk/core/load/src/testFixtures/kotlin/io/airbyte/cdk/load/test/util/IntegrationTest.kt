/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.airbyte.cdk.load.test.util.destination_process.DestinationProcessFactory
import io.airbyte.cdk.load.test.util.destination_process.DestinationUncleanExitException
import io.airbyte.cdk.load.test.util.destination_process.NonDockerizedDestination
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
import java.time.Instant
import java.time.LocalDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import java.util.concurrent.atomic.AtomicBoolean
import kotlin.test.fail
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
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
    val dataDumper: DestinationDataDumper,
    val destinationCleaner: DestinationCleaner,
    val recordMangler: ExpectedRecordMapper = NoopExpectedRecordMapper,
    val nameMapper: NameMapper = NoopNameMapper,
    /** See [RecordDiffer.nullEqualsUnset]. */
    val nullEqualsUnset: Boolean = false,
) {
    // Intentionally don't inject the actual destination process - we need a full factory
    // because some tests want to run multiple syncs, so we need to run the destination
    // multiple times.
    val destinationProcessFactory = DestinationProcessFactory.get()

    @Suppress("DEPRECATION") private val randomSuffix = RandomStringUtils.randomAlphabetic(4)
    private val timestampString =
        LocalDateTime.ofInstant(Instant.now(), ZoneOffset.UTC)
            .format(DateTimeFormatter.ofPattern("YYYYMMDD"))
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
        if (hasRunCleaner.compareAndSet(false, true)) {
            destinationCleaner.cleanup()
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
            canonicalExpectedRecords.map { recordMangler.mapRecord(it) }

        RecordDiffer(
                primaryKey = primaryKey.map { nameMapper.mapFieldName(it) },
                cursor = cursor?.let { nameMapper.mapFieldName(it) },
                nullEqualsUnset = nullEqualsUnset,
                allowUnexpectedRecord = allowUnexpectedRecord,
            )
            .diffRecords(expectedRecords, actualRecords)
            ?.let {
                var message =
                    "Incorrect records for ${stream.descriptor.namespace}.${stream.descriptor.name}:\n$it"
                if (reason != null) {
                    message = reason + "\n" + message
                }
                fail(message)
            }
    }

    /** Convenience wrapper for [runSync] using a single stream. */
    fun runSync(
        configContents: String,
        stream: DestinationStream,
        messages: List<DestinationMessage>,
        streamStatus: AirbyteStreamStatus? = AirbyteStreamStatus.COMPLETE,
    ): List<AirbyteMessage> =
        runSync(configContents, DestinationCatalog(listOf(stream)), messages, streamStatus)

    /**
     * Run a sync with the given config+stream+messages, sending a trace message at the end of the
     * sync with the given stream status for every stream. [messages] should not include
     * [AirbyteStreamStatus] messages unless [streamStatus] is set to `null` (unless you actually
     * want to send multiple stream status messages).
     */
    fun runSync(
        configContents: String,
        catalog: DestinationCatalog,
        messages: List<DestinationMessage>,
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
    ): List<AirbyteMessage> {
        val destination =
            destinationProcessFactory.createDestinationProcess(
                "write",
                configContents,
                catalog.asProtocolObject(),
            )
        return runBlocking(Dispatchers.IO) {
            launch { destination.run() }
            messages.forEach { destination.sendMessage(it.asProtocolMessage()) }
            if (streamStatus != null) {
                catalog.streams.forEach {
                    destination.sendMessage(
                        DestinationRecordStreamComplete(it.descriptor, System.currentTimeMillis())
                            .asProtocolMessage()
                    )
                }
            }
            destination.shutdown()
            destination.readMessages()
        }
    }

    /**
     * Run a sync until it acknowledges the given state message, then kill the sync. This method
     * is useful for tests that want to verify recovery-from-failure cases, e.g. truncate refresh
     * behaviors.
     *
     * A common pattern is to call [runSyncUntilStateAck], and then call
     * `dumpAndDiffRecords(..., allowUnexpectedRecord = true)` to verify that [records] were
     * written to the destination.
     */
    fun runSyncUntilStateAck(
        configContents: String,
        stream: DestinationStream,
        records: List<DestinationRecord>,
        inputStateMessage: StreamCheckpoint,
        allowGracefulShutdown: Boolean,
    ): AirbyteStateMessage {
        val destination =
            destinationProcessFactory.createDestinationProcess(
                "write",
                configContents,
                DestinationCatalog(listOf(stream)).asProtocolObject(),
            )
        return runBlocking(Dispatchers.IO) {
            launch {
                // expect an exception. we're sending a stream incomplete or killing the
                // destination, so it's expected to crash
                // TODO: This is a hack, not sure what's going on
                if (destination is NonDockerizedDestination) {
                    assertThrows<DestinationUncleanExitException> { destination.run() }
                } else {
                    destination.run()
                }
            }
            records.forEach { destination.sendMessage(it.asProtocolMessage()) }
            destination.sendMessage(inputStateMessage.asProtocolMessage())

            val deferred = async {
                val outputStateMessage: AirbyteStateMessage
                while (true) {
                    destination.sendMessage("")
                    val returnedMessages = destination.readMessages()
                    if (returnedMessages.any { it.type == AirbyteMessage.Type.STATE }) {
                        outputStateMessage =
                            returnedMessages
                                .filter { it.type == AirbyteMessage.Type.STATE }
                                .map { it.state }
                                .first()
                        break
                    }
                }
                outputStateMessage
            }
            val outputStateMessage = deferred.await()
            if (allowGracefulShutdown) {
                destination.sendMessage("{\"unparseable")
                destination.shutdown()
            } else {
                destination.kill()
            }

            outputStateMessage
        }
    }

    companion object {
        private val hasRunCleaner = AtomicBoolean(false)

        // Connectors are calling System.getenv rather than using micronaut-y properties,
        // so we have to mock it out, instead of just setting more properties
        // inside NonDockerizedDestination.
        // This field has no effect on DockerizedDestination, which explicitly
        // sets env vars when invoking `docker run`.
        @SystemStub private lateinit var nonDockerMockEnvVars: EnvironmentVariables

        @JvmStatic
        @BeforeAll
        fun setEnvVars() {
            nonDockerMockEnvVars.set("WORKER_JOB_ID", "0")
        }
    }
}
