/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.staging

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.base.Preconditions
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.async.AsyncStreamConsumer
import io.airbyte.cdk.integrations.destination.async.buffers.BufferManager
import io.airbyte.cdk.integrations.destination.async.deser.AirbyteMessageDeserializer
import io.airbyte.cdk.integrations.destination.async.deser.IdentityDataTransformer
import io.airbyte.cdk.integrations.destination.async.deser.StreamAwareDataTransformer
import io.airbyte.cdk.integrations.destination.async.state.FlushFailure
import io.airbyte.cdk.integrations.destination.jdbc.WriteConfig
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper
import io.airbyte.protocol.models.v0.*
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import java.util.Optional
import java.util.concurrent.Executors
import java.util.function.Consumer
import java.util.function.Function

private val LOGGER = KotlinLogging.logger {}
/**
 * Uses both Factory and Consumer design pattern to create a single point of creation for consuming
 * [AirbyteMessage] for processing
 */
class StagingConsumerFactory
private constructor(
    private val outputRecordCollector: Consumer<AirbyteMessage>?,
    private val database: JdbcDatabase?,
    private val stagingOperations: StagingOperations?,
    private val namingResolver: NamingConventionTransformer?,
    private val config: JsonNode?,
    private val catalog: ConfiguredAirbyteCatalog?,
    private val purgeStagingData: Boolean,
    private val typerDeduper: TyperDeduper?,
    private val parsedCatalog: ParsedCatalog?,
    private val defaultNamespace: String?,
    private val destinationColumns: JavaBaseConstants.DestinationColumns,
    // Optional fields
    private val bufferMemoryLimit: Optional<Long>,
    private val optimalBatchSizeBytes: Long,
    private val dataTransformer: StreamAwareDataTransformer
) : SerialStagingConsumerFactory() {
    class Builder {
        // Required (?) fields
        // (TODO which of these are _actually_ required, and which have we just coincidentally
        // always
        // provided?)
        var outputRecordCollector: Consumer<AirbyteMessage>? = null
        var database: JdbcDatabase? = null
        var stagingOperations: StagingOperations? = null
        var namingResolver: NamingConventionTransformer? = null
        var config: JsonNode? = null
        var catalog: ConfiguredAirbyteCatalog? = null
        var purgeStagingData: Boolean = false
        var typerDeduper: TyperDeduper? = null
        var parsedCatalog: ParsedCatalog? = null
        var defaultNamespace: String? = null
        var destinationColumns: JavaBaseConstants.DestinationColumns =
            JavaBaseConstants.DestinationColumns.LEGACY

        // Optional fields
        private var bufferMemoryLimit = Optional.empty<Long>()
        private var optimalBatchSizeBytes = (50 * 1024 * 1024).toLong()

        private var dataTransformer: StreamAwareDataTransformer? = null

        fun setBufferMemoryLimit(bufferMemoryLimit: Optional<Long>): Builder {
            this.bufferMemoryLimit = bufferMemoryLimit
            return this
        }

        fun setOptimalBatchSizeBytes(optimalBatchSizeBytes: Long): Builder {
            this.optimalBatchSizeBytes = optimalBatchSizeBytes
            return this
        }

        fun setDataTransformer(dataTransformer: StreamAwareDataTransformer?): Builder {
            this.dataTransformer = dataTransformer
            return this
        }

        fun build(): StagingConsumerFactory {
            return StagingConsumerFactory(
                outputRecordCollector,
                database,
                stagingOperations,
                namingResolver,
                config,
                catalog,
                purgeStagingData,
                typerDeduper,
                parsedCatalog,
                defaultNamespace,
                destinationColumns,
                bufferMemoryLimit,
                optimalBatchSizeBytes,
                (if (dataTransformer != null) dataTransformer else IdentityDataTransformer())!!
            )
        }
    }

    fun createAsync(): SerializedAirbyteMessageConsumer {
        val typerDeduper = this.typerDeduper!!
        val stagingOperations = this.stagingOperations!!

        val writeConfigs: List<WriteConfig> =
            createWriteConfigs(namingResolver, config, catalog, parsedCatalog, destinationColumns)
        val streamDescToWriteConfig: Map<StreamDescriptor, WriteConfig> =
            streamDescToWriteConfig(writeConfigs)
        val flusher =
            AsyncFlush(
                streamDescToWriteConfig,
                stagingOperations,
                database,
                catalog,
                optimalBatchSizeBytes,
                destinationColumns
            )
        return AsyncStreamConsumer(
            outputRecordCollector!!,
            GeneralStagingFunctions.onStartFunction(
                database!!,
                stagingOperations,
                writeConfigs,
                typerDeduper
            ),
            GeneralStagingFunctions.onCloseFunction(
                database,
                stagingOperations,
                writeConfigs,
                purgeStagingData,
                typerDeduper
            ),
            flusher,
            catalog!!,
            BufferManager(getMemoryLimit(bufferMemoryLimit)),
            Optional.ofNullable(defaultNamespace),
            FlushFailure(),
            Executors.newFixedThreadPool(5),
            AirbyteMessageDeserializer(dataTransformer),
        )
    }

    companion object {

        private val SYNC_DATETIME: Instant = Instant.now()

        @JvmStatic
        fun builder(
            outputRecordCollector: Consumer<AirbyteMessage>,
            database: JdbcDatabase?,
            stagingOperations: StagingOperations,
            namingResolver: NamingConventionTransformer?,
            config: JsonNode?,
            catalog: ConfiguredAirbyteCatalog,
            purgeStagingData: Boolean,
            typerDeduper: TyperDeduper,
            parsedCatalog: ParsedCatalog?,
            defaultNamespace: String?,
            destinationColumns: JavaBaseConstants.DestinationColumns
        ): Builder {
            val builder = Builder()
            builder.outputRecordCollector = outputRecordCollector
            builder.database = database
            builder.stagingOperations = stagingOperations
            builder.namingResolver = namingResolver
            builder.config = config
            builder.catalog = catalog
            builder.purgeStagingData = purgeStagingData
            builder.typerDeduper = typerDeduper
            builder.parsedCatalog = parsedCatalog
            builder.defaultNamespace = defaultNamespace
            builder.destinationColumns = destinationColumns
            return builder
        }

        private fun getMemoryLimit(bufferMemoryLimit: Optional<Long>): Long {
            return bufferMemoryLimit.orElse(
                (Runtime.getRuntime().maxMemory() * BufferManager.MEMORY_LIMIT_RATIO).toLong()
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
                var affectedStreamsAsString =
                    conflictingStreams.joinToString(", ") { config: WriteConfig ->
                        config.namespace + "." + config.streamName
                    }
                val message =
                    "You are trying to write multiple streams to the same table. Consider switching to a custom namespace format using " +
                        "\${SOURCE_NAMESPACE}, or moving one of them into a separate connection with a different stream prefix. " +
                        "Affected streams: $affectedStreamsAsString"
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
            destinationColumns: JavaBaseConstants.DestinationColumns
        ): List<WriteConfig> {
            return catalog!!.streams.map {
                toWriteConfig(namingResolver, config, parsedCatalog, destinationColumns).apply(it)
            }
        }

        private fun toWriteConfig(
            namingResolver: NamingConventionTransformer?,
            config: JsonNode?,
            parsedCatalog: ParsedCatalog?,
            destinationColumns: JavaBaseConstants.DestinationColumns
        ): Function<ConfiguredAirbyteStream, WriteConfig> {
            return Function<ConfiguredAirbyteStream, WriteConfig> { stream: ConfiguredAirbyteStream
                ->
                Preconditions.checkNotNull(
                    stream.destinationSyncMode,
                    "Undefined destination sync mode"
                )
                val abStream = stream.stream
                val streamName = abStream.name

                val outputSchema: String
                val tableName: String
                when (destinationColumns) {
                    JavaBaseConstants.DestinationColumns.V2_WITH_META,
                    JavaBaseConstants.DestinationColumns.V2_WITHOUT_META,
                    JavaBaseConstants.DestinationColumns.V2_WITH_GENERATION -> {
                        val streamId = parsedCatalog!!.getStream(abStream.namespace, streamName).id
                        outputSchema = streamId.rawNamespace
                        tableName = streamId.rawName
                    }
                    JavaBaseConstants.DestinationColumns.LEGACY -> {
                        outputSchema =
                            getOutputSchema(abStream, config!!["schema"].asText(), namingResolver)
                        tableName =
                            @Suppress("deprecation") namingResolver!!.getRawTableName(streamName)
                    }
                }
                val tmpTableName =
                    @Suppress("deprecation") namingResolver!!.getTmpTableName(streamName)
                val syncMode = stream.destinationSyncMode

                val writeConfig =
                    WriteConfig(
                        streamName,
                        abStream.namespace,
                        outputSchema,
                        tmpTableName,
                        tableName,
                        syncMode,
                        SYNC_DATETIME
                    )
                LOGGER.info { "Write config: $writeConfig" }
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
