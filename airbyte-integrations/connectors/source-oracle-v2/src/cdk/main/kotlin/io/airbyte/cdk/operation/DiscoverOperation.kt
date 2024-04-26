/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.operation

import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.consumers.OutputConsumer
import io.airbyte.cdk.discover.ColumnMetadata
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.discover.TableName
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteStream
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
    val outputConsumer: OutputConsumer
) : Operation {

    override val type = OperationType.DISCOVER

    override fun execute() {
        val discoveredStreams: List<DiscoveredStream> =
            metadataQuerierFactory.session(config).use { metadataQuerier: MetadataQuerier ->
                metadataQuerier.tableNames().mapNotNull { tableName: TableName ->
                    val columnMetadata: List<ColumnMetadata> =
                        metadataQuerier.columnMetadata(tableName)
                    if (columnMetadata.isEmpty()) {
                        log.info { "Skipping no-column table $tableName." }
                        return@mapNotNull null
                    }
                    val primaryKeys: List<List<String>> = metadataQuerier.primaryKeys(tableName)
                    DiscoveredStream(tableName, columnMetadata, primaryKeys)
                }
            }
        val airbyteStreams: List<AirbyteStream> =
            discoveredStreams.map {
                if (config.global) {
                    metadataQuerierFactory.discoverMapper.globalAirbyteStream(it)
                } else {
                    metadataQuerierFactory.discoverMapper.nonGlobalAirbyteStream(it)
                }
            }
        outputConsumer.accept(AirbyteCatalog().withStreams(airbyteStreams))
    }
}
