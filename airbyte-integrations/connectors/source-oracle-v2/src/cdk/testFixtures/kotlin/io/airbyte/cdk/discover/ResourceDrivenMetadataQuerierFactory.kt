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
@Requires(property = "metadata.resource")
@Replaces(MetadataQuerier.Factory::class)
class ResourceDrivenMetadataQuerierFactory(
    @Value("\${metadata.resource}") resource: String? = null
) : MetadataQuerier.Factory {

    val tableNames: List<TableName>
    val metadata: Map<TableName, TestTableMetadata>

    init {
        val json: String? = resource?.let { MoreResources.readResource(it) }
        val level0: List<Level1> = JsonUtils.parseList(Level1::class.java, json)
        tableNames = level0.map { it.key }
        metadata = level0.mapNotNull { level1: Level1 ->
            level1.value?.let { level2: Level2 ->
                val columns: List<Field> = level2.columns.map { (id: String, className: String) ->
                    Field(id, Class.forName(className).kotlin.objectInstance as FieldType)
                }
                level1.key to TestTableMetadata(columns, level2.primaryKeys)
            }
        }.toMap()
    }

    override fun session(config: SourceConfiguration): MetadataQuerier =
        object : MetadataQuerier {
            var isClosed = false

            override fun tableNames(): List<TableName> {
                if (isClosed) throw IllegalStateException()
                return tableNames
            }

            override fun fields(table: TableName): List<Field> =
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
    val columns: List<Field>,
    val primaryKeys: List<List<String>>
)

data class Level1(val key: TableName, val value: Level2?)
data class Level2(val columns: Map<String, String>, val primaryKeys: List<List<String>>)
