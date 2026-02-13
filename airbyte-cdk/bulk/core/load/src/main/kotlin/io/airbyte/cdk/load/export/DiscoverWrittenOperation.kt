/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.export

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.cdk.Operation
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.cdk.load.data.NullValue
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import kotlinx.coroutines.runBlocking

@Singleton
@Requires(property = Operation.PROPERTY, value = "discover-written")
class DiscoverWrittenOperation(
    private val catalog: DestinationCatalog,
    private val schemaEvolutionClient: TableSchemaEvolutionClient,
    private val destinationReader: DestinationReader,
    private val spec: ConfigurationSpecification,
) : Operation {
    private val log = KotlinLogging.logger {}

    override fun execute() {
        log.info { "Running discover-written..." }
        val catalogNode = JsonNodeFactory.instance.objectNode()
        val streamsArray = catalogNode.putArray("streams")

        for (stream in catalog.streams) {
            val tableName = stream.tableSchema.tableNames.finalTableName ?: continue
            log.info { "Discovering schema for: ${tableName.toPrettyString()}" }

            val tableSchema = runBlocking { schemaEvolutionClient.discoverSchema(tableName) }
            val columnStats = computeColumnStats(stream)

            val streamNode = JsonNodeFactory.instance.objectNode()
            streamNode.put("namespace", stream.unmappedNamespace)
            streamNode.put("name", stream.unmappedName)

            val schemaNode = streamNode.putObject("json_schema")
            schemaNode.put("type", "object")
            val propertiesNode = schemaNode.putObject("properties")

            for ((columnName, columnType) in tableSchema.columns) {
                val columnNode = propertiesNode.putObject(columnName)
                columnNode.put("x-destination-type", columnType.type)
                columnNode.put("x-destination-nullable", columnType.nullable)
                val stats = columnStats[columnName]
                if (stats != null) {
                    columnNode.put("x-null-count", stats.nullCount)
                    columnNode.put("x-non-null-count", stats.nonNullCount)
                }
            }

            streamsArray.add(streamNode)
        }

        val output = ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(catalogNode)
        println(output)
        log.info { "Discover-written complete." }
    }

    private fun computeColumnStats(stream: DestinationStream): Map<String, ColumnStats> {
        log.info { "Computing column stats for stream: ${stream.mappedDescriptor}" }
        val stats = mutableMapOf<String, MutableColumnStats>()
        var recordCount = 0L

        destinationReader.exportRecords(spec, stream).forEach { record ->
            for ((columnName, value) in record.data.values) {
                val columnStat = stats.getOrPut(columnName) { MutableColumnStats() }
                if (value is NullValue) {
                    columnStat.nullCount++
                } else {
                    columnStat.nonNullCount++
                }
            }
            recordCount++
            if (recordCount % 10_000L == 0L) {
                log.info { "Processed $recordCount records for stats..." }
            }
        }

        log.info { "Finished computing stats: $recordCount total records" }
        return stats.mapValues { (_, v) -> ColumnStats(v.nullCount, v.nonNullCount) }
    }
}

private data class MutableColumnStats(var nullCount: Long = 0, var nonNullCount: Long = 0)

data class ColumnStats(val nullCount: Long, val nonNullCount: Long)
