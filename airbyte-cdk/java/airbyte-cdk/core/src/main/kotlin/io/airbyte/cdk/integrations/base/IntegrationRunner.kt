/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.annotations.VisibleForTesting
import com.google.common.base.Preconditions
import com.google.common.collect.Lists
import datadog.trace.api.Trace
import io.airbyte.cdk.core.util.ShutdownUtils
import io.airbyte.cdk.core.util.WriteStreamConsumer
import io.airbyte.cdk.integrations.util.ApmTraceUtils
import io.airbyte.cdk.integrations.util.ConnectorExceptionUtil
import io.airbyte.cdk.integrations.util.concurrent.ConcurrentStreamConsumer
import io.airbyte.commons.features.EnvVariableFeatureFlags
import io.airbyte.commons.features.FeatureFlags
import io.airbyte.commons.io.IOs
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.stream.AirbyteStreamStatusHolder
import io.airbyte.commons.stream.StreamStatusUtils
import io.airbyte.commons.util.AutoCloseableIterator
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.validation.json.JsonSchemaValidator
import java.io.*
import java.nio.file.Path
import java.util.*
import java.util.concurrent.*
import java.util.function.Consumer
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * Accepts EITHER a destination or a source. Routes commands from the commandline to the appropriate
 * methods on the integration. Keeps itself DRY for methods that are common between source and
 * destination.
 */
class IntegrationRunner
@VisibleForTesting
internal constructor(
    cliParser: IntegrationCliParser,
    outputRecordCollector: Consumer<AirbyteMessage>,
    destination: Destination?,
    source: Source?
) {
    private val cliParser: IntegrationCliParser
    private val outputRecordCollector: Consumer<AirbyteMessage>
    private val integration: Integration
    private val destination: Destination?
    private val source: Source?
    private val featureFlags: FeatureFlags
    private val shutdownUtils: ShutdownUtils

    constructor(
        destination: Destination?
    ) : this(
        IntegrationCliParser(),
        Consumer<AirbyteMessage> { message: AirbyteMessage ->
            Destination.defaultOutputRecordCollector(message)
        },
        destination,
        null
    )

    constructor(
        source: Source?
    ) : this(
        IntegrationCliParser(),
        Consumer<AirbyteMessage> { message: AirbyteMessage ->
            Destination.defaultOutputRecordCollector(message)
        },
        null,
        source
    )

    init {
        Preconditions.checkState(
            (destination != null) xor (source != null),
            "can only pass in a destination or a source"
        )
        this.cliParser = cliParser
        this.outputRecordCollector = outputRecordCollector
        // integration iface covers the commands that are the same for both source and destination.
        integration = source ?: destination!!
        this.source = source
        this.destination = destination
        this.featureFlags = EnvVariableFeatureFlags()
        this.shutdownUtils = ShutdownUtils()
        validator = JsonSchemaValidator()

        Thread.setDefaultUncaughtExceptionHandler(AirbyteExceptionHandler())
    }

    @VisibleForTesting
    internal constructor(
        cliParser: IntegrationCliParser,
        outputRecordCollector: Consumer<AirbyteMessage>,
        destination: Destination?,
        source: Source?,
        jsonSchemaValidator: JsonSchemaValidator
    ) : this(cliParser, outputRecordCollector, destination, source) {
        validator = jsonSchemaValidator
    }

    @Trace(operationName = "RUN_OPERATION")
    @Throws(Exception::class)
    fun run(args: Array<String>) {
        val parsed = cliParser.parse(args)
        try {
            runInternal(parsed)
        } catch (e: Exception) {
            throw e
        }
    }

    @Throws(Exception::class)
    private fun runInternal(parsed: IntegrationConfig?) {
        LOGGER.info("Running integration: {}", integration.javaClass.name)
        LOGGER.info("Command: {}", parsed!!.command)
        LOGGER.info("Integration config: {}", parsed)

        try {
            when (parsed.command) {
                Command.SPEC ->
                    outputRecordCollector.accept(
                        AirbyteMessage()
                            .withType(AirbyteMessage.Type.SPEC)
                            .withSpec(integration.spec())
                    )
                Command.CHECK -> {
                    val config = parseConfig(parsed.getConfigPath())
                    if (integration is Destination) {
                        DestinationConfig.Companion.initialize(config, integration.isV2Destination)
                    }
                    try {
                        validateConfig(integration.spec().connectionSpecification, config, "CHECK")
                    } catch (e: Exception) {
                        // if validation fails don't throw an exception, return a failed connection
                        // check message
                        outputRecordCollector.accept(
                            AirbyteMessage()
                                .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                                .withConnectionStatus(
                                    AirbyteConnectionStatus()
                                        .withStatus(AirbyteConnectionStatus.Status.FAILED)
                                        .withMessage(e.message)
                                )
                        )
                    }

                    outputRecordCollector.accept(
                        AirbyteMessage()
                            .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                            .withConnectionStatus(integration.check(config))
                    )
                }
                Command.DISCOVER -> {
                    val config = parseConfig(parsed.getConfigPath())
                    validateConfig(integration.spec().connectionSpecification, config, "DISCOVER")
                    outputRecordCollector.accept(
                        AirbyteMessage()
                            .withType(AirbyteMessage.Type.CATALOG)
                            .withCatalog(source!!.discover(config))
                    )
                }
                Command.READ -> {
                    val config = parseConfig(parsed.getConfigPath())
                    validateConfig(integration.spec().connectionSpecification, config, "READ")
                    val catalog =
                        parseConfig(parsed.getCatalogPath(), ConfiguredAirbyteCatalog::class.java)
                    val stateOptional =
                        parsed.getStatePath().map { path: Path? -> parseConfig(path) }
                    try {
                        if (featureFlags.concurrentSourceStreamRead()) {
                            LOGGER.info("Concurrent source stream read enabled.")
                            readConcurrent(config, catalog, stateOptional)
                        } else {
                            readSerial(config, catalog, stateOptional)
                        }
                    } finally {
                        if (source is AutoCloseable) {
                            (source as AutoCloseable).close()
                        }
                    }
                }
                Command.WRITE -> {
                    val config = parseConfig(parsed.getConfigPath())
                    validateConfig(integration.spec().connectionSpecification, config, "WRITE")
                    // save config to singleton
                    DestinationConfig.initialize(
                        config,
                        (integration as Destination).isV2Destination
                    )
                    val catalog =
                        parseConfig(parsed.getCatalogPath(), ConfiguredAirbyteCatalog::class.java)

                    try {
                        destination!!
                            .getSerializedMessageConsumer(config, catalog, outputRecordCollector)
                            ?.let {
                                it.use { consumer ->
                                    WriteStreamConsumer(consumer).consumeWriteStream()
                                }
                            }
                    } finally {
                        shutdownUtils.stopOrphanedThreads()
                    }
                }
            }
        } catch (e: Exception) {
            // Many of the exceptions thrown are nested inside layers of RuntimeExceptions. An
            // attempt is made
            // to
            // find the root exception that corresponds to a configuration error. If that does not
            // exist, we
            // just return the original exception.
            ApmTraceUtils.addExceptionToTrace(e)
            val rootThrowable = ConnectorExceptionUtil.getRootConfigError(e)
            val displayMessage = ConnectorExceptionUtil.getDisplayMessage(rootThrowable)
            // If the source connector throws a config error, a trace message with the relevant
            // message should
            // be surfaced.
            if (ConnectorExceptionUtil.isConfigError(rootThrowable)) {
                AirbyteTraceMessageUtility.emitConfigErrorTrace(e, displayMessage)
            }
            if (parsed.command == Command.CHECK) {
                // Currently, special handling is required for the CHECK case since the user display
                // information in
                // the trace message is
                // not properly surfaced to the FE. In the future, we can remove this and just throw
                // an exception.
                outputRecordCollector.accept(
                    AirbyteMessage()
                        .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                        .withConnectionStatus(
                            AirbyteConnectionStatus()
                                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                                .withMessage(displayMessage)
                        )
                )
                return
            }
            throw e
        }

        LOGGER.info("Completed integration: {}", integration.javaClass.name)
    }

    private fun produceMessages(
        messageIterator: AutoCloseableIterator<AirbyteMessage>,
        recordCollector: Consumer<AirbyteMessage>
    ) {
        messageIterator.airbyteStream.ifPresent { s: AirbyteStreamNameNamespacePair? ->
            LOGGER.debug("Producing messages for stream {}...", s)
        }
        messageIterator.forEachRemaining(recordCollector)
        messageIterator.airbyteStream.ifPresent { s: AirbyteStreamNameNamespacePair? ->
            LOGGER.debug("Finished producing messages for stream {}...", s)
        }
    }

    @Throws(Exception::class)
    private fun readConcurrent(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        stateOptional: Optional<JsonNode?>
    ) {
        val streams = source!!.readStreams(config, catalog, stateOptional.orElse(null))

        try {
            ConcurrentStreamConsumer(
                    { stream: AutoCloseableIterator<AirbyteMessage> ->
                        this.consumeFromStream(stream)
                    },
                    streams!!.size
                )
                .use { streamConsumer ->
                    /*
                     * Break the streams into partitions equal to the number of concurrent streams supported by the
                     * stream consumer.
                     */
                    val partitionSize = streamConsumer.parallelism
                    val partitions = Lists.partition(streams.stream().toList(), partitionSize)

                    // Submit each stream partition for concurrent execution
                    partitions.forEach(
                        Consumer { partition: List<AutoCloseableIterator<AirbyteMessage>> ->
                            streamConsumer.accept(partition)
                        }
                    )

                    // Check for any exceptions that were raised during the concurrent execution
                    if (streamConsumer.exception.isPresent) {
                        throw streamConsumer.exception.get()
                    }
                }
        } catch (e: Exception) {
            LOGGER.error("Unable to perform concurrent read.", e)
            throw e
        } finally {
            shutdownUtils.stopOrphanedThreads()
        }
    }

    @Throws(Exception::class)
    private fun readSerial(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        stateOptional: Optional<JsonNode?>
    ) {
        try {
            source!!.read(config, catalog, stateOptional.orElse(null)).use { messageIterator ->
                produceMessages(messageIterator, outputRecordCollector)
            }
        } finally {
            shutdownUtils.stopOrphanedThreads()
        }
    }

    private fun consumeFromStream(stream: AutoCloseableIterator<AirbyteMessage>) {
        try {
            val streamStatusTrackingRecordConsumer =
                StreamStatusUtils.statusTrackingRecordCollector(
                    stream,
                    outputRecordCollector,
                    Optional.of(
                        Consumer { obj: AirbyteStreamStatusHolder ->
                            AirbyteTraceMessageUtility.emitStreamStatusTrace(obj)
                        }
                    )
                )
            produceMessages(stream, streamStatusTrackingRecordConsumer)
        } catch (e: Exception) {
            stream.airbyteStream.ifPresent { s: AirbyteStreamNameNamespacePair? ->
                LOGGER.error("Failed to consume from stream {}.", s, e)
            }
            throw RuntimeException(e)
        }
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(IntegrationRunner::class.java)

        private lateinit var validator: JsonSchemaValidator

        @Throws(Exception::class)
        private fun validateConfig(
            schemaJson: JsonNode,
            objectJson: JsonNode,
            operationType: String
        ) {
            val validationResult = validator.validate(schemaJson, objectJson)
            if (validationResult.isNotEmpty()) {
                throw Exception(
                    String.format(
                        "Verification error(s) occurred for %s. Errors: %s ",
                        operationType,
                        validationResult
                    )
                )
            }
        }

        fun parseConfig(path: Path?): JsonNode {
            return Jsons.deserialize(IOs.readFile(path))
        }

        private fun <T> parseConfig(path: Path?, klass: Class<T>): T {
            val jsonNode = parseConfig(path)
            return Jsons.`object`(jsonNode, klass)
        }

        /** @param connectorImage Expected format: [organization/]image[:version] */
        @VisibleForTesting
        fun parseConnectorVersion(connectorImage: String?): String {
            if (connectorImage == null || connectorImage == "") {
                return "unknown"
            }

            val tokens =
                connectorImage.split(":".toRegex()).dropLastWhile { it.isEmpty() }.toTypedArray()
            return tokens[tokens.size - 1]
        }
    }
}
