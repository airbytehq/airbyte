/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util.destination_process

import io.airbyte.cdk.ConnectorUncleanExitException
import io.airbyte.cdk.command.CliRunnable
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.Property
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.io.PipedInputStream
import java.io.PipedOutputStream
import java.io.PrintWriter
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.util.concurrent.Executors
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.asCoroutineDispatcher
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import org.apache.commons.lang3.RandomStringUtils
import org.junit.jupiter.api.Assertions.assertFalse

private val logger = KotlinLogging.logger {}

class NonDockerizedDestination(
    command: String,
    configContents: String?,
    catalog: ConfiguredAirbyteCatalog?,
    useFileTransfer: Boolean,
    additionalMicronautEnvs: List<String>,
    micronautProperties: Map<Property, String>,
    vararg featureFlags: FeatureFlag,
) : DestinationProcess {
    private val destinationStdinPipe: PrintWriter
    private val destination: CliRunnable
    private val destinationComplete = CompletableDeferred<Unit>()
    // The destination has a runBlocking inside WriteOperation.
    // This means that normal coroutine cancellation doesn't work.
    // So we start our own thread pool, which we can forcibly kill if needed.
    private val executor = Executors.newSingleThreadExecutor()
    private val coroutineDispatcher = executor.asCoroutineDispatcher()
    private val file = File("/tmp/test_file")

    init {
        if (useFileTransfer) {
            val fileContentStr = "123"
            file.writeText(fileContentStr)
        }
        val destinationStdin = PipedInputStream()
        // This could probably be a channel, somehow. But given the current structure,
        // it's easier to just use the pipe stuff.
        destinationStdinPipe =
            // spotbugs requires explicitly specifying the charset,
            // so we also have to specify autoFlush=false (i.e. the default behavior
            // from PrintWriter(outputStream) ).
            // Thanks, spotbugs.
            PrintWriter(PipedOutputStream(destinationStdin), false, Charsets.UTF_8)
        destination =
            CliRunner.destination(
                command,
                configContents = configContents,
                catalog = catalog,
                inputStream = destinationStdin,
                featureFlags = featureFlags,
                additionalMicronautEnvs = additionalMicronautEnvs,
                micronautProperties = micronautProperties.mapKeys { (k, _) -> k.micronautProperty },
            )
    }

    override suspend fun run() {
        withContext(coroutineDispatcher) {
                launch {
                    try {
                        destination.run()
                    } catch (e: ConnectorUncleanExitException) {
                        throw DestinationUncleanExitException.of(
                            e.exitCode,
                            destination.results.traces(),
                            destination.results.states(),
                        )
                    }
                    destinationComplete.complete(Unit)
                }
            }
            .invokeOnCompletion { executor.shutdownNow() }
    }

    override fun sendMessage(message: AirbyteMessage) {
        destinationStdinPipe.println(message.serializeToString())
    }

    override fun sendMessage(string: String) {
        destinationStdinPipe.println(string)
    }

    override fun readMessages(): List<AirbyteMessage> = destination.results.newMessages()

    override suspend fun shutdown() {
        destinationStdinPipe.close()
        destinationComplete.join()
    }

    override fun kill() {
        // In addition to preventing the executor from accepting new tasks,
        // this also sends a Thread.interrupt() to running tasks.
        // Coroutines interpret this as a cancellation.
        executor.shutdownNow()
    }

    override fun verifyFileDeleted() {
        assertFalse(file.exists())
    }
}

class NonDockerizedDestinationFactory(
    private val additionalMicronautEnvs: List<String>,
) : DestinationProcessFactory() {
    override fun createDestinationProcess(
        command: String,
        configContents: String?,
        catalog: ConfiguredAirbyteCatalog?,
        useFileTransfer: Boolean,
        micronautProperties: Map<Property, String>,
        vararg featureFlags: FeatureFlag,
    ): DestinationProcess {
        // TODO pass test name into the destination process
        return NonDockerizedDestination(
            command,
            configContents,
            catalog,
            useFileTransfer,
            additionalMicronautEnvs,
            micronautProperties,
            *featureFlags
        )
    }
}

// TODO if this is actually what we do - need to move NonDockerDest to src/main
// TODO the cleaner maybe should also be looking for old streams??
fun interface CheckCleanerUpper<C : DestinationConfiguration> {
    fun cleanup(config: C, stream: DestinationStream)
}

class GenericChecker<C : DestinationConfiguration>(
    private val cleanerUpper: CheckCleanerUpper<C>,
) : DestinationChecker<C> {
    override fun check(config: C) {
        // generate a string like "20240523"
        val date = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"))
        // generate 5 random characters
        val random = RandomStringUtils.insecure().nextAlphabetic(5).lowercase()
        val mockStream =
            DestinationStream(
                descriptor = DestinationStream.Descriptor("airbyte_test", "test$date$random"),
                importType = Append,
                schema = ObjectType(linkedMapOf("test" to FieldType(IntegerType, nullable = true))),
                generationId = 1,
                minimumGenerationId = 0,
                syncId = 1,
            )
        try {
            val destination =
                NonDockerizedDestination(
                    command = "check",
                    configContents = config.serializeToString(),
                    catalog =
                        ConfiguredAirbyteCatalog()
                            .withStreams(listOf(mockStream.asProtocolObject())),
                    useFileTransfer = false,
                    // TODO pass these in
                    additionalMicronautEnvs = emptyList(),
                    micronautProperties = emptyMap(),
                )
            destination.sendMessages(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withEmittedAt(System.currentTimeMillis())
                            .withStream(mockStream.descriptor.name)
                            .withNamespace(mockStream.descriptor.namespace)
                            .withData("""{"test": 42}""".deserializeToNode())
                    ),
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
                                            .withName(mockStream.descriptor.name)
                                            .withNamespace(mockStream.descriptor.namespace)
                                    )
                                    .withStatus(
                                        AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE
                                    )
                            )
                    )
            )
            runBlocking { destination.shutdown() }
        } finally {
            cleanerUpper.cleanup(config, mockStream)
        }
    }
}
