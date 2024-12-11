/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.data.DoubleCodec
import io.airbyte.cdk.data.FloatCodec
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.jdbc.*
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.sql.JDBCType
import java.sql.PreparedStatement
import java.sql.ResultSet

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

    data object MsSqlServerFloatAccessor : JdbcAccessor<Float> {
        override fun get(
            rs: ResultSet,
            colIdx: Int,
        ): Float?  {
            val retVal = rs.getFloat(colIdx).takeUnless { rs.wasNull() }
            log.info { "SGX value for column $colIdx is $retVal (stringVal = ${rs.getString(colIdx)}" }
            return retVal
        }

        override fun set(
            stmt: PreparedStatement,
            paramIdx: Int,
            value: Float,
        ) {
            stmt.setFloat(paramIdx, value)
        }
    }

    data object MsSqlServerFloatFieldType :
        SymmetricJdbcFieldType<Float>(
            LeafAirbyteSchemaType.NUMBER,
            MsSqlServerFloatAccessor,
            FloatCodec,
        )

    data object MsSqlServerDoubleFieldType :
        SymmetricJdbcFieldType<Double>(
            LeafAirbyteSchemaType.NUMBER,
            MsSqlServerDoubleAccessor,
            DoubleCodec,
        )


    data object MsSqlServerDoubleAccessor : JdbcAccessor<Double> {
        override fun get(
            rs: ResultSet,
            colIdx: Int,
        ): Double? {
            val retVal = rs.getDouble(colIdx).takeUnless { rs.wasNull() }
            log.info { "SGX value for column $colIdx is $retVal (stringVal = ${rs.getString(colIdx)}" }
            return retVal
        }

        override fun set(
            stmt: PreparedStatement,
            paramIdx: Int,
            value: Double,
        ) {
            stmt.setDouble(paramIdx, value)
        }
    }

    private fun leafType(type: SystemType): JdbcFieldType<*> {
        val retVal =  MsSqlServerSqlType.fromName(type.typeName)?.jdbcType
            ?: when (type.jdbcType) {
                JDBCType.BIT -> BooleanFieldType
                JDBCType.TINYINT -> ShortFieldType
                JDBCType.SMALLINT -> ShortFieldType
                JDBCType.INTEGER -> IntFieldType
                JDBCType.BIGINT -> BigIntegerFieldType
                JDBCType.FLOAT -> MsSqlServerFloatFieldType
                JDBCType.REAL ->
                    // according to https://learn.microsoft.com/en-us/sql/t-sql/data-types/float-and-real-transact-sql?view=sql-server-ver16,
                    // when precision is less than 25, the value is stored in a 4 bytes structure, which corresponds to a float in Java.
                    // Between 25 and 53, it's stored in a 8 bytes structure, which corresponds to a double in Java.
                    // Correspondance between SQLServer and java was mostly by experience, and the sizes match
                    if (type.precision!! < 25) {
                        FloatFieldType
                    } else {
                        DoubleFieldType
                    }
                JDBCType.DOUBLE -> MsSqlServerFloatFieldType
                JDBCType.NUMERIC -> DoubleFieldType
                JDBCType.DECIMAL -> DoubleFieldType
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
        log.info { "SGX getting leafType for ${type}, ${type.jdbcType}: $retVal" }
        return retVal
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
                log.info {"SGX nameToVallue = $nameToValue"}
                val retVal = nameToValue[name]
                return retVal
            }
        }
    }

    companion object {
        val DATETIME_FORMAT_MICROSECONDS = "yyyy-MM-dd'T'HH:mm:ss[.][SSSSSS]"
    }
}
