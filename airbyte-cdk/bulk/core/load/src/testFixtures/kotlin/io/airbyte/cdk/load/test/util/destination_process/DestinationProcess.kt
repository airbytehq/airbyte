/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util.destination_process

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.Property
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.config.NamespaceDefinitionType
import io.airbyte.cdk.load.config.NamespaceMappingConfig
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import io.airbyte.cdk.load.message.InputMessage
import io.airbyte.cdk.load.message.InputStreamComplete
import io.airbyte.cdk.load.test.util.IntegrationTest
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.micronaut.context.env.yaml.YamlPropertySourceLoader
import java.nio.file.Files
import java.nio.file.Path
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking

/**
 * Represents a destination process, whether running in-JVM via micronaut, or as a separate Docker
 * container. The general lifecycle is:
 * 1. `val dest = DestinationProcessFactory.createDestinationProcess(...)`
 * 2. `launch { dest.run() }`
 * 3. [sendMessage] as many times as you want
 * 4. [readMessages] as needed (e.g. to check that state messages are emitted during the sync)
 * 5. [shutdown] once you have no more messages to send to the destination
 */
interface DestinationProcess {
    val dataChannelMedium: DataChannelMedium

    /**
     * Run the destination process. Callers who want to interact with the destination should
     * `launch` this method.
     */
    suspend fun run()

    /**
     * Sending raw strings is not recommended now that we're using multiple serialization formats,
     * unless you're trying to send a poison pill.
     */
    suspend fun sendMessage(string: String)
    suspend fun sendMessage(message: InputMessage, broadcast: Boolean = false)
    suspend fun sendMessages(vararg messages: InputMessage) {
        messages.forEach { sendMessage(it) }
    }

    /** Return all messages the destination emitted since the last call to [readMessages]. */
    fun readMessages(): List<AirbyteMessage>

    /**
     * Signal the destination to exit (i.e. close its stdin stream), then wait for it to terminate.
     */
    suspend fun shutdown()

    /** Terminate the destination as immediately as possible. */
    suspend fun kill()

    fun verifyFileDeleted()
}

@SuppressFBWarnings("NP_NONNULL_RETURN_VIOLATION", "good old lateinit")
abstract class DestinationProcessFactory {
    /**
     * Ideally we'd take this in the constructor, but that's annoying because of how junit injects
     * TestInfo, and how Micronaut injects everything else. Instead, we'll rely on [IntegrationTest]
     * to set this in a BeforeEach function.
     */
    lateinit var testName: String

    /**
     * If [useFileTransfer] is enabled, the process should create a file for the connector to
     * transfer.
     */
    abstract fun createDestinationProcess(
        command: String,
        configContents: String? = null,
        catalog: ConfiguredAirbyteCatalog? = null,
        useFileTransfer: Boolean = false,
        micronautProperties: Map<Property, String> = emptyMap(),
        dataChannelMedium: DataChannelMedium = DataChannelMedium.STDIO,
        dataChannelFormat: DataChannelFormat = DataChannelFormat.JSONL,
        namespaceMappingConfig: NamespaceMappingConfig =
            NamespaceMappingConfig(NamespaceDefinitionType.SOURCE),
        vararg featureFlags: FeatureFlag,
    ): DestinationProcess

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
        testPrettyName: String,
        dataChannelMedium: DataChannelMedium,
        dataChannelFormat: DataChannelFormat,
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
        namespaceMappingConfig: NamespaceMappingConfig? = null,
        micronautProperties: Map<Property, String> = emptyMap(),
    ): List<AirbyteMessage> {
        check(streamStatus == null || streamStatus == AirbyteStreamStatus.COMPLETE) {
            "Invalid stream status: $streamStatus"
        }
        testName = testPrettyName

        val destination =
            createDestinationProcess(
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

    companion object {
        /**
         * [additionalMicronautEnvs] is only passed into the non-docker connector. We assume that
         * the dockerized connector is capable of setting its own micronaut environments.
         */
        fun get(additionalMicronautEnvs: List<String>): DestinationProcessFactory =
            when (val runner = System.getenv("AIRBYTE_CONNECTOR_INTEGRATION_TEST_RUNNER")) {
                null,
                "non-docker" -> NonDockerizedDestinationFactory(additionalMicronautEnvs)
                "docker" -> {
                    val rawProperties: Map<String, Any?> =
                        YamlPropertySourceLoader()
                            .read(
                                "irrelevant",
                                Files.readAllBytes(Path.of("metadata.yaml")),
                            )
                    DockerizedDestinationFactory(
                        rawProperties["data.dockerRepository"] as String,
                        "dev"
                    )
                }
                else ->
                    throw IllegalArgumentException(
                        "Unknown AIRBYTE_CONNECTOR_INTEGRATION_TEST_RUNNER environment variable: $runner"
                    )
            }
    }
}
