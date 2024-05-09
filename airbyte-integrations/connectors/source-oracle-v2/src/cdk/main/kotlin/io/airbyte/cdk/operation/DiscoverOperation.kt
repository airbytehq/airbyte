/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.operation

import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.consumers.OutputConsumer
import io.airbyte.cdk.source.Field
import io.airbyte.cdk.source.MetadataQuerier
import io.airbyte.cdk.source.TableName
import io.airbyte.protocol.models.Field as AirbyteField
import io.airbyte.cdk.source.AirbyteStreamDecorator
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

private val log = KotlinLogging.logger {}

@Singleton
@Requires(property = CONNECTOR_OPERATION, value = "discover")
@Requires(env = ["source"])
class DiscoverOperation(
    val config: SourceConfiguration,
    val metadataQuerierFactory: MetadataQuerier.Factory,
    val airbyteStreamDecorator: AirbyteStreamDecorator,
    val outputConsumer: OutputConsumer
) : Operation {

    override fun execute() {
        val discoveredStreams: List<DiscoveredStream>
        metadataQuerierFactory.session(config).use { metadataQuerier: MetadataQuerier ->
            discoveredStreams =
                metadataQuerier.tableNames().mapNotNull { tableName: TableName ->
                    val fields: List<Field> = metadataQuerier.fields(tableName)
                    if (fields.isEmpty()) {
                        log.info { "Ignoring $tableName because no columns were discovered." }
                        return@mapNotNull null
                    }
                    val primaryKeys: List<List<String>> = metadataQuerier.primaryKeys(tableName)
                    DiscoveredStream(tableName, fields, primaryKeys)
                }
        }
        val airbyteStreams: List<AirbyteStream> = discoveredStreams.map(::toAirbyteStream)
        outputConsumer.accept(AirbyteCatalog().withStreams(airbyteStreams))
    }

    fun toAirbyteStream(discoveredStream: DiscoveredStream): AirbyteStream {
        val allColumnsByID: Map<String, Field> =
            discoveredStream.columns.associateBy { it.id }
        val airbyteStream: AirbyteStream =
            CatalogHelpers.createAirbyteStream(
                discoveredStream.table.name,
                discoveredStream.table.schema ?: discoveredStream.table.catalog,
                discoveredStream.columns.map {
                    AirbyteField.of(it.id, it.type.airbyteType.asJsonSchemaType())
                }
            )
        val pkColumnIDs: List<List<String>> =
            discoveredStream.primaryKeyColumnIDs.filter { pk: List<String> ->
                // Only keep PKs whose values can be round-tripped.
                pk.all { airbyteStreamDecorator.isPossiblePrimaryKeyElement(allColumnsByID[it]!!) }
            }
        airbyteStream.withSourceDefinedPrimaryKey(pkColumnIDs)
        val cursorColumnIDs: List<String> =
            discoveredStream.columns
                // Only keep cursors whose values can be round-tripped and aggregated by MAX.
                .filter { airbyteStreamDecorator.isPossibleCursor(it) }
                .map { it.id }
        airbyteStream.withDefaultCursorField(cursorColumnIDs)
        if (config.global) {
            airbyteStreamDecorator.decorateGlobal(airbyteStream)
        } else {
            airbyteStreamDecorator.decorateNonGlobal(airbyteStream)
        }
        return airbyteStream
    }

    data class DiscoveredStream(
        val table: TableName,
        val columns: List<Field>,
        val primaryKeyColumnIDs: List<List<String>>
    )

}
