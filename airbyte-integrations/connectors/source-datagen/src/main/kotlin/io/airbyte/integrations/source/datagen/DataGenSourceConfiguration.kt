/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.datagen

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.output.DataChannelMedium
import io.airbyte.cdk.output.DataChannelMedium.SOCKET
import io.airbyte.cdk.output.DataChannelMedium.STDIO
import io.airbyte.cdk.output.sockets.DATA_CHANNEL_PROPERTY_PREFIX
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.datagen.flavor.Flavor
import io.airbyte.integrations.source.datagen.flavor.increment.IncrementFlavor
import io.airbyte.integrations.source.datagen.flavor.increment.IntegerFieldType
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Value
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.time.Duration
import java.util.*
import kotlin.time.Duration.Companion.seconds
import kotlin.time.toJavaDuration

/** Dev data gen-specific implementation of [SourceConfiguration] */
data class DataGenSourceConfiguration(
    override val global: Boolean = false,
    override val maxSnapshotReadDuration: Duration? = null,
    override val checkpointTargetInterval: Duration = 10.seconds.toJavaDuration(),
    override val maxConcurrency: Int,
    override val resourceAcquisitionHeartbeat: Duration = Duration.ofMillis(100L),
    override val realHost: String = "unused",
    override val realPort: Int = 0,
    override val sshTunnel: SshTunnelMethodConfiguration? = null,
    override val sshConnectionOptions: SshConnectionOptions =
        SshConnectionOptions.fromAdditionalProperties(emptyMap()),
    val flavor: Flavor,
    val maxRecords: Long
) : SourceConfiguration {
    /** Required to inject [DataGenSourceConfiguration] directly. */
    @Factory
    private class MicronautFactory {
        @Singleton
        fun dataGenSourceConfig(
            factory:
                SourceConfigurationFactory<
                    DataGenSourceConfigurationSpecification, DataGenSourceConfiguration,
                    >,
            supplier: ConfigurationSpecificationSupplier<DataGenSourceConfigurationSpecification>,
        ): DataGenSourceConfiguration = factory.make(supplier.get())
    }
}

@Singleton
class DataGenSourceConfigurationFactory
@Inject
constructor(
    @Value("\${${DATA_CHANNEL_PROPERTY_PREFIX}.medium}") val dataChannelMedium: String = STDIO.name,
    @Value("\${${DATA_CHANNEL_PROPERTY_PREFIX}.socket-paths}")
    val socketPaths: List<String> = emptyList()
) :
    SourceConfigurationFactory<
        DataGenSourceConfigurationSpecification, DataGenSourceConfiguration,
        > {

    private val log = KotlinLogging.logger {}

    override fun makeWithoutExceptionHandling(
        pojo: DataGenSourceConfigurationSpecification
    ): DataGenSourceConfiguration {
        if ((pojo.concurrency ?: 1) <= 0) {
            throw ConfigErrorException("Concurrency setting should be positive")
        }

        val maxConcurrency: Int =
            when (DataChannelMedium.valueOf(dataChannelMedium)) {
                STDIO -> pojo.concurrency ?: 1
                SOCKET -> {
                    pojo.concurrency ?: socketPaths.size
                }
            }
        log.info { "Effective concurrency: $maxConcurrency" }

        val catalog = parseMockCatalog(pojo.getFlavor())

        // unnecessary rn cuz incremental is default, template for future flavor additions
        //        if (pojo.getFlavor() is Incremental) {
        //            log.info { "Using Incremental Flavor" }
        //            return DataGenSourceConfiguration(maxConcurrency = maxConcurrency, flavor =
        // IncrementFlavor, runDuration = runDuration)
        //        }

        return DataGenSourceConfiguration(
            maxConcurrency = maxConcurrency,
            flavor = IncrementFlavor,
            maxRecords = pojo.maxRecords,
        )
    }

    //@Throws(io.airbyte.validation.json.JsonValidationException::class)
    fun parseMockCatalog(config: FlavorSpec): AirbyteCatalog {
        when (config) {
            is Incremental -> {
                val streamName = config.streamName
                val streamSchemaText = config.streamSchema
                // val streamDuplication
                val streamSchema: Optional<JsonNode?> =
                    Jsons.deseriali(streamSchemaText) //deserialize string to jsonNode
//                if (streamSchema.isEmpty()) {
//                    throw io.airbyte.validation.json.JsonValidationException(
//                        String.format(
//                            "Stream \"%s\" has invalid schema: %s",
//                            streamName,
//                            streamSchemaText,
//                        ),
//                    )
//                }
//                ContinuousFeedConfig.checkSchema(streamName, streamSchema.get())

                // if (streamDuplication == 1) {
                    val stream =
                        AirbyteStream().withName(streamName).withJsonSchema(streamSchema.get())
                            .withSupportedSyncModes(
                                com.google.common.collect.Lists.newArrayList<SyncMode?>(
                                    SyncMode.FULL_REFRESH,
                                ),
                            )
                    return AirbyteCatalog().withStreams(mutableListOf<AirbyteStream?>(stream))
//                } else {
//                    val streams: MutableList<AirbyteStream?> =
//                        ArrayList<AirbyteStream?>(streamDuplication)
//                    for (i in 0..<streamDuplication) {
//                        streams.add(
//                            AirbyteStream()
//                                .withName(java.lang.String.join("_", streamName, i.toString()))
//                                .withSupportedSyncModes(
//                                    com.google.common.collect.Lists.newArrayList<SyncMode?>(
//                                        SyncMode.FULL_REFRESH,
//                                    ),
//                                )
//                                .withJsonSchema(streamSchema.get()),
//                        )
//                    }
//                    return AirbyteCatalog().withStreams(streams)
//                }
            }

//            MockCatalogType.MULTI_STREAM -> {
//                val streamSchemasText = mockCatalogConfig.get("stream_schemas").asText()
//                val streamSchemas: Optional<JsonNode?> =
//                    io.airbyte.commons.json.Jsons.tryDeserialize(streamSchemasText)
//                if (streamSchemas.isEmpty()) {
//                    throw io.airbyte.validation.json.JsonValidationException("Input stream schemas are invalid: %s" + streamSchemasText)
//                }
//
//                val streamEntries: MutableList<MutableMap.MutableEntry<String?, JsonNode?>> =
//                    io.airbyte.commons.util.MoreIterators.toList<MutableMap.MutableEntry<String?, JsonNode?>?>(
//                        streamSchemas.get().fields(),
//                    )
//                val streams: MutableList<AirbyteStream?> =
//                    ArrayList<AirbyteStream?>(streamEntries.size)
//                for (entry in streamEntries) {
//                    val streamName = entry.key
//                    val streamSchema: JsonNode = entry.value!!
//                    ContinuousFeedConfig.checkSchema(streamName, streamSchema)
//                    streams.add(
//                        AirbyteStream().withName(streamName).withJsonSchema(streamSchema)
//                            .withSupportedSyncModes(
//                                com.google.common.collect.Lists.newArrayList<SyncMode?>(
//                                    SyncMode.FULL_REFRESH,
//                                ),
//                            ),
//                    )
//                }
//                return AirbyteCatalog().withStreams(streams)
//            }

            else -> throw IllegalArgumentException("Unsupported mock catalog type" )
        }
    }

    fun parseSchema(schemaJson: String): List<Field> {
        val mapper = jacksonObjectMapper()
        val root = mapper.readTree(schemaJson)

        val properties = root["properties"] ?: return emptyList()

        return properties.fields().asSequence().map { (name, definition) ->
            val typeNode = definition["airbyte_type"]?.asText()
            val fieldType = when (typeNode) {
                "integer" -> IntegerFieldType
                else -> IntegerFieldType
            }
            Field(name, fieldType)
        }.toList()

    }
}
