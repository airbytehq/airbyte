/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.ColumnMetadata
import io.airbyte.cdk.discover.DiscoverMapper
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.discover.TableName
import io.airbyte.cdk.operation.CONNECTOR_OPERATION
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Requires
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton
import java.sql.JDBCType
import java.sql.SQLException

/**
 * [MetadataQuerier] factory which serves content from a catalog for unit tests. This is useful for
 * unit-testing READ operation components in cases where we want to assume that the catalog and
 * state are all valid with respect to the source database schema. In effect, with this
 * implementation, the catalog will be high-fiving itself.
 */
@Singleton
@Requires(env = [Environment.TEST])
@Requires(notEnv = [Environment.CLI])
@Requires(property = CONNECTOR_OPERATION, value = "read")
@Requires(property = "metadata.catalog")
@Primary
@Replaces(MetadataQuerier.Factory::class)
class CatalogDrivenMetadataQuerierFactory(
    override val discoverMapper: DiscoverMapper,
    val catalog: ConfiguredAirbyteCatalog
) : MetadataQuerier.Factory {

    override fun session(config: SourceConfiguration): MetadataQuerier =
        object : MetadataQuerier {
            var isClosed = false

            override fun tableNames(): List<TableName> {
                if (isClosed) throw IllegalStateException()
                return catalog.streams.map {
                    TableName(schema = it.stream.namespace, name = it.stream.name, type = "TABLE")
                }
            }

            override fun columnMetadata(table: TableName): List<ColumnMetadata> {
                val stream: ConfiguredAirbyteStream = stream(table)
                val jsonSchema: JsonNode = stream.stream.jsonSchema["properties"]!!
                return jsonSchema.fields().asSequence().toList().map {
                    (field: String, value: JsonNode) ->
                    JDBCType.entries
                        .map { ColumnMetadata(name = field, label = field, type = it) }
                        .find { discoverMapper.columnType(it).asJsonSchema() == value }
                        ?: ColumnMetadata(name = field, label = field)
                }
            }

            override fun primaryKeys(table: TableName): List<List<String>> =
                stream(table).stream.sourceDefinedPrimaryKey

            fun stream(table: TableName): ConfiguredAirbyteStream {
                if (isClosed) throw IllegalStateException()
                return catalog.streams.find {
                    it.stream.name == table.name && it.stream.namespace == table.schema
                }
                    ?: throw SQLException("query failed")
            }

            override fun close() {
                isClosed = true
            }
        }
}
