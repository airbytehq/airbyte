/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.discover

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.util.ResourceUtils
import io.airbyte.protocol.models.v0.StreamDescriptor
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
    val metadata: Map<StreamIdentifier, TestStreamMetadata?>

    init {
        val json: String? = resource?.let { ResourceUtils.readResource(it) }
        val level0: List<Level1> = ValidatedJsonUtils.parseList(Level1::class.java, json)
        val map = mutableMapOf<StreamIdentifier, TestStreamMetadata?>()
        for (level1 in level0) {
            val desc = StreamDescriptor().withName(level1.name).withNamespace(level1.namespace)
            val streamID: StreamIdentifier = StreamIdentifier.from(desc)
            map[streamID] = null
            val level2: Level2 = level1.metadata ?: continue
            val columns: List<Field> =
                level2.columns.map { (id: String, fullyQualifiedClassName: String) ->
                    val fieldType: FieldType =
                        Class.forName(fullyQualifiedClassName).kotlin.objectInstance as FieldType
                    Field(id, fieldType)
                }
            map[streamID] = TestStreamMetadata(columns, level2.primaryKeys)
        }
        metadata = map
    }

    override fun session(config: SourceConfiguration): MetadataQuerier =
        object : MetadataQuerier {
            var isClosed = false

            override fun streamNamespaces(): List<String> {
                if (isClosed) throw IllegalStateException()
                return metadata.keys.mapNotNull { it.namespace }.distinct()
            }

            override fun streamNames(streamNamespace: String?): List<StreamIdentifier> {
                if (isClosed) throw IllegalStateException()
                return metadata.keys.filter { it.namespace == streamNamespace }
            }

            override fun fields(
                streamID: StreamIdentifier,
            ): List<Field> {
                if (isClosed) throw IllegalStateException()
                return metadata[streamID]?.fields ?: throw SQLException("query failed", "tbl")
            }

            override fun primaryKey(
                streamID: StreamIdentifier,
            ): List<List<String>> {
                if (isClosed) throw IllegalStateException()
                return metadata[streamID]?.primaryKeys ?: throw SQLException("query failed", "tbl")
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
