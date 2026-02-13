/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.export

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.cdk.Operation
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import kotlinx.coroutines.runBlocking

@Singleton
@Requires(property = Operation.PROPERTY, value = "discover-written")
class DiscoverWrittenOperation(
    private val catalog: DestinationCatalog,
    private val schemaEvolutionClient: TableSchemaEvolutionClient?,
    private val columnStatsProvider: ColumnStatsProvider?,
) : Operation {
    private val log = KotlinLogging.logger {}

    override fun execute() {
        log.info { "Running discover-written..." }
        val catalogNode = JsonNodeFactory.instance.objectNode()
        val streamsArray = catalogNode.putArray("streams")

        for (stream in catalog.streams) {
            try {
                val tableName = stream.tableSchema.tableNames.finalTableName
                if (tableName == null) {
                    log.warn {
                        "No final table name for stream ${stream.unmappedNamespace}.${stream.unmappedName}, skipping"
                    }
                    continue
                }
                log.info { "Discovering schema for: ${tableName.toPrettyString()}" }

                val tableSchema =
                    try {
                        if (schemaEvolutionClient != null) {
                            runBlocking { schemaEvolutionClient.discoverSchema(tableName) }
                        } else {
                            log.warn {
                                "No TableSchemaEvolutionClient available, skipping schema discovery for ${tableName.toPrettyString()}"
                            }
                            null
                        }
                    } catch (e: Exception) {
                        log.warn(e) {
                            "Failed to discover schema for ${tableName.toPrettyString()}, continuing without schema"
                        }
                        null
                    }

                val columnStats =
                    try {
                        if (columnStatsProvider != null && tableSchema != null) {
                            columnStatsProvider.computeColumnStats(
                                tableName,
                                tableSchema.columns.keys,
                            )
                        } else {
                            null
                        }
                    } catch (e: Exception) {
                        log.warn(e) {
                            "Failed to compute column stats for ${tableName.toPrettyString()}, continuing with null stats"
                        }
                        null
                    }

                val streamNode = JsonNodeFactory.instance.objectNode()
                streamNode.put("namespace", stream.unmappedNamespace)
                streamNode.put("name", stream.unmappedName)

                val schemaNode = streamNode.putObject("json_schema")
                schemaNode.put("type", "object")
                val propertiesNode = schemaNode.putObject("properties")

                if (tableSchema != null) {
                    for ((columnName, columnType) in tableSchema.columns) {
                        val columnNode = propertiesNode.putObject(columnName)
                        columnNode.put("x-destination-type", columnType.type)
                        columnNode.put("x-destination-nullable", columnType.nullable)
                        val stats = columnStats?.get(columnName)
                        if (stats != null) {
                            columnNode.put("x-null-count", stats.nullCount)
                            columnNode.put("x-non-null-count", stats.nonNullCount)
                        } else {
                            columnNode.putNull("x-null-count")
                            columnNode.putNull("x-non-null-count")
                        }
                    }
                }

                streamsArray.add(streamNode)
            } catch (e: Exception) {
                log.warn(e) {
                    "Unexpected error processing stream ${stream.unmappedNamespace}.${stream.unmappedName}, skipping"
                }
            }
        }

        val output =
            ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(catalogNode)
        println(output)
        log.info { "Discover-written complete." }
    }
}
