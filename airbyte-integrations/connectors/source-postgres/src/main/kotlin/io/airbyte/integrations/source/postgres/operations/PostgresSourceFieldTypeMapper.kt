/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres.operations

import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.jdbc.ArrayFieldType
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.BinaryStreamFieldType
import io.airbyte.cdk.jdbc.BooleanFieldType
import io.airbyte.cdk.jdbc.DoubleFieldType
import io.airbyte.cdk.jdbc.FloatFieldType
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.JdbcFieldType
import io.airbyte.cdk.jdbc.LocalDateFieldType
import io.airbyte.cdk.jdbc.LocalDateTimeFieldType
import io.airbyte.cdk.jdbc.LocalTimeFieldType
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.jdbc.NullFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.OffsetTimeFieldType
import io.airbyte.cdk.jdbc.PokemonFieldType
import io.airbyte.cdk.jdbc.ShortFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.integrations.source.postgres.operations.types.BoxFieldType
import io.airbyte.integrations.source.postgres.operations.types.CircleFieldType
import io.airbyte.integrations.source.postgres.operations.types.HstoreFieldType
import io.airbyte.integrations.source.postgres.operations.types.LegacyBooleanBitsFieldType
import io.airbyte.integrations.source.postgres.operations.types.LineFieldType
import io.airbyte.integrations.source.postgres.operations.types.LsegFieldType
import io.airbyte.integrations.source.postgres.operations.types.PathFieldType
import io.airbyte.integrations.source.postgres.operations.types.PointFieldType
import io.airbyte.integrations.source.postgres.operations.types.PolygonFieldType
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.sql.JDBCType

@Singleton
@Primary
class PostgresSourceFieldTypeMapper : JdbcMetadataQuerier.FieldTypeMapper {

    override fun toFieldType(c: JdbcMetadataQuerier.ColumnMetadata): FieldType =
        when (val type = c.type) {
            is SystemType -> {
                val pgType = PgSystemType(type)
                if (pgType.isArray) {
                    ArrayFieldType(scalarType(pgType))
                } else scalarType(pgType)
            }
            else -> PokemonFieldType
        }

    private fun scalarType(type: PgSystemType): JdbcFieldType<*> {
        // TODO (https://github.com/airbytehq/airbyte-internal-issues/issues/15946):
        //  Remove this - preserves legacy mapping of "_oid" array inconsistent with "oid" scalar
        if (type.isArray && type.scalarTypeName == "oid") return BigDecimalFieldType
        return when (type.scalarJdbcType) {
            JDBCType.BIT ->
                // BOOLEAN reports as JDBCType.BIT
                if (type.scalarTypeName == "bool") BooleanFieldType
                // TODO (https://github.com/airbytehq/airbyte-internal-issues/issues/15946):
                //  Fix array types mismatching scalar types.
                //  Currently: bit(1) -> STRING; _bit(1) -> ARRAY<BOOLEAN>
                else if (type.isArray) LegacyBooleanBitsFieldType else StringFieldType
            JDBCType.BOOLEAN -> BooleanFieldType
            JDBCType.SMALLINT -> ShortFieldType
            JDBCType.INTEGER ->
                // oid type is unsigned and must be cast to Long to avoid truncation
                if (type.scalarTypeName == "oid") LongFieldType else IntFieldType
            JDBCType.BIGINT -> LongFieldType
            JDBCType.REAL -> FloatFieldType
            JDBCType.FLOAT,
            JDBCType.DOUBLE -> DoubleFieldType
            JDBCType.NUMERIC,
            JDBCType.DECIMAL -> {
                // TODO (https://github.com/airbytehq/airbyte-internal-issues/issues/15879):
                //  Fix type handling for numeric arrays.
                //  Precision and scale for array types are not accurately reported by JDBC.
                //  If we are able to fetch the real values, we should remove this clause.
                if (type.isArray) BigDecimalFieldType
                else if (type.precision != 0 && type.scale == 0) IntFieldType
                else BigDecimalFieldType
            }
            JDBCType.DATE -> LocalDateFieldType
            JDBCType.TIMESTAMP ->
                // JDBC driver reports timestamptz as TIMESTAMP instead of TIMESTAMP_WITH_TIMEZONE
                // for complex and historical reasons
                if (type.scalarTypeName == "timestamptz") OffsetDateTimeFieldType
                else LocalDateTimeFieldType
            JDBCType.TIME ->
                // JDBC driver reports timetz as TIME instead of TIME_WITH_TIMEZONE
                // for complex and historical reasons
                if (type.scalarTypeName == "timetz") OffsetTimeFieldType else LocalTimeFieldType
            JDBCType.CHAR,
            JDBCType.VARCHAR -> StringFieldType
            JDBCType.BINARY,
            JDBCType.VARBINARY ->
                if (type.scalarTypeName == "bytea") StringFieldType else BinaryStreamFieldType
            JDBCType.NULL -> NullFieldType
            JDBCType.OTHER ->
                when (type.scalarTypeName) {
                    "hstore" -> HstoreFieldType
                    "circle" -> CircleFieldType
                    "box" -> BoxFieldType
                    "line" -> LineFieldType
                    "lseg" -> LsegFieldType
                    "path" -> PathFieldType
                    "point" -> PointFieldType
                    "polygon" -> PolygonFieldType
                    // Legacy mapping. Could be JsonStringFieldType instead?
                    "json" -> StringFieldType
                    // Legacy mapping. Could be JsonStringFieldType instead?
                    "jsonb" -> StringFieldType
                    else -> StringFieldType
                }
            else -> PokemonFieldType
        }
    }

    class PgSystemType(systemType: SystemType) {
        val isArray: Boolean = systemType.typeName!!.startsWith("_")
        val scalarTypeName =
            if (isArray) systemType.typeName!!.substring(1) else systemType.typeName!!
        val scalarJdbcType: JDBCType =
            if (isArray) scalarJDBCType(systemType.typeName!!) else systemType.jdbcType!!
        // TODO: Fix type handling for numeric arrays.
        //  Requires fetching the correct scale and precision of array elements from another source.
        //  https://github.com/airbytehq/airbyte-internal-issues/issues/15879
        val scale = systemType.scale
        val precision = systemType.precision

        init {
            // TODO: Better user-facing message? Alert Extract team?
            requireNotNull(systemType.typeName)
            requireNotNull(systemType.jdbcType)
        }

        // Postgres reports the JDBC type of all arrays as JDBCType.ARRAY. Here, we use the
        // name of the array type to determine the JDBC type of its elements. Array type names
        // are prefixed with an underscore. These names are canonical, not aliases. But be warned:
        // the same is not true of scalar types, whose type names can be aliases.
        private fun scalarJDBCType(arrayTypeName: String): JDBCType =
            when (arrayTypeName) {
                "_bit",
                "_varbit" -> JDBCType.BIT
                "_bool" -> JDBCType.BOOLEAN
                "_text",
                "_varchar",
                "_name" -> JDBCType.VARCHAR
                "_char",
                "_bpchar" -> JDBCType.CHAR
                "_int2" -> JDBCType.SMALLINT
                "_int4",
                "_oid" -> JDBCType.INTEGER
                "_int8", -> JDBCType.BIGINT
                "_numeric",
                "_money" -> JDBCType.NUMERIC
                "_float4" -> JDBCType.REAL
                "_float8" -> JDBCType.DOUBLE
                // JDBC driver reports timestamptz as TIMESTAMP instead of TIMESTAMP_WITH_TIMEZONE
                // for complex and historical reasons. We follow suit for the array case.
                "_timestamptz" -> JDBCType.TIMESTAMP
                "_timestamp" -> JDBCType.TIMESTAMP
                // JDBC driver reports timetz as TIME instead of TIMESTAMP_WITH_TIMEZONE
                // for complex and historical reasons. We follow suit for the array case.
                "_timetz" -> JDBCType.TIME
                "_time" -> JDBCType.TIME
                "_date" -> JDBCType.DATE
                "_bytea" -> JDBCType.VARBINARY
                else -> JDBCType.OTHER
            }
    }
}
