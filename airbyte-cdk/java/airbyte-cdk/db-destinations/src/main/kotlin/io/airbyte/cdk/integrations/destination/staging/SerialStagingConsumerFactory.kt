/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.staging

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.base.Preconditions
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer
import io.airbyte.cdk.integrations.destination.jdbc.WriteConfig
import io.airbyte.cdk.integrations.destination.record_buffer.BufferCreateFunction
import io.airbyte.cdk.integrations.destination.record_buffer.SerializedBufferingStrategy
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog
import io.airbyte.integrations.base.destination.typing_deduping.TypeAndDedupeOperationValve
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import java.time.Instant
import java.util.*
import java.util.function.Consumer
import java.util.function.Function
import java.util.stream.Collectors
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * Uses both Factory and Consumer design pattern to create a single point of creation for consuming
 * [AirbyteMessage] for processing
 */
open class SerialStagingConsumerFactory {
    fun create(
        outputRecordCollector: Consumer<AirbyteMessage>,
        database: JdbcDatabase,
        stagingOperations: StagingOperations,
        namingResolver: NamingConventionTransformer,
        onCreateBuffer: BufferCreateFunction,
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        purgeStagingData: Boolean,
        typerDeduperValve: TypeAndDedupeOperationValve,
        typerDeduper: TyperDeduper,
        parsedCatalog: ParsedCatalog,
        defaultNamespace: String?,
        useDestinationsV2Columns: Boolean
    ): AirbyteMessageConsumer {
        val writeConfigs =
            createWriteConfigs(
                namingResolver,
                config,
                catalog,
                parsedCatalog,
                useDestinationsV2Columns
            )
        return BufferedStreamConsumer(
            outputRecordCollector,
            GeneralStagingFunctions.onStartFunction(
                database,
                stagingOperations,
                writeConfigs,
                typerDeduper
            ),
            SerializedBufferingStrategy(
                onCreateBuffer,
                catalog,
                SerialFlush.function(
                    database,
                    stagingOperations,
                    writeConfigs,
                    catalog,
                    typerDeduperValve,
                    typerDeduper
                )
            ),
            GeneralStagingFunctions.onCloseFunction(
                database,
                stagingOperations,
                writeConfigs,
                purgeStagingData,
                typerDeduper
            ),
            catalog,
            { data: JsonNode? -> stagingOperations.isValidData(data) },
            defaultNamespace
        )
    }

    companion object {
        private val LOGGER: Logger =
            LoggerFactory.getLogger(SerialStagingConsumerFactory::class.java)

        // using a random string here as a placeholder for the moment.
        // This would avoid mixing data in the staging area between different syncs (especially if
        // they
        // manipulate streams with similar names)
        // if we replaced the random connection id by the actual connection_id, we'd gain the
        // opportunity to
        // leverage data that was uploaded to stage
        // in a previous attempt but failed to load to the warehouse for some reason (interrupted?)
        // instead.
        // This would also allow other programs/scripts
        // to load (or reload backups?) in the connection's staging area to be loaded at the next
        // sync.
        private val SYNC_DATETIME: Instant = Instant.now()
        val RANDOM_CONNECTION_ID: UUID = UUID.randomUUID()

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
            namingResolver: NamingConventionTransformer,
            config: JsonNode,
            catalog: ConfiguredAirbyteCatalog,
            parsedCatalog: ParsedCatalog,
            useDestinationsV2Columns: Boolean
        ): List<WriteConfig> {
            return catalog.streams
                .stream()
                .map(toWriteConfig(namingResolver, config, parsedCatalog, useDestinationsV2Columns))
                .collect(Collectors.toList())
        }

        private fun toWriteConfig(
            namingResolver: NamingConventionTransformer,
            config: JsonNode,
            parsedCatalog: ParsedCatalog,
            useDestinationsV2Columns: Boolean
        ): Function<ConfiguredAirbyteStream, WriteConfig> {
            return Function { stream: ConfiguredAirbyteStream ->
                Preconditions.checkNotNull(
                    stream.destinationSyncMode,
                    "Undefined destination sync mode"
                )
                val abStream = stream.stream
                val streamName = abStream.name

                val outputSchema: String
                val tableName: String?
                if (useDestinationsV2Columns) {
                    val streamId = parsedCatalog.getStream(abStream.namespace, streamName).id
                    outputSchema = streamId.rawNamespace
                    tableName = streamId.rawName
                } else {
                    outputSchema =
                        getOutputSchema(abStream, config["schema"].asText(), namingResolver)
                    tableName = @Suppress("deprecation") namingResolver.getRawTableName(streamName)
                }
                val tmpTableName =
                    @Suppress("deprecation") namingResolver.getTmpTableName(streamName)
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
                LOGGER.info("Write config: {}", writeConfig)
                writeConfig
            }
        }

        private fun getOutputSchema(
            stream: AirbyteStream,
            defaultDestSchema: String,
            namingResolver: NamingConventionTransformer
        ): String {
            return if (stream.namespace != null) namingResolver.getNamespace(stream.namespace)
            else namingResolver.getNamespace(defaultDestSchema)
        }
    }
}
