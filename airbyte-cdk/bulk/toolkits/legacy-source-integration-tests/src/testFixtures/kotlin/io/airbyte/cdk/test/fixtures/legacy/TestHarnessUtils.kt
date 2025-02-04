package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.protocol.models.*
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.BufferedReader
import java.io.IOException
import java.io.InputStream
import java.io.InputStreamReader
import java.nio.charset.StandardCharsets
import java.time.Duration
import java.time.temporal.ChronoUnit
import java.util.*
import java.util.concurrent.TimeUnit
import java.util.stream.Collectors

private val LOGGER = KotlinLogging.logger {}
// TODO:(Issue-4824): Figure out how to log Docker process information.
object TestHarnessUtils {

    fun gentleClose(process: Process?, timeout: Long, timeUnit: TimeUnit?) {
        if (process == null) {
            return
        }

        if (process.info() != null) {
            process.info().commandLine().ifPresent { commandLine: String ->
                LOGGER.debug { "Gently closing process $commandLine" }
            }
        }

        try {
            if (process.isAlive) {
                process.waitFor(timeout, timeUnit)
            }
        } catch (e: InterruptedException) {
            LOGGER.error(e) { "Exception while while waiting for process to finish" }
        }

        if (process.isAlive) {
            closeProcess(process, Duration.of(1, ChronoUnit.MINUTES))
        }
    }

    fun closeProcess(process: Process?, lastChanceDuration: Duration) {
        if (process == null) {
            return
        }
        try {
            process.destroy()
            process.waitFor(lastChanceDuration.toMillis(), TimeUnit.MILLISECONDS)
            if (process.isAlive) {
                LOGGER.warn {
                    "Process is still alive after calling destroy. Attempting to destroy forcibly..."
                }
                process.destroyForcibly()
            }
        } catch (e: InterruptedException) {
            LOGGER.error(e) { "Exception when closing process." }
        }
    }

    fun wait(process: Process) {
        try {
            process.waitFor()
        } catch (e: InterruptedException) {
            LOGGER.error(e) { "Exception while while waiting for process to finish" }
        }
    }

    fun cancelProcess(process: Process?) {
        closeProcess(process, Duration.of(10, ChronoUnit.SECONDS))
    }

    /**
     * Translates a StandardSyncInput into a WorkerSourceConfig. WorkerSourceConfig is a subset of
     * StandardSyncInput.
     */
    fun syncToWorkerSourceConfig(sync: StandardSyncInput): WorkerSourceConfig {
        return WorkerSourceConfig()
            .withSourceId(sync.sourceId)
            .withSourceConnectionConfiguration(sync.sourceConfiguration)
            .withCatalog(sync.catalog)
            .withState(sync.state)
    }

    /**
     * Translates a StandardSyncInput into a WorkerDestinationConfig. WorkerDestinationConfig is a
     * subset of StandardSyncInput.
     */
    fun syncToWorkerDestinationConfig(sync: StandardSyncInput): WorkerDestinationConfig {
        return WorkerDestinationConfig()
            .withDestinationId(sync.destinationId)
            .withDestinationConnectionConfiguration(sync.destinationConfiguration)
            .withCatalog(sync.catalog)
            .withState(sync.state)
    }

    private fun getConnectorCommandFromOutputType(
        outputType: ConnectorJobOutput.OutputType
    ): FailureHelper.ConnectorCommand {
        return when (outputType) {
            ConnectorJobOutput.OutputType.SPEC -> FailureHelper.ConnectorCommand.SPEC
            ConnectorJobOutput.OutputType.CHECK_CONNECTION -> FailureHelper.ConnectorCommand.CHECK
            ConnectorJobOutput.OutputType.DISCOVER_CATALOG_ID ->
                FailureHelper.ConnectorCommand.DISCOVER
        }
    }

    fun getMostRecentConfigControlMessage(
        messagesByType: Map<AirbyteMessage.Type, List<AirbyteMessage>>
    ): Optional<AirbyteControlConnectorConfigMessage> {
        return Optional.ofNullable(
            messagesByType
                .getOrDefault(AirbyteMessage.Type.CONTROL, ArrayList())
                .map { obj: AirbyteMessage -> obj.control }
                .filter { control: AirbyteControlMessage ->
                    control.type == AirbyteControlMessage.Type.CONNECTOR_CONFIG
                }
                .map { obj: AirbyteControlMessage -> obj.connectorConfig }
                .lastOrNull()
        )
    }

    private fun getTraceMessageFromMessagesByType(
        messagesByType: Map<AirbyteMessage.Type, List<AirbyteMessage>>
    ): AirbyteTraceMessage? {
        return messagesByType
            .getOrDefault(AirbyteMessage.Type.TRACE, ArrayList())
            .map { obj: AirbyteMessage -> obj.trace }
            .filter { trace: AirbyteTraceMessage -> trace.type == AirbyteTraceMessage.Type.ERROR }
            .firstOrNull()
    }

    fun getDidControlMessageChangeConfig(
        initialConfigJson: JsonNode,
        configMessage: AirbyteControlConnectorConfigMessage
    ): Boolean {
        val newConfig = configMessage.config
        val newConfigJson = Jsons.jsonNode(newConfig)
        return initialConfigJson != newConfigJson
    }

    @Throws(IOException::class)
    fun getMessagesByType(
        process: Process,
        streamFactory: AirbyteStreamFactory,
        timeOut: Int
    ): Map<AirbyteMessage.Type, List<AirbyteMessage>> {
        val messagesByType: Map<AirbyteMessage.Type, List<AirbyteMessage>>
        process.inputStream.use { stdout ->
            messagesByType =
                streamFactory
                    .create(IOs.newBufferedReader(stdout))
                    .collect(Collectors.groupingBy { obj: AirbyteMessage -> obj.type })
            gentleClose(process, timeOut.toLong(), TimeUnit.MINUTES)
            return messagesByType
        }
    }

    fun getJobFailureReasonFromMessages(
        outputType: ConnectorJobOutput.OutputType,
        messagesByType: Map<AirbyteMessage.Type, List<AirbyteMessage>>
    ): Optional<FailureReason> {
        val traceMessage = getTraceMessageFromMessagesByType(messagesByType)
        if (traceMessage != null) {
            val connectorCommand = getConnectorCommandFromOutputType(outputType)
            return Optional.of(
                FailureHelper.connectorCommandFailure(traceMessage, null, null, connectorCommand)
            )
        } else {
            return Optional.empty()
        }
    }

    fun mapStreamNamesToSchemas(
        syncInput: StandardSyncInput
    ): Map<AirbyteStreamNameNamespacePair, JsonNode> {
        return syncInput.catalog!!.streams.associate {
            AirbyteStreamNameNamespacePair.fromAirbyteStream(it.stream) to it.stream.jsonSchema
        }
    }

    @Throws(IOException::class)
    fun getStdErrFromErrorStream(errorStream: InputStream): String {
        val reader = BufferedReader(InputStreamReader(errorStream, StandardCharsets.UTF_8))
        val errorOutput = StringBuilder()
        var line: String?
        while ((reader.readLine().also { line = it }) != null) {
            errorOutput.append(line)
            errorOutput.append(System.lineSeparator())
        }
        return errorOutput.toString()
    }

    @Throws(TestHarnessException::class, IOException::class)
    fun throwWorkerException(errorMessage: String, process: Process) {
        val stderr = getStdErrFromErrorStream(process.errorStream)
        if (stderr.isEmpty()) {
            throw TestHarnessException(errorMessage)
        } else {
            throw TestHarnessException("$errorMessage: \n$stderr")
        }
    }
}
