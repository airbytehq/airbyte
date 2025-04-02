/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.discover

import io.airbyte.cdk.Operation
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteStream
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Requires(property = Operation.PROPERTY, value = "discover")
@Requires(env = ["source"])
class DiscoverOperation(
    val config: SourceConfiguration,
    val metadataQuerierFactory: MetadataQuerier.Factory<SourceConfiguration>,
    val airbyteStreamFactory: AirbyteStreamFactory,
    val outputConsumer: OutputConsumer,
) : Operation {
    private val log = KotlinLogging.logger {}

    override fun execute() {
        val airbyteStreams = mutableListOf<AirbyteStream>()
        metadataQuerierFactory.session(config).use { metadataQuerier: MetadataQuerier ->
            val namespaces: List<String?> =
                listOf<String?>(null) + metadataQuerier.streamNamespaces()
            for (namespace in namespaces) {
                for (streamID in metadataQuerier.streamNames(namespace)) {
                    val fields: List<Field> = metadataQuerier.fields(streamID)
                    if (fields.isEmpty()) {
                        log.info {
                            "Ignoring stream '${streamID.name}' in '${namespace ?: ""}' because no fields were discovered."
                        }
                        continue
                    }
                    val primaryKey: List<List<String>> = metadataQuerier.primaryKey(streamID)
                    val discoveredStream = DiscoveredStream(streamID, fields, primaryKey)
                    val airbyteStream: AirbyteStream =
                        airbyteStreamFactory.create(config, discoveredStream)
                    airbyteStreams.add(airbyteStream)
                }
            }
        }
        outputConsumer.accept(AirbyteCatalog().withStreams(airbyteStreams))
    }
}
