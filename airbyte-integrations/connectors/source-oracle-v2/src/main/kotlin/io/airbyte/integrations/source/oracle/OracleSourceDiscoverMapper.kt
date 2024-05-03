/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.discover.ArrayColumnType
import io.airbyte.cdk.discover.ColumnMetadata
import io.airbyte.cdk.discover.ColumnType
import io.airbyte.cdk.discover.DiscoverMapper
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.GenericUserDefinedType
import io.airbyte.cdk.discover.LeafType
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.discover.TableName
import io.airbyte.cdk.discover.UserDefinedArray
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.sql.Types

private val log = KotlinLogging.logger {}

@Singleton
class OracleSourceDiscoverMapper : DiscoverMapper {

    override fun selectFromTableLimit0(table: TableName, columns: List<String>): String =
        // Oracle doesn't do LIMIT, instead we need to involve ROWNUM.
        "SELECT ${columns.joinToString()} FROM ${table.fullyQualifiedName()} WHERE ROWNUM < 1"

    override fun columnType(c: ColumnMetadata) =
        when (val type = c.type) {
            is UserDefinedArray -> ArrayColumnType(recursiveArrayType(type))
            is GenericUserDefinedType ->
                // TODO: revisit this
                // Representing Oracle object types as JSON is convenient to do in 19c+
                // but not in earlier releases.
                // https://asktom.oracle.com/ords/f?p=100:11:::::P11_QUESTION_ID:9539152100346578907
                LeafType.JSONB
            is SystemType -> leafType(c.type.typeName, c.scale != 0) ?: LeafType.STRING
        }

    private fun recursiveArrayType(type: UserDefinedArray): ColumnType =
        when (val elementType = type.elementType) {
            is UserDefinedArray -> ArrayColumnType(recursiveArrayType(elementType))
            is GenericUserDefinedType -> LeafType.JSONB
            is SystemType -> leafType(elementType.typeName, Types.INTEGER != elementType.typeCode)
                    ?: LeafType.STRING
        }

    private fun leafType(typeName: String?, notInteger: Boolean): LeafType? =
        // This mapping includes literals returned by the JDBC driver as well as
        // *_TYPE_NAME column values from queries to ALL_* system tables.
        when (typeName) {
            "FLOAT",
            "BINARY_FLOAT",
            "BINARY_DOUBLE",
            "DOUBLE PRECISION",
            "REAL" -> LeafType.NUMBER
            "NUMBER",
            "NUMERIC",
            "DECIMAL",
            "DEC" -> if (notInteger) LeafType.NUMBER else LeafType.INTEGER
            "INTEGER",
            "INT",
            "SMALLINT" -> LeafType.INTEGER
            "BOOLEAN",
            "BOOL" -> LeafType.BOOLEAN
            "CHAR",
            "NCHAR",
            "NVARCHAR2",
            "VARCHAR2",
            "VARCHAR",
            "CHARACTER",
            "CHARACTER VARYING",
            "CHAR VARYING",
            "NCHAR VARYING",
            "NATIONAL CHARACTER VARYING",
            "NATIONAL CHARACTER",
            "NATIONAL CHAR VARYING",
            "NATIONAL CHAR" -> LeafType.STRING
            "BLOB",
            "CLOB",
            "NCLOB",
            "BFILE" -> LeafType.BINARY
            "DATE" -> LeafType.DATE
            "INTERVALDS",
            "INTERVAL DAY TO SECOND",
            "INTERVALYM",
            "INTERVAL YEAR TO MONTH" -> LeafType.STRING
            "JSON" -> LeafType.JSONB
            "LONG",
            "LONG RAW",
            "RAW",
            "ROWID" -> LeafType.BINARY
            "TIMESTAMP" -> LeafType.TIMESTAMP_WITHOUT_TIMEZONE
            "TIMESTAMP WITH LOCAL TIME ZONE",
            "TIMESTAMP WITH LOCAL TZ",
            "TIMESTAMP WITH TIME ZONE",
            "TIMESTAMP WITH TZ" -> LeafType.TIMESTAMP_WITH_TIMEZONE
            else -> null
        }

    override fun isPossibleCursor(c: ColumnMetadata): Boolean =
        // No surprises here.
        when (val type = columnType(c)) {
            is ArrayColumnType -> false
            is LeafType ->
                when (type) {
                    LeafType.BOOLEAN,
                    LeafType.BINARY,
                    LeafType.NULL,
                    LeafType.JSONB -> false
                    LeafType.STRING,
                    LeafType.DATE,
                    LeafType.TIME_WITH_TIMEZONE,
                    LeafType.TIME_WITHOUT_TIMEZONE,
                    LeafType.TIMESTAMP_WITH_TIMEZONE,
                    LeafType.TIMESTAMP_WITHOUT_TIMEZONE,
                    LeafType.INTEGER,
                    LeafType.NUMBER -> true
                }
        }

    private fun TableName.fullyQualifiedName(): String =
        // The catalog never comes into play with Oracle.
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
