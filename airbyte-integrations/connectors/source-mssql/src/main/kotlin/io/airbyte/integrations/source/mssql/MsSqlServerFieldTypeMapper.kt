/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.jdbc.*
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.sql.JDBCType

private val log = KotlinLogging.logger {}

@Singleton
@Primary
class MsSqlServerFieldTypeMapper : JdbcMetadataQuerier.FieldTypeMapper {
    override fun toFieldType(c: JdbcMetadataQuerier.ColumnMetadata): FieldType {
        when (val type = c.type) {
            is SystemType -> {
                val retVal = leafType(type)
                return retVal
            }
            else -> {
                return PokemonFieldType
            }
        }
    }

    private fun leafType(type: SystemType): JdbcFieldType<*> {
        return MsSqlServerSqlType.fromName(type.typeName)?.jdbcType
            ?: when (type.jdbcType) {
                JDBCType.BIT -> BooleanFieldType
                JDBCType.TINYINT -> ShortFieldType
                JDBCType.SMALLINT -> ShortFieldType
                JDBCType.INTEGER -> IntFieldType
                JDBCType.BIGINT -> BigIntegerFieldType
                JDBCType.FLOAT -> FloatFieldType
                JDBCType.REAL -> DoubleFieldType
                JDBCType.DOUBLE -> DoubleFieldType
                JDBCType.NUMERIC -> DoubleFieldType
                JDBCType.DECIMAL -> BigIntegerFieldType
                JDBCType.CHAR -> StringFieldType
                JDBCType.VARCHAR -> StringFieldType
                JDBCType.LONGVARCHAR -> StringFieldType
                JDBCType.DATE -> LocalDateFieldType
                JDBCType.TIME -> LocalTimeFieldType
                JDBCType.TIMESTAMP -> LocalDateTimeFieldType
                JDBCType.BINARY -> BytesFieldType
                JDBCType.VARBINARY -> BytesFieldType
                JDBCType.LONGVARBINARY -> BytesFieldType
                JDBCType.NULL -> NullFieldType
                JDBCType.OTHER -> PokemonFieldType
                JDBCType.JAVA_OBJECT -> PokemonFieldType
                JDBCType.DISTINCT -> PokemonFieldType
                JDBCType.STRUCT -> PokemonFieldType
                JDBCType.ARRAY -> PokemonFieldType
                JDBCType.BLOB -> BinaryStreamFieldType
                JDBCType.CLOB -> CharacterStreamFieldType
                JDBCType.REF -> PokemonFieldType
                JDBCType.DATALINK -> PokemonFieldType
                JDBCType.BOOLEAN -> BooleanFieldType
                JDBCType.ROWID -> PokemonFieldType
                JDBCType.NCHAR -> StringFieldType
                JDBCType.NVARCHAR -> StringFieldType
                JDBCType.LONGNVARCHAR -> StringFieldType
                JDBCType.NCLOB -> CharacterStreamFieldType
                JDBCType.SQLXML -> PokemonFieldType
                JDBCType.REF_CURSOR -> PokemonFieldType
                JDBCType.TIME_WITH_TIMEZONE -> OffsetTimeFieldType
                JDBCType.TIMESTAMP_WITH_TIMEZONE -> OffsetDateTimeFieldType
                null -> PokemonFieldType
            }
    }

    enum class MsSqlServerSqlType(val names: List<String>, val jdbcType: JdbcFieldType<*>) {
        BINARY(BinaryStreamFieldType, "VARBINARY", "BINARY"),
        DATETIME_TYPES(LocalDateTimeFieldType, "DATETIME", "DATETIME2", "SMALLDATETIME"),
        DATE(LocalDateFieldType, "DATE"),
        DATETIMEOFFSET(OffsetDateTimeFieldType, "DATETIMEOFFSET"),
        TIME_TYPE(LocalTimeFieldType, "TIME"),
        SMALLMONEY_TYPE(PokemonFieldType, "SMALLMONEY"),
        GEOMETRY(PokemonFieldType, "GEOMETRY"),
        GEOGRAPHY(PokemonFieldType, "GEOGRAPHY");

        constructor(
            jdbcType: JdbcFieldType<*>,
            vararg names: String
        ) : this(names.toList(), jdbcType) {}

        companion object {
            private val nameToValue =
                MsSqlServerSqlType.entries
                    .flatMap { msSqlServerSqlType ->
                        msSqlServerSqlType.names.map { name -> name to msSqlServerSqlType }
                    }
                    .toMap()

            fun fromName(name: String?): MsSqlServerSqlType? {
                val retVal = nameToValue[name]
                return retVal
            }
        }
    }

    companion object {
        val DATETIME_FORMAT_MICROSECONDS = "yyyy-MM-dd'T'HH:mm:ss[.][SSSSSS]"
    }
}
