/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle

import io.airbyte.cdk.jdbc.ColumnMetadata
import io.airbyte.cdk.jdbc.SourceOperations
import io.airbyte.cdk.jdbc.TableName
import io.airbyte.protocol.models.JsonSchemaType
import jakarta.inject.Singleton
import java.sql.JDBCType

/**
 * Oracle-specific implementation of [SourceOperations].
 */
@Singleton
class OracleSourceOperations : SourceOperations {

    override fun selectStarFromTableLimit0(table: TableName) =
        // Oracle doesn't do LIMIT, instead we need to involve ROWNUM.
        "SELECT * FROM ${table.name} WHERE ROWNUM < 1"


    override fun toAirbyteType(c: ColumnMetadata): JsonSchemaType =
        // This is underspecified and almost certainly incorrect! TODO.
        when (c.type) {
            JDBCType.BIT,
            JDBCType.BOOLEAN -> JsonSchemaType.BOOLEAN
            JDBCType.TINYINT,
            JDBCType.SMALLINT -> JsonSchemaType.INTEGER
            JDBCType.INTEGER -> JsonSchemaType.INTEGER
            JDBCType.BIGINT -> JsonSchemaType.INTEGER
            JDBCType.FLOAT,
            JDBCType.DOUBLE -> JsonSchemaType.NUMBER
            JDBCType.REAL -> JsonSchemaType.NUMBER
            JDBCType.NUMERIC,
            JDBCType.DECIMAL -> JsonSchemaType.NUMBER
            JDBCType.CHAR,
            JDBCType.NCHAR,
            JDBCType.NVARCHAR,
            JDBCType.VARCHAR,
            JDBCType.LONGVARCHAR -> JsonSchemaType.STRING
            JDBCType.DATE -> JsonSchemaType.STRING_DATE
            JDBCType.TIME -> JsonSchemaType.STRING_TIME_WITHOUT_TIMEZONE
            JDBCType.TIMESTAMP -> JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE
            JDBCType.TIME_WITH_TIMEZONE -> JsonSchemaType.STRING_TIME_WITH_TIMEZONE
            JDBCType.TIMESTAMP_WITH_TIMEZONE -> JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE
            JDBCType.BLOB,
            JDBCType.BINARY,
            JDBCType.VARBINARY,
            JDBCType.LONGVARBINARY -> JsonSchemaType.STRING_BASE_64
            JDBCType.ARRAY -> JsonSchemaType.ARRAY
            else -> JsonSchemaType.STRING
        }
}
