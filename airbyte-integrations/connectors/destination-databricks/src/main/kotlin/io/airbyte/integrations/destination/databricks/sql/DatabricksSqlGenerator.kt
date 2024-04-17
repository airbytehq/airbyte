package io.airbyte.integrations.destination.databricks.sql

import io.airbyte.integrations.base.destination.typing_deduping.ColumnId
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import java.time.Instant
import java.util.*

class DatabricksSqlGenerator : SqlGenerator {
    override fun buildStreamId(
        namespace: String,
        name: String,
        rawNamespaceOverride: String
    ): StreamId {
        TODO("Not yet implemented")
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
        TODO("Not yet implemented")
    }

    override fun clearLoadedAt(streamId: StreamId): Sql {
        TODO("Not yet implemented")
    }
}
