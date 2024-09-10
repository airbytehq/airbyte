/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.discover

import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.util.ResourceUtils
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
    @Value("\${metadata.resource}") resource: String? = null,
) : MetadataQuerier.Factory<SourceConfiguration> {
    val metadata: Map<String?, Map<String, TestStreamMetadata?>>

    init {
        val json: String? = resource?.let { ResourceUtils.readResource(it) }
        val level0: List<Level1> = ValidatedJsonUtils.parseList(Level1::class.java, json)
        metadata = level0.map { it.namespace }.distinct().associateWith { mutableMapOf() }
        for (level1 in level0) {
            metadata[level1.namespace]!![level1.name] = null
            val level2: Level2 = level1.metadata ?: continue
            val columns: List<Field> =
                level2.columns.map { (id: String, fullyQualifiedClassName: String) ->
                    val fieldType: FieldType =
                        Class.forName(fullyQualifiedClassName).kotlin.objectInstance as FieldType
                    Field(id, fieldType)
                }
            metadata[level1.namespace]!![level1.name] =
                TestStreamMetadata(columns, level2.primaryKeys)
        }
    }

    override fun session(config: SourceConfiguration): MetadataQuerier =
        object : MetadataQuerier {
            var isClosed = false

            override fun streamNamespaces(): List<String> {
                if (isClosed) throw IllegalStateException()
                return metadata.keys.filterNotNull()
            }

            override fun streamNames(streamNamespace: String?): List<String> {
                if (isClosed) throw IllegalStateException()
                return metadata[streamNamespace]?.keys?.toList() ?: listOf()
            }

            override fun fields(
                streamName: String,
                streamNamespace: String?,
            ): List<Field> {
                if (isClosed) throw IllegalStateException()
                return metadata[streamNamespace]?.get(streamName)?.fields
                    ?: throw SQLException("query failed", "tbl")
            }

            override fun primaryKey(
                streamName: String,
                streamNamespace: String?,
            ): List<List<String>> {
                if (isClosed) throw IllegalStateException()
                return metadata[streamNamespace]?.get(streamName)?.primaryKeys
                    ?: throw SQLException("query failed", "tbl")
            }

            override fun extraChecks() {}

            override fun close() {
                isClosed = true
            }
        }
}

data class TestStreamMetadata(
    val fields: List<Field>,
    val primaryKeys: List<List<String>>,
)

data class Level1(
    val name: String,
    val namespace: String?,
    val metadata: Level2?,
)

data class Level2(
    val columns: Map<String, String>,
    val primaryKeys: List<List<String>>,
)
