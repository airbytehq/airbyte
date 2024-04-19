package io.airbyte.integrations.destination.databricks.jdbc

import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import java.time.Instant
import java.util.*

class DatabricksSqlGenerator(val namingTransformer: NamingConventionTransformer) : SqlGenerator {
    override fun buildStreamId(
        namespace: String,
        name: String,
        rawNamespaceOverride: String
    ): StreamId {
        return StreamId(
            namingTransformer.getNamespace(namespace),
            namingTransformer.getIdentifier(name),
            namingTransformer.getNamespace(rawNamespaceOverride),
            namingTransformer.getIdentifier(StreamId.concatenateRawTableName(namespace, name)),
            namespace,
            name
        )
    }

    override fun buildColumnId(name: String, suffix: String?): ColumnId {
        TODO("Not yet implemented")
    }

    override fun createTable(stream: StreamConfig, suffix: String, force: Boolean): Sql {
        TODO("Not yet implemented")
    }

    override fun createSchema(schema: String?): Sql {
        TODO("Not yet implemented")
    }

    override fun updateTable(
        stream: StreamConfig,
        finalSuffix: String,
        minRawTimestamp: Optional<Instant>,
        useExpensiveSaferCasting: Boolean
    ): Sql {
        TODO("Not yet implemented")
    }

    override fun overwriteFinalTable(stream: StreamId, finalSuffix: String): Sql {
        TODO("Not yet implemented")
    }

    override fun migrateFromV1toV2(
        streamId: StreamId,
        namespace: String?,
        tableName: String?
    ): Sql {
        throw UnsupportedOperationException("This method is not allowed in Databricks and should not be called")
    }

    override fun clearLoadedAt(streamId: StreamId): Sql {
        TODO("Not yet implemented")
    }
}
