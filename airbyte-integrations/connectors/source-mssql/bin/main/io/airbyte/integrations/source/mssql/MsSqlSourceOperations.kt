/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.microsoft.sqlserver.jdbc.Geography
import com.microsoft.sqlserver.jdbc.Geometry
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.data.FloatCodec
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.LocalDateTimeCodec
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.discover.CdcIntegerMetaFieldType
import io.airbyte.cdk.discover.CdcOffsetDateTimeMetaFieldType
import io.airbyte.cdk.discover.CdcStringMetaFieldType
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.JdbcAirbyteStreamFactory
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.jdbc.*
import io.airbyte.cdk.jdbc.LosslessJdbcFieldType
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.*
import io.airbyte.cdk.read.SelectQueryGenerator
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.sql.JDBCType
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.sql.Timestamp
import java.time.LocalDateTime
import java.time.OffsetDateTime

private val log = KotlinLogging.logger {}

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
                    JDBCType.TIMESTAMP -> MsSqlServerLocalDateTimeFieldType
                    JDBCType.BINARY,
                    JDBCType.VARBINARY,
                    JDBCType.LONGVARBINARY -> BytesFieldType
                    JDBCType.BLOB -> BinaryStreamFieldType
                    JDBCType.CLOB,
                    JDBCType.NCLOB -> CharacterStreamFieldType
                    JDBCType.TIME_WITH_TIMEZONE -> OffsetTimeFieldType
                    JDBCType.TIMESTAMP_WITH_TIMEZONE -> OffsetDateTimeFieldType
                    JDBCType.NULL -> NullFieldType
                    JDBCType.SQLXML -> XmlFieldType
                    JDBCType.OTHER,
                    JDBCType.JAVA_OBJECT,
                    JDBCType.DISTINCT,
                    JDBCType.STRUCT,
                    JDBCType.ARRAY,
                    JDBCType.REF,
                    JDBCType.DATALINK,
                    JDBCType.ROWID,
                    JDBCType.REF_CURSOR,
                    null -> PokemonFieldType
                }
        return retVal
    }

    // Custom LocalDateTime accessor that truncates to 6 decimal places (microseconds)
    // SQL Server datetime2 can have up to 7 decimal places, but destination may only support 6
    // decimal places
    data object MsSqlServerLocalDateTimeAccessor : JdbcAccessor<LocalDateTime> {
        override fun get(
            rs: ResultSet,
            colIdx: Int,
        ): LocalDateTime? {
            val timestamp = rs.getTimestamp(colIdx)?.takeUnless { rs.wasNull() } ?: return null
            val localDateTime = timestamp.toLocalDateTime()
            // Truncate to microseconds (6 decimal places) by zeroing out the nanoseconds beyond
            // microseconds
            val truncatedNanos = (localDateTime.nano / 1000) * 1000
            return localDateTime.withNano(truncatedNanos)
        }

        override fun set(
            stmt: PreparedStatement,
            paramIdx: Int,
            value: LocalDateTime,
        ) {
            stmt.setTimestamp(paramIdx, Timestamp.valueOf(value))
        }
    }

    data object MsSqlServerLocalDateTimeFieldType :
        SymmetricJdbcFieldType<LocalDateTime>(
            LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
            MsSqlServerLocalDateTimeAccessor,
            LocalDateTimeCodec,
        )

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
        DATETIME_TYPES(MsSqlServerLocalDateTimeFieldType, "DATETIME", "DATETIME2", "SMALLDATETIME"),
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

    /**
     * Quotes an identifier for SQL Server using square brackets. If the identifier contains a
     * closing bracket ']', it will be escaped as ']]'. This protects against reserved keywords and
     * special characters in identifier names.
     */
    fun String.quoted(): String = "[${this.replace("]", "]]")}]"

    fun Field.sql(): String =
        if (type is MsSqlServerHierarchyFieldType) "${id.quoted()}.ToString()" else id.quoted()

    fun FromNode.sql(): String =
        when (this) {
            NoFrom -> ""
            is From -> {
                val ns = this.namespace
                if (ns == null) "FROM ${name.quoted()}" else "FROM ${ns.quoted()}.${name.quoted()}"
            }
            is FromSample -> {
                val ns = this.namespace
                if (sampleRateInv == 1L) {
                    if (ns == null) "FROM ${name.quoted()}"
                    else "FROM ${ns.quoted()}.${name.quoted()}"
                } else {
                    val tableName =
                        if (ns == null) name.quoted() else "${ns.quoted()}.${name.quoted()}"
                    val samplePercent = sampleRatePercentage.toPlainString()

                    "FROM (SELECT TOP $sampleSize * FROM $tableName TABLESAMPLE ($samplePercent PERCENT) ORDER BY NEWID()) AS randomly_sampled"
                }
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

    override val globalCursor: MetaField = MsSqlServerCdcMetaFields.CDC_CURSOR
    override val globalMetaFields: Set<MetaField> =
        setOf(
            CommonMetaField.CDC_UPDATED_AT,
            CommonMetaField.CDC_DELETED_AT,
            MsSqlServerCdcMetaFields.CDC_CURSOR,
            MsSqlServerCdcMetaFields.CDC_EVENT_SERIAL_NO,
            MsSqlServerCdcMetaFields.CDC_LSN,
        )

    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: ObjectNode,
    ) {
        recordData.set<JsonNode>(
            CommonMetaField.CDC_UPDATED_AT.id,
            CdcOffsetDateTimeMetaFieldType.jsonEncoder.encode(timestamp),
        )
        recordData.set<JsonNode>(
            MsSqlServerCdcMetaFields.CDC_LSN.id,
            CdcStringMetaFieldType.jsonEncoder.encode(""),
        )
        if (globalStateValue == null) {
            return
        }
        // For MSSQL, we would need to deserialize the state to get the LSN
        // This is a placeholder implementation - actual implementation would extract LSN from state
        try {
            val stateNode = globalStateValue["state"] as? ObjectNode
            if (stateNode != null) {
                val offsetNode = stateNode["mssql_cdc_offset"] as? ObjectNode
                if (offsetNode != null && offsetNode.size() > 0) {
                    // Extract LSN from the offset if available
                    val offsetValue = offsetNode.values().asSequence().first()
                    val lsn = Jsons.readTree(offsetValue.textValue())["commit_lsn"]?.asText()
                    if (lsn != null) {
                        recordData.set<JsonNode>(
                            MsSqlServerCdcMetaFields.CDC_LSN.id,
                            CdcStringMetaFieldType.jsonEncoder.encode(lsn),
                        )
                    }
                }
            }
        } catch (e: Exception) {
            log.warn(e) {
                "Failed to extract LSN from CDC state for stream ${stream.name}. Using empty LSN value."
            }
        }
    }

    @Suppress("UNCHECKED_CAST")
    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: NativeRecordPayload
    ) {
        // Add CDC_UPDATED_AT field
        recordData[CommonMetaField.CDC_UPDATED_AT.id] =
            FieldValueEncoder(
                timestamp,
                CommonMetaField.CDC_UPDATED_AT.type.jsonEncoder as JsonEncoder<Any>
            )

        // Add CDC_LSN field with empty string as default
        var lsnValue = ""

        if (globalStateValue != null) {
            // For MSSQL, extract the LSN from the state if available
            try {
                val stateNode = globalStateValue["state"] as? ObjectNode
                if (stateNode != null) {
                    val offsetNode = stateNode["mssql_cdc_offset"] as? ObjectNode
                    if (offsetNode != null && offsetNode.size() > 0) {
                        // Extract LSN from the offset if available
                        val offsetValue = offsetNode.values().asSequence().first()
                        val lsn = Jsons.readTree(offsetValue.textValue())["commit_lsn"]?.asText()
                        if (lsn != null) {
                            lsnValue = lsn
                        }
                    }
                }
            } catch (e: Exception) {
                log.warn(e) {
                    "Failed to extract LSN from CDC state for stream ${stream.name}. Using empty LSN value."
                }
            }
        }

        recordData[MsSqlServerCdcMetaFields.CDC_LSN.id] =
            FieldValueEncoder(
                lsnValue,
                MsSqlServerCdcMetaFields.CDC_LSN.type.jsonEncoder as JsonEncoder<Any>
            )
    }

    enum class MsSqlServerCdcMetaFields(override val type: FieldType) : MetaField {
        CDC_CURSOR(CdcIntegerMetaFieldType),
        CDC_LSN(CdcStringMetaFieldType),
        CDC_EVENT_SERIAL_NO(CdcStringMetaFieldType);

        override val id: String
            get() = MetaField.META_PREFIX + name.lowercase()
    }
}
