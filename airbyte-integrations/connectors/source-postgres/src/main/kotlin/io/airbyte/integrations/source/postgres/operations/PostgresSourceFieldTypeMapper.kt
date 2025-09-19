/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres.operations

import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.BigIntegerFieldType
import io.airbyte.cdk.jdbc.BinaryStreamFieldType
import io.airbyte.cdk.jdbc.BooleanFieldType
import io.airbyte.cdk.jdbc.BytesFieldType
import io.airbyte.cdk.jdbc.DoubleFieldType
import io.airbyte.cdk.jdbc.FloatFieldType
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.JdbcFieldType
import io.airbyte.cdk.jdbc.LocalDateFieldType
import io.airbyte.cdk.jdbc.LocalTimeFieldType
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.jdbc.NullFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.PokemonFieldType
import io.airbyte.cdk.jdbc.ShortFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.sql.JDBCType

@Singleton
@Primary
class PostgresSourceFieldTypeMapper : JdbcMetadataQuerier.FieldTypeMapper {

    override fun toFieldType(c: JdbcMetadataQuerier.ColumnMetadata): FieldType =
        when (val type = c.type) {
            is SystemType -> leafType(type)
            else -> PokemonFieldType
        }

    private fun leafType(type: SystemType): JdbcFieldType<*> {

        return when (type.jdbcType) {
            JDBCType.BIT -> if (type.precision == 1) BooleanFieldType else BytesFieldType
            JDBCType.BOOLEAN -> BooleanFieldType
            JDBCType.TINYINT -> ShortFieldType
            JDBCType.SMALLINT,
            JDBCType.INTEGER -> IntFieldType
            JDBCType.BIGINT -> LongFieldType
            JDBCType.FLOAT,
            JDBCType.DOUBLE, -> {
                if ((type.precision ?: 0) <= 23) FloatFieldType else DoubleFieldType
            }
            JDBCType.DECIMAL -> {
                if (type.scale == 0) BigIntegerFieldType else BigDecimalFieldType
            }
            JDBCType.DATE -> LocalDateFieldType
            //            JDBCType.DATETIME -> LocalDateTimeFieldType
            JDBCType.TIMESTAMP -> OffsetDateTimeFieldType
            JDBCType.TIME -> LocalTimeFieldType
            JDBCType.CHAR,
            JDBCType.VARCHAR,
            //            JDBCType.TINYTEXT,
            //            JDBCType.TEXT,
            //            JDBCType.MEDIUMTEXT,
            //            JDBCType.LONGTEXT,
            //            JDBCType.ENUM,
            /*JDBCType.SET*/ -> StringFieldType
            //            JDBCType.JSON -> StringFieldType // TODO: replace this with
            // JsonStringFieldType
            //            JDBCType.TINYBLOB,
            JDBCType.BLOB,
            //            JDBCType.MEDIUMBLOB,
            //            JDBCType.LONGBLOB,
            JDBCType.BINARY,
            JDBCType.VARBINARY,
            /*JDBCType.GEOMETRY*/ -> BinaryStreamFieldType
            JDBCType.NULL -> NullFieldType
            //            JDBCType.VECTOR,
            //            JDBCType.UNKNOWN,
            /*null*/
            else -> PokemonFieldType
        }
    }
}
