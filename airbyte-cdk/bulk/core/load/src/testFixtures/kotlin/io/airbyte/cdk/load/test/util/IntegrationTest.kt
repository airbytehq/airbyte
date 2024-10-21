/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.test.util.destination_process.DestinationProcessFactory
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.time.Instant
import java.time.LocalDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import java.util.concurrent.atomic.AtomicBoolean
import kotlin.test.fail
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import org.apache.commons.lang3.RandomStringUtils
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.TestInfo
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
) {
    // Connectors are calling System.getenv rather than using micronaut-y properties,
    // so we have to mock it out, instead of just setting more properties
    // inside NonDockerizedDestination.
    // This field has no effect on DockerizedDestination, which explicitly
    // sets env vars when invoking `docker run`.
    @SystemStub private lateinit var nonDockerMockEnvVars: EnvironmentVariables

    @BeforeEach
    fun setEnvVars() {
        nonDockerMockEnvVars.set("WORKER_JOB_ID", "0")
    }

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
    ) {
        val actualRecords: List<OutputRecord> = dataDumper.dumpRecords(config, stream)
        val expectedRecords: List<OutputRecord> =
            canonicalExpectedRecords.map { recordMangler.mapRecord(it) }

        RecordDiffer(
                primaryKey.map { nameMapper.mapFieldName(it) },
                cursor?.let { nameMapper.mapFieldName(it) },
            )
            .diffRecords(expectedRecords, actualRecords)
            ?.let(::fail)
    }

    /** Convenience wrapper for [runSync] using a single stream. */
    fun runSync(
        config: ConfigurationSpecification,
        stream: DestinationStream,
        messages: List<DestinationMessage>,
        streamStatus: AirbyteStreamStatus? = AirbyteStreamStatus.COMPLETE,
    ): List<AirbyteMessage> =
        runSync(config, DestinationCatalog(listOf(stream)), messages, streamStatus)

    /**
     * Run a sync with the given config+stream+messages, sending a trace message at the end of the
     * sync with the given stream status for every stream. [messages] should not include
     * [AirbyteStreamStatus] messages unless [streamStatus] is set to `null` (unless you actually
     * want to send multiple stream status messages).
     */
    fun runSync(
        config: ConfigurationSpecification,
        catalog: DestinationCatalog,
        messages: List<DestinationMessage>,
        streamStatus: AirbyteStreamStatus? = AirbyteStreamStatus.COMPLETE,
    ): List<AirbyteMessage> {
        val destination =
            destinationProcessFactory.createDestinationProcess(
                "write",
                config,
                catalog.asProtocolObject(),
            )
        return runBlocking {
            launch { destination.run() }
            messages.forEach { destination.sendMessage(it.asProtocolMessage()) }
            if (streamStatus != null) {
                catalog.streams.forEach {
                    destination.sendMessage(
                        AirbyteMessage()
                            .withType(AirbyteMessage.Type.TRACE)
                            .withTrace(
                                AirbyteTraceMessage()
                                    .withType(AirbyteTraceMessage.Type.STREAM_STATUS)
                                    .withEmittedAt(System.currentTimeMillis().toDouble())
                                    .withStreamStatus(
                                        AirbyteStreamStatusTraceMessage()
                                            .withStreamDescriptor(
                                                StreamDescriptor()
                                                    .withName(it.descriptor.name)
                                                    .withNamespace(it.descriptor.namespace),
                                            )
                                            .withStatus(streamStatus),
                                    ),
                            ),
                    )
                }
            }
            destination.shutdown()
            destination.readMessages()
        }
    }

    companion object {
        private val hasRunCleaner = AtomicBoolean(false)
    }
}
