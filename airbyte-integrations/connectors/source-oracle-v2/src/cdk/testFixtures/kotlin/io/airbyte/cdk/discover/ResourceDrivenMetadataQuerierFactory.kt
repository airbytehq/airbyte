/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.discover

import io.airbyte.cdk.command.JsonUtils
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.commons.resources.MoreResources
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton
import java.sql.SQLException

/** [MetadataQuerier] factory which serves content from a resource file for unit tests. */
@Singleton
@Requires(env = [Environment.TEST])
@Requires(notEnv = [Environment.CLI])
@Replaces(MetadataQuerier.Factory::class)
class ResourceDrivenMetadataQuerierFactory(
    @Value("\${metadata.resource}") resource: String? = null,
    override val discoverMapper: DiscoverMapper
) : MetadataQuerier.Factory {

    val tableNames: List<TableName>
    val metadata: Map<TableName, TestTableMetadata>

    init {
        val json: String? = resource?.let { MoreResources.readResource(it) }
        val list: List<TestMetadataPair> = JsonUtils.parseList(TestMetadataPair::class.java, json)
        tableNames = list.map { it.key }
        metadata = list.filter { it.value != null }.associate { it.key to it.value!! }
    }

    override fun session(config: SourceConfiguration): MetadataQuerier =
        object : MetadataQuerier {
            var isClosed = false

            override fun tableNames(): List<TableName> {
                if (isClosed) throw IllegalStateException()
                return tableNames
            }

            override fun columnMetadata(table: TableName): List<ColumnMetadata> =
                tableMetadata(table).columns

            override fun primaryKeys(table: TableName): List<List<String>> =
                tableMetadata(table).primaryKeys

            private fun tableMetadata(table: TableName): TestTableMetadata {
                if (isClosed) throw IllegalStateException()
                return metadata[table] ?: throw SQLException("query failed", "tbl")
            }

            override fun close() {
                isClosed = true
            }
        }
}

data class TestTableMetadata(
    val columns: List<ColumnMetadata>,
    val primaryKeys: List<List<String>>
)

data class TestMetadataPair(val key: TableName, val value: TestTableMetadata?)
