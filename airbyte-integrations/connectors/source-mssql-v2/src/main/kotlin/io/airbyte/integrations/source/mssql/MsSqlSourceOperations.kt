/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.node.ObjectNode
import com.microsoft.sqlserver.jdbc.Geography
import com.microsoft.sqlserver.jdbc.Geometry
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.data.FloatCodec
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.discover.*
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.JdbcAirbyteStreamFactory
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.jdbc.*
import io.airbyte.cdk.jdbc.LosslessJdbcFieldType
import io.airbyte.cdk.read.*
import io.airbyte.cdk.read.SelectQueryGenerator
import io.airbyte.cdk.read.Stream
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.sql.JDBCType
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.time.OffsetDateTime

@Singleton
@Primary
class MsSqlSourceOperations :
    JdbcMetadataQuerier.FieldTypeMapper, SelectQueryGenerator, JdbcAirbyteStreamFactory {
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
        val retVal =
            MsSqlServerSqlType.fromName(type.typeName)?.jdbcType
                ?: when (type.jdbcType) {
                    JDBCType.BIT,
                    JDBCType.BOOLEAN -> BooleanFieldType
                    JDBCType.TINYINT,
                    JDBCType.SMALLINT -> ShortFieldType
                    JDBCType.INTEGER -> IntFieldType
                    JDBCType.BIGINT -> BigIntegerFieldType
                    JDBCType.FLOAT -> FloatFieldType
                    JDBCType.REAL ->
                        // according to
                        // https://learn.microsoft.com/en-us/sql/t-sql/data-types/float-and-real-transact-sql?view=sql-server-ver16,
                        // when precision is less than 25, the value is stored in a 4 bytes
                        // structure, which corresponds to a float in Java.
                        // Between 25 and 53, it's stored in a 8 bytes structure, which corresponds
                        // to a double in Java.
                        // Correspondance between SQLServer and java was mostly by experience, and
                        // the sizes match
                        if (type.precision!! < 25) FloatFieldType else DoubleFieldType
                    JDBCType.DOUBLE -> DoubleFieldType
                    JDBCType.NUMERIC,
                    JDBCType.DECIMAL -> BigDecimalFieldType
                    JDBCType.CHAR,
                    JDBCType.VARCHAR,
                    JDBCType.LONGVARCHAR,
                    JDBCType.NCHAR,
                    JDBCType.NVARCHAR,
                    JDBCType.LONGNVARCHAR -> StringFieldType
                    JDBCType.DATE -> LocalDateFieldType
                    JDBCType.TIME -> LocalTimeFieldType
                    JDBCType.TIMESTAMP -> LocalDateTimeFieldType
                    JDBCType.BINARY,
                    JDBCType.VARBINARY,
                    JDBCType.LONGVARBINARY -> BytesFieldType
                    JDBCType.BLOB -> BinaryStreamFieldType
                    JDBCType.CLOB,
                    JDBCType.NCLOB -> CharacterStreamFieldType
                    JDBCType.TIME_WITH_TIMEZONE -> OffsetTimeFieldType
                    JDBCType.TIMESTAMP_WITH_TIMEZONE -> OffsetDateTimeFieldType
                    JDBCType.NULL -> NullFieldType
                    JDBCType.OTHER,
                    JDBCType.JAVA_OBJECT,
                    JDBCType.DISTINCT,
                    JDBCType.STRUCT,
                    JDBCType.ARRAY,
                    JDBCType.REF,
                    JDBCType.DATALINK,
                    JDBCType.ROWID,
                    JDBCType.SQLXML,
                    JDBCType.REF_CURSOR,
                    null -> PokemonFieldType
                }
        return retVal
    }

    data object MsSqlServerFloatAccessor : JdbcAccessor<Float> {
        override fun get(
            rs: ResultSet,
            colIdx: Int,
        ): Float? {
            val retVal = rs.getFloat(colIdx).takeUnless { rs.wasNull() }
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

    data object MsSqlServerGeographyFieldType :
        SymmetricJdbcFieldType<String>(
            LeafAirbyteSchemaType.STRING,
            MsSqlServerGeographyAccessor,
            TextCodec,
        )

    data object MsSqlServerGeographyAccessor : JdbcAccessor<String> {
        override fun get(
            rs: ResultSet,
            colIdx: Int,
        ): String? {
            val bytes = rs.getBytes(colIdx)
            if (rs.wasNull() || bytes == null) return null
            return Geography.deserialize(bytes).toString()
        }

        override fun set(
            stmt: PreparedStatement,
            paramIdx: Int,
            value: String,
        ) {
            stmt.setBytes(paramIdx, Geography.parse(value).serialize())
        }
    }

    data object MsSqlServerGeometryFieldType :
        SymmetricJdbcFieldType<String>(
            LeafAirbyteSchemaType.STRING,
            MsSqlServerGeometryAccessor,
            TextCodec,
        )

    data object MsSqlServerGeometryAccessor : JdbcAccessor<String> {
        override fun get(
            rs: ResultSet,
            colIdx: Int,
        ): String? {
            val bytes = rs.getBytes(colIdx)
            if (rs.wasNull() || bytes == null) return null
            return Geometry.deserialize(bytes).toString()
        }

        override fun set(
            stmt: PreparedStatement,
            paramIdx: Int,
            value: String,
        ) {
            stmt.setBytes(paramIdx, Geometry.parse(value).serialize())
        }
    }

    data object MsSqlServerHierarchyFieldType :
        SymmetricJdbcFieldType<String>(
            LeafAirbyteSchemaType.STRING,
            StringAccessor,
            TextCodec,
        )

    enum class MsSqlServerSqlType(
        val names: List<String>,
        val jdbcType: JdbcFieldType<*>,
    ) {
        BINARY_FIELD(BinaryStreamFieldType, "VARBINARY", "BINARY"),
        DATETIME_TYPES(LocalDateTimeFieldType, "DATETIME", "DATETIME2", "SMALLDATETIME"),
        DATE(LocalDateFieldType, "DATE"),
        DATETIMEOFFSET(OffsetDateTimeFieldType, "DATETIMEOFFSET"),
        TIME_TYPE(LocalTimeFieldType, "TIME"),
        GEOMETRY(MsSqlServerGeometryFieldType, "GEOMETRY"),
        GEOGRAPHY(MsSqlServerGeographyFieldType, "GEOGRAPHY"),
        DOUBLE(DoubleFieldType, "MONEY", "SMALLMONEY"),
        HIERARCHY(MsSqlServerHierarchyFieldType, "HIERARCHYID"),
        ;

        constructor(
            jdbcType: JdbcFieldType<*>,
            vararg names: String,
        ) : this(names.toList(), jdbcType) {}

        companion object {
            private val nameToValue =
                MsSqlServerSqlType.entries
                    .flatMap { msSqlServerSqlType ->
                        msSqlServerSqlType.names.map { name ->
                            name.uppercase() to msSqlServerSqlType
                        }
                    }
                    .toMap()

            fun fromName(name: String?): MsSqlServerSqlType? {
                val retVal = nameToValue[name?.uppercase()]
                return retVal
            }
        }
    }

    override fun generate(ast: SelectQuerySpec): SelectQuery =
        SelectQuery(ast.sql(), ast.select.columns, ast.bindings())

    fun SelectQuerySpec.sql(): String {
        val components: List<String> =
            listOf(sql(select, limit), from.sql(), where.sql(), orderBy.sql())
        val sql: String = components.filter { it.isNotBlank() }.joinToString(" ")
        return sql
    }

    fun sql(
        selectNode: SelectNode,
        limit: LimitNode,
    ): String {
        val topClause: String =
            when (limit) {
                NoLimit -> ""
                Limit(0) -> "TOP 0 "
                is Limit -> "TOP ${limit.n} "
            }
        return "SELECT $topClause" +
            when (selectNode) {
                is SelectColumns -> selectNode.columns.joinToString(", ") { it.sql() }
                is SelectColumnMaxValue -> "MAX(${selectNode.column.sql()})"
            }
    }

    fun Field.sql(): String = if (type is MsSqlServerHierarchyFieldType) "$id.ToString()" else "$id"

    fun FromNode.sql(): String =
        when (this) {
            NoFrom -> ""
            is From -> if (this.namespace == null) "FROM $name" else "FROM $namespace.$name"
            is FromSample -> {
                val sample: String =
                    if (sampleRateInv == 1L) {
                        ""
                    } else {
                        " TABLESAMPLE (${sampleRatePercentage.toPlainString()} PERCENT)"
                    }
                val baseFrom = if (namespace == null) "FROM $name" else "FROM $namespace.$name"
                "$baseFrom$sample"
            }
        }

    fun WhereNode.sql(): String =
        when (this) {
            NoWhere -> ""
            is Where -> "WHERE ${clause.sql()}"
        }

    fun WhereClauseNode.sql(): String =
        when (this) {
            is And -> conj.joinToString(") AND (", "(", ")") { it.sql() }
            is Or -> disj.joinToString(") OR (", "(", ")") { it.sql() }
            is Equal -> "${column.sql()} = ?"
            is Greater -> "${column.sql()} > ?"
            is GreaterOrEqual -> "${column.sql()} >= ?"
            is LesserOrEqual -> "${column.sql()} <= ?"
            is Lesser -> "${column.sql()} < ?"
        }

    fun OrderByNode.sql(): String =
        when (this) {
            NoOrderBy -> ""
            is OrderBy -> "ORDER BY " + columns.joinToString(", ") { it.sql() }
        }

    fun SelectQuerySpec.bindings(): List<SelectQuery.Binding> = where.bindings() + limit.bindings()

    fun WhereNode.bindings(): List<SelectQuery.Binding> =
        when (this) {
            is NoWhere -> listOf()
            is Where -> clause.bindings()
        }

    fun WhereClauseNode.bindings(): List<SelectQuery.Binding> =
        when (this) {
            is And -> conj.flatMap { it.bindings() }
            is Or -> disj.flatMap { it.bindings() }
            is WhereClauseLeafNode -> {
                val type = column.type as LosslessJdbcFieldType<*, *>
                listOf(SelectQuery.Binding(bindingValue, type))
            }
        }

    fun LimitNode.bindings(): List<SelectQuery.Binding> =
        when (this) {
            NoLimit,
            Limit(0),
            is Limit, -> emptyList()
        }

    override val globalCursor: MetaField? = null
    override val globalMetaFields: Set<MetaField> = emptySet()
    //        setOf(
    //            CommonMetaField.CDC_UPDATED_AT,
    //            CommonMetaField.CDC_DELETED_AT,
    //            MsSqlServerCdcMetaFields.CDC_CURSOR,
    //            MsSqlServerCdcMetaFields.CDC_EVENT_SERIAL_NO,
    //            MsSqlServerCdcMetaFields.CDC_LSN,
    //        )

    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: ObjectNode,
    ) {
        //        recordData.set<JsonNode>(
        //            CommonMetaField.CDC_UPDATED_AT.id,
        //            CdcOffsetDateTimeMetaFieldType.jsonEncoder.encode(timestamp),
        //        )
        // CDC record decoration disabled
    }

    // CDC meta fields disabled - remove when CDC is not needed
    // enum class MsSqlServerCdcMetaFields(override val type: FieldType) : MetaField { ... }
}
