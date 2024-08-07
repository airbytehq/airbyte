/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.operation

import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.consumers.OutputConsumer
import io.airbyte.cdk.source.AirbyteStreamDecorator
import io.airbyte.cdk.source.Field
import io.airbyte.cdk.source.MetadataQuerier
import io.airbyte.protocol.models.Field as AirbyteField
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

private val log = KotlinLogging.logger {}

@Singleton
@Requires(property = Operation.PROPERTY, value = "discover")
@Requires(env = ["source"])
class DiscoverOperation(
    val config: SourceConfiguration,
    val metadataQuerierFactory: MetadataQuerier.Factory<SourceConfiguration>,
    val airbyteStreamDecorator: AirbyteStreamDecorator,
    val outputConsumer: OutputConsumer,
) : Operation {
    override fun execute() {
        val airbyteStreams = mutableListOf<AirbyteStream>()
        metadataQuerierFactory.session(config).use { metadataQuerier: MetadataQuerier ->
            val namespaces: List<String?> =
                listOf<String?>(null) + metadataQuerier.streamNamespaces()
            for (namespace in namespaces) {
                for (name in metadataQuerier.streamNames(namespace)) {
                    val fields: List<Field> = metadataQuerier.fields(name, namespace)
                    if (fields.isEmpty()) {
                        log.info {
                            "Ignoring stream '$name' in '${namespace ?: ""}' because no fields were discovered."
                        }
                        continue
                    }
                    val primaryKeys: List<List<String>> =
                        metadataQuerier.primaryKeys(name, namespace)
                    val discoveredStream = DiscoveredStream(name, namespace, fields, primaryKeys)
                    airbyteStreams.add(toAirbyteStream(discoveredStream))
                }
            }
        }
        outputConsumer.accept(AirbyteCatalog().withStreams(airbyteStreams))
    }

    fun toAirbyteStream(discoveredStream: DiscoveredStream): AirbyteStream {
        val allColumnsByID: Map<String, Field> = discoveredStream.columns.associateBy { it.id }
        val airbyteStream: AirbyteStream =
            CatalogHelpers.createAirbyteStream(
                discoveredStream.name,
                discoveredStream.namespace,
                discoveredStream.columns.map {
                    AirbyteField.of(it.id, it.type.airbyteType.asJsonSchemaType())
                },
            )
        val pkColumnIDs: List<List<String>> =
            discoveredStream.primaryKeyColumnIDs.filter { pk: List<String> ->
                // Only keep PKs whose values can be round-tripped.
                pk.all { airbyteStreamDecorator.isPossiblePrimaryKeyElement(allColumnsByID[it]!!) }
            }
        airbyteStream.withSourceDefinedPrimaryKey(pkColumnIDs)
        if (config.global) {
            // There is a global feed of incremental records, like CDC.
            airbyteStreamDecorator.decorateGlobal(airbyteStream)
        } else if (discoveredStream.columns.any { airbyteStreamDecorator.isPossibleCursor(it) }) {
            // There is one field whose values can be round-tripped and aggregated by MAX.
            airbyteStreamDecorator.decorateNonGlobal(airbyteStream)
        } else {
            // There is no such field.
            airbyteStreamDecorator.decorateNonGlobalNoCursor(airbyteStream)
        }
        return airbyteStream
    }

    data class DiscoveredStream(
        val name: String,
        val namespace: String?,
        val columns: List<Field>,
        val primaryKeyColumnIDs: List<List<String>>,
    )
}
