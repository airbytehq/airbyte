/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.staging

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.base.Preconditions
import io.airbyte.cdk.core.command.option.ConnectorConfiguration
import io.airbyte.cdk.core.command.option.DefaultConnectorConfiguration
import io.airbyte.cdk.core.command.option.DefaultMicronautConfiguredAirbyteCatalog
import io.airbyte.cdk.core.command.option.MicronautConfiguredAirbyteCatalog
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.async.AirbyteFileUtils
import io.airbyte.cdk.integrations.destination.async.AsyncStreamConsumer
import io.airbyte.cdk.integrations.destination.async.DetectStreamToFlush
import io.airbyte.cdk.integrations.destination.async.FlushWorkers
import io.airbyte.cdk.integrations.destination.async.GlobalMemoryManager
import io.airbyte.cdk.integrations.destination.async.RunningFlushWorkers
import io.airbyte.cdk.integrations.destination.async.StreamDescriptorUtils
import io.airbyte.cdk.integrations.destination.async.buffers.AsyncBuffers
import io.airbyte.cdk.integrations.destination.async.buffers.BufferDequeue
import io.airbyte.cdk.integrations.destination.async.buffers.BufferEnqueue
import io.airbyte.cdk.integrations.destination.async.buffers.BufferMemory
import io.airbyte.cdk.integrations.destination.async.deser.DeserializationUtil
import io.airbyte.cdk.integrations.destination.async.deser.StreamAwareDataTransformer
import io.airbyte.cdk.integrations.destination.async.state.FlushFailure
import io.airbyte.cdk.integrations.destination.async.state.GlobalAsyncStateManager
import io.airbyte.cdk.integrations.destination.jdbc.WriteConfig
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog
import io.airbyte.integrations.base.destination.typing_deduping.TypeAndDedupeOperationValve
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper
import io.airbyte.protocol.models.v0.*
import io.micronaut.scheduling.ScheduledExecutorTaskScheduler
import io.micronaut.scheduling.instrument.InstrumentedExecutorService
import java.time.Instant
import java.util.*
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.function.Consumer
import java.util.function.Function
import java.util.stream.Collectors
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * Uses both Factory and Consumer design pattern to create a single point of creation for consuming
 * [AirbyteMessage] for processing
 */
class StagingConsumerFactory(
    private val outputRecordCollector: Consumer<AirbyteMessage>,
    private val database: JdbcDatabase,
    private val stagingOperations: StagingOperations,
    private val namingResolver: NamingConventionTransformer,
    private val config: JsonNode,
    private val catalog: ConfiguredAirbyteCatalog,
    private val purgeStagingData: Boolean,
    private val typerDeduperValve: TypeAndDedupeOperationValve,
    private val typerDeduper: TyperDeduper,
    private val parsedCatalog: ParsedCatalog,
    private val defaultNamespace: String?,
    private val useDestinationsV2Columns: Boolean = false,
    // Optional fields
    private val bufferMemoryLimit: Optional<Long> = Optional.empty<Long>(),
    private val optimalBatchSizeBytes: Long = (50 * 1024 * 1024).toLong(),
    private val dataTransformer: StreamAwareDataTransformer
) : SerialStagingConsumerFactory() {

    fun createAsync(): SerializedAirbyteMessageConsumer {
        val writeConfigs =
            SerialStagingConsumerFactory.createWriteConfigs(
                namingResolver,
                config,
                catalog,
                parsedCatalog,
                useDestinationsV2Columns,
            )
        val streamDescToWriteConfig: Map<StreamDescriptor, WriteConfig> =
            streamDescToWriteConfig(writeConfigs)
        val flusher =
            AsyncFlush(
                streamDescToWriteConfig,
                stagingOperations,
                database,
                catalog,
                typerDeduperValve,
                typerDeduper,
                optimalBatchSizeBytes,
                useDestinationsV2Columns,
            )

        val asyncBuffers = AsyncBuffers()
        val bufferMemory: BufferMemory =
            object : BufferMemory() {
                override fun getMemoryLimit(): Long {
                    return getMemoryLimit(bufferMemoryLimit)
                }
            }
        val memoryManager = GlobalMemoryManager(bufferMemory)
        val stateManager = GlobalAsyncStateManager(memoryManager)
        val bufferEnqueue = BufferEnqueue(memoryManager, stateManager, asyncBuffers)
        val bufferDequeue = BufferDequeue(memoryManager, stateManager, asyncBuffers)
        val runningFlushWorkers = RunningFlushWorkers()
        val airbyteFileUtils = AirbyteFileUtils()
        val detectStreamToFlush =
            DetectStreamToFlush(
                bufferDequeue,
                runningFlushWorkers,
                flusher,
                airbyteFileUtils,
                Optional.empty(),
            )
        val workerPool: ExecutorService = InstrumentedExecutorService {
            Executors.newFixedThreadPool(5)
        }
        val flushFailure = FlushFailure()
        val flushWorkers =
            FlushWorkers(
                stateManager,
                bufferDequeue,
                flusher,
                outputRecordCollector,
                workerPool,
                ScheduledExecutorTaskScheduler(Executors.newScheduledThreadPool(2)),
                detectStreamToFlush,
                runningFlushWorkers,
                flushFailure,
                airbyteFileUtils,
            )
        val micronautConfiguredAirbyteCatalog = DefaultMicronautConfiguredAirbyteCatalog(catalog!!)
        val configuration: ConnectorConfiguration = DefaultConnectorConfiguration(defaultNamespace)

        return AsyncStreamConsumer(
            GeneralStagingFunctions.onStartFunction(
                database,
                stagingOperations,
                writeConfigs,
                typerDeduper,
            ), // todo (cgardens) - wrapping the old close function to avoid more code churn.
            { _: Boolean?, streamSyncSummaries: Map<StreamDescriptor, StreamSyncSummary> ->
                try {
                    GeneralStagingFunctions.onCloseFunction(
                            database,
                            stagingOperations,
                            writeConfigs,
                            purgeStagingData,
                            typerDeduper,
                        )
                        .accept(false, streamSyncSummaries)
                } catch (e: Exception) {
                    throw RuntimeException(e)
                }
            },
            configuration,
            micronautConfiguredAirbyteCatalog,
            bufferEnqueue,
            flushWorkers,
            flushFailure,
            dataTransformer,
            DeserializationUtil(),
            StreamDescriptorUtils(),
        )
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(StagingConsumerFactory::class.java)

        private val SYNC_DATETIME: Instant = Instant.now()

        private fun getMemoryLimit(bufferMemoryLimit: Optional<Long>): Long {
            return bufferMemoryLimit.orElse(
                (Runtime.getRuntime().maxMemory() * BufferMemory.MEMORY_LIMIT_RATIO).toLong(),
            )
        }

        private fun streamDescToWriteConfig(
            writeConfigs: List<WriteConfig>
        ): Map<StreamDescriptor, WriteConfig> {
            val conflictingStreams: MutableSet<WriteConfig> = HashSet()
            val streamDescToWriteConfig: MutableMap<StreamDescriptor, WriteConfig> =
                HashMap<StreamDescriptor, WriteConfig>()
            for (config in writeConfigs) {
                val streamIdentifier = toStreamDescriptor(config)
                if (streamDescToWriteConfig.containsKey(streamIdentifier)) {
                    conflictingStreams.add(config)
                    val existingConfig: WriteConfig =
                        streamDescToWriteConfig.getValue(streamIdentifier)
                    // The first conflicting stream won't have any problems, so we need to
                    // explicitly add it here.
                    conflictingStreams.add(existingConfig)
                } else {
                    streamDescToWriteConfig[streamIdentifier] = config
                }
            }
            if (conflictingStreams.isNotEmpty()) {
                val message =
                    String.format(
                        "You are trying to write multiple streams to the same table. Consider switching to a custom namespace format using \${SOURCE_NAMESPACE}, or moving one of them into a separate connection with a different stream prefix. Affected streams: %s",
                        conflictingStreams
                            .stream()
                            .map { config: WriteConfig ->
                                "${config.namespace}.${config.streamName}"
                            }
                            .collect(Collectors.joining(", ")),
                    )
                throw ConfigErrorException(message)
            }
            return streamDescToWriteConfig
        }

        private fun toStreamDescriptor(config: WriteConfig): StreamDescriptor {
            return StreamDescriptor().withName(config.streamName).withNamespace(config.namespace)
        }

        /**
         * Creates a list of all [WriteConfig] for each stream within a [ConfiguredAirbyteCatalog].
         * Each write config represents the configuration settings for writing to a destination
         * connector
         *
         * @param namingResolver [NamingConventionTransformer] used to transform names that are
         * acceptable by each destination connector
         * @param config destination connector configuration parameters
         * @param catalog [ConfiguredAirbyteCatalog] collection of configured
         * [ConfiguredAirbyteStream]
         * @return list of all write configs for each stream in a [ConfiguredAirbyteCatalog]
         */
        private fun createWriteConfigs(
            namingResolver: NamingConventionTransformer?,
            config: JsonNode?,
            catalog: ConfiguredAirbyteCatalog?,
            parsedCatalog: ParsedCatalog?,
            useDestinationsV2Columns: Boolean
        ): List<WriteConfig> {
            return catalog!!
                .streams
                .stream()
                .map(toWriteConfig(namingResolver, config, parsedCatalog, useDestinationsV2Columns))
                .toList()
        }

        private fun toWriteConfig(
            namingResolver: NamingConventionTransformer?,
            config: JsonNode?,
            parsedCatalog: ParsedCatalog?,
            useDestinationsV2Columns: Boolean
        ): Function<ConfiguredAirbyteStream, WriteConfig> {
            return Function<ConfiguredAirbyteStream, WriteConfig> { stream: ConfiguredAirbyteStream
                ->
                Preconditions.checkNotNull(
                    stream.destinationSyncMode,
                    "Undefined destination sync mode",
                )
                val abStream = stream.stream
                val streamName = abStream.name

                val outputSchema: String
                val tableName: String
                if (useDestinationsV2Columns) {
                    val streamId = parsedCatalog!!.getStream(abStream.namespace, streamName).id
                    outputSchema = streamId.rawNamespace!!
                    tableName = streamId.rawName!!
                } else {
                    outputSchema =
                        getOutputSchema(abStream, config!!["schema"].asText(), namingResolver)
                    tableName = namingResolver!!.getRawTableName(streamName)
                }
                val tmpTableName = namingResolver!!.getTmpTableName(streamName)
                val syncMode = stream.destinationSyncMode

                val writeConfig =
                    WriteConfig(
                        streamName,
                        abStream.namespace,
                        outputSchema,
                        tmpTableName,
                        tableName,
                        syncMode,
                        SYNC_DATETIME,
                    )
                LOGGER.info("Write config: {}", writeConfig)
                writeConfig
            }
        }

        private fun getOutputSchema(
            stream: AirbyteStream,
            defaultDestSchema: String,
            namingResolver: NamingConventionTransformer?
        ): String {
            return if (stream.namespace != null) namingResolver!!.getNamespace(stream.namespace)
            else namingResolver!!.getNamespace(defaultDestSchema)
        }
    }
}
