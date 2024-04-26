/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.source

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.discover.ColumnMetadata
import io.airbyte.cdk.discover.ColumnType
import io.airbyte.cdk.discover.DiscoverMapper
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.LeafType
import io.airbyte.cdk.discover.TableName
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Secondary
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton
import java.sql.JDBCType

/** [DiscoverMapper] implementation for [TestSource]. */
@Singleton
@Requires(env = [Environment.TEST])
@Secondary
class TestDiscoverMapper : DiscoverMapper {

    override fun selectStarFromTableLimit0(table: TableName): String =
        "SELECT * FROM ${table.fullyQualifiedName()} LIMIT 0"

    override fun columnType(c: ColumnMetadata): ColumnType =
        when (c.type) {
            JDBCType.BIT,
            JDBCType.BOOLEAN -> LeafType.BOOLEAN
            JDBCType.TINYINT,
            JDBCType.SMALLINT,
            JDBCType.INTEGER,
            JDBCType.BIGINT -> LeafType.INTEGER
            JDBCType.FLOAT,
            JDBCType.DOUBLE,
            JDBCType.REAL,
            JDBCType.NUMERIC,
            JDBCType.DECIMAL -> LeafType.NUMBER
            JDBCType.CHAR,
            JDBCType.NCHAR,
            JDBCType.NVARCHAR,
            JDBCType.VARCHAR,
            JDBCType.LONGVARCHAR -> LeafType.STRING
            JDBCType.DATE -> LeafType.DATE
            JDBCType.TIME -> LeafType.TIME_WITHOUT_TIMEZONE
            JDBCType.TIMESTAMP -> LeafType.TIMESTAMP_WITHOUT_TIMEZONE
            JDBCType.TIME_WITH_TIMEZONE -> LeafType.TIME_WITH_TIMEZONE
            JDBCType.TIMESTAMP_WITH_TIMEZONE -> LeafType.TIMESTAMP_WITH_TIMEZONE
            JDBCType.BLOB,
            JDBCType.BINARY,
            JDBCType.VARBINARY,
            JDBCType.LONGVARBINARY -> LeafType.BINARY
            JDBCType.ARRAY -> LeafType.STRING
            else -> LeafType.STRING
        }

    override fun isPossibleCursor(c: ColumnMetadata): Boolean =
        when (c.type) {
            JDBCType.TIMESTAMP_WITH_TIMEZONE,
            JDBCType.TIMESTAMP,
            JDBCType.TIME_WITH_TIMEZONE,
            JDBCType.TIME,
            JDBCType.DATE,
            JDBCType.TINYINT,
            JDBCType.SMALLINT,
            JDBCType.INTEGER,
            JDBCType.BIGINT,
            JDBCType.FLOAT,
            JDBCType.DOUBLE,
            JDBCType.REAL,
            JDBCType.NUMERIC,
            JDBCType.DECIMAL,
            JDBCType.NVARCHAR,
            JDBCType.VARCHAR,
            JDBCType.LONGVARCHAR -> c.nullable == false
            else -> false
        }

    private fun TableName.fullyQualifiedName(): String =
        if (schema == null) name else "${schema}.${name}"

    override fun globalAirbyteStream(stream: DiscoveredStream): AirbyteStream =
        DiscoverMapper.basicAirbyteStream(this, stream).apply {
            namespace = stream.table.schema
            supportedSyncModes = listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
            (jsonSchema["properties"] as ObjectNode).apply {
                set<ObjectNode>("_ab_cdc_lsn", LeafType.NUMBER.asJsonSchema())
                set<ObjectNode>(
                    "_ab_cdc_updated_at",
                    LeafType.TIMESTAMP_WITH_TIMEZONE.asJsonSchema()
                )
                set<ObjectNode>(
                    "_ab_cdc_deleted_at",
                    LeafType.TIMESTAMP_WITH_TIMEZONE.asJsonSchema()
                )
            }
            defaultCursorField = listOf("_ab_cdc_lsn")
            sourceDefinedCursor = true
        }

    override fun nonGlobalAirbyteStream(stream: DiscoveredStream): AirbyteStream =
        DiscoverMapper.basicAirbyteStream(this, stream).apply {
            namespace = stream.table.schema
            supportedSyncModes = listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
            if (defaultCursorField.isEmpty()) {
                supportedSyncModes = listOf(SyncMode.FULL_REFRESH)
            }
        }
}
