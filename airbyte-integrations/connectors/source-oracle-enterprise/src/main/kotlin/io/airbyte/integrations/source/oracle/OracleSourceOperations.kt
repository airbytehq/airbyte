/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.oracle

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.CdcIntegerMetaFieldType
import io.airbyte.cdk.discover.CdcOffsetDateTimeMetaFieldType
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.JdbcAirbyteStreamFactory
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.discover.UserDefinedArray
import io.airbyte.cdk.discover.UserDefinedType
import io.airbyte.cdk.jdbc.ArrayFieldType
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.BigIntegerFieldType
import io.airbyte.cdk.jdbc.BinaryStreamFieldType
import io.airbyte.cdk.jdbc.BooleanFieldType
import io.airbyte.cdk.jdbc.ClobFieldType
import io.airbyte.cdk.jdbc.DoubleFieldType
import io.airbyte.cdk.jdbc.FloatFieldType
import io.airbyte.cdk.jdbc.JdbcFieldType
import io.airbyte.cdk.jdbc.JsonStringFieldType
import io.airbyte.cdk.jdbc.LocalDateTimeFieldType
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.jdbc.LosslessJdbcFieldType
import io.airbyte.cdk.jdbc.NClobFieldType
import io.airbyte.cdk.jdbc.NStringFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.PokemonFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.read.And
import io.airbyte.cdk.read.Equal
import io.airbyte.cdk.read.From
import io.airbyte.cdk.read.FromNode
import io.airbyte.cdk.read.FromSample
import io.airbyte.cdk.read.Greater
import io.airbyte.cdk.read.GreaterOrEqual
import io.airbyte.cdk.read.Lesser
import io.airbyte.cdk.read.LesserOrEqual
import io.airbyte.cdk.read.Limit
import io.airbyte.cdk.read.LimitNode
import io.airbyte.cdk.read.NoFrom
import io.airbyte.cdk.read.NoLimit
import io.airbyte.cdk.read.NoOrderBy
import io.airbyte.cdk.read.NoWhere
import io.airbyte.cdk.read.Or
import io.airbyte.cdk.read.OrderBy
import io.airbyte.cdk.read.OrderByNode
import io.airbyte.cdk.read.SelectColumnMaxValue
import io.airbyte.cdk.read.SelectColumns
import io.airbyte.cdk.read.SelectNode
import io.airbyte.cdk.read.SelectQuery
import io.airbyte.cdk.read.SelectQueryGenerator
import io.airbyte.cdk.read.SelectQuerySpec
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.Where
import io.airbyte.cdk.read.WhereClauseLeafNode
import io.airbyte.cdk.read.WhereClauseNode
import io.airbyte.cdk.read.WhereNode
import io.airbyte.cdk.read.cdc.ValidDebeziumWarmStartState
import io.airbyte.cdk.util.Jsons
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.time.OffsetDateTime

@Singleton
@Primary
class OracleSourceOperations :
    JdbcMetadataQuerier.FieldTypeMapper, SelectQueryGenerator, JdbcAirbyteStreamFactory {
    override fun toFieldType(c: JdbcMetadataQuerier.ColumnMetadata): FieldType =
        when (val type = c.type) {
            is SystemType -> leafType(c.type.typeName, type.scale != 0)
            is UserDefinedArray -> ArrayFieldType(recursiveArrayType(type))
            is UserDefinedType -> PokemonFieldType
        }

    private fun recursiveArrayType(type: UserDefinedArray): JdbcFieldType<*> =
        when (val elementType = type.elementType) {
            is SystemType -> {
                val leafType: JdbcFieldType<*> =
                    leafType(elementType.typeName, elementType.scale != 0)
                if (leafType == OffsetDateTimeFieldType) {
                    // Oracle's JDBC driver has a bug which prevents object conversions in
                    // ArrayDataResultSet instances. Fall back to strings instead.
                    PokemonFieldType
                } else {
                    leafType
                }
            }
            is UserDefinedArray -> ArrayFieldType(recursiveArrayType(elementType))
            is UserDefinedType -> PokemonFieldType
        }

    private fun leafType(
        typeName: String?,
        notInteger: Boolean,
    ): JdbcFieldType<*> =
        // This mapping includes literals returned by the JDBC driver as well as
        // *_TYPE_NAME column values from queries to ALL_* system tables.
        when (typeName) {
            "BINARY_FLOAT" -> FloatFieldType
            "BINARY_DOUBLE" -> DoubleFieldType
            "FLOAT",
            "DOUBLE PRECISION",
            "REAL", -> BigDecimalFieldType
            "NUMBER",
            "NUMERIC",
            "DECIMAL",
            "DEC", -> if (notInteger) BigDecimalFieldType else BigIntegerFieldType
            "INTEGER",
            "INT",
            "SMALLINT", -> BigIntegerFieldType
            "BOOLEAN",
            "BOOL", -> BooleanFieldType
            "CHAR",
            "VARCHAR2",
            "VARCHAR",
            "CHARACTER",
            "CHARACTER VARYING",
            "CHAR VARYING", -> StringFieldType
            "NCHAR",
            "NVARCHAR2",
            "NCHAR VARYING",
            "NATIONAL CHARACTER VARYING",
            "NATIONAL CHARACTER",
            "NATIONAL CHAR VARYING",
            "NATIONAL CHAR", -> NStringFieldType
            "BLOB" -> BinaryStreamFieldType
            "CLOB" -> ClobFieldType
            "NCLOB" -> NClobFieldType
            "BFILE" -> BinaryStreamFieldType
            "DATE" -> LocalDateTimeFieldType
            "INTERVALDS",
            "INTERVAL DAY TO SECOND",
            "INTERVALYM",
            "INTERVAL YEAR TO MONTH", -> StringFieldType
            "JSON" -> JsonStringFieldType
            "LONG",
            "LONG RAW",
            "RAW", -> BinaryStreamFieldType
            "TIMESTAMP",
            "TIMESTAMP WITH LOCAL TIME ZONE",
            "TIMESTAMP WITH LOCAL TZ", -> LocalDateTimeFieldType
            "TIMESTAMP WITH TIME ZONE",
            "TIMESTAMP WITH TZ", -> OffsetDateTimeFieldType
            else -> PokemonFieldType
        }

    override fun generate(ast: SelectQuerySpec): SelectQuery =
        SelectQuery(ast.sql(), ast.select.columns, ast.bindings())

    fun SelectQuerySpec.sql(): String {
        val components: List<String> = listOf(select.sql(), from.sql(), where.sql(), orderBy.sql())
        val sqlWithoutLimit: String = components.filter { it.isNotBlank() }.joinToString(" ")
        val rownumClause: String =
            when (limit) {
                NoLimit -> return sqlWithoutLimit
                Limit(0) -> "ROWNUM < 1"
                is Limit -> "ROWNUM <= ?"
            }
        return if (where == NoWhere && orderBy == NoOrderBy) {
            "$sqlWithoutLimit WHERE $rownumClause"
        } else {
            "${select.sql()} FROM ($sqlWithoutLimit) WHERE $rownumClause"
        }
    }

    fun SelectNode.sql(): String =
        "SELECT " +
            when (this) {
                is SelectColumns -> columns.joinToString(", ") { it.sql() }
                is SelectColumnMaxValue -> "MAX(${column.sql()})"
            }

    fun Field.sql(): String = "\"$id\""

    fun FromNode.sql(): String =
        when (this) {
            NoFrom -> "FROM DUAL"
            is From ->
                if (this.namespace == null) "FROM \"$name\"" else "FROM \"$namespace\".\"$name\""
            is FromSample -> {
                val sample: String =
                    if (sampleRateInv == 1L) {
                        ""
                    } else {
                        " SAMPLE(${sampleRatePercentage.toPlainString()})"
                    }
                val innerFrom: String = From(name, namespace).sql() + sample
                val inner = "SELECT * $innerFrom ORDER BY dbms_random.value"
                "FROM (SELECT * FROM ($inner) WHERE ROWNUM <= $sampleSize)"
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
            is GreaterOrEqual -> "${column.sql()} >= ?"
            is Greater -> "${column.sql()} > ?"
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
            Limit(0) -> listOf()
            is Limit -> listOf(SelectQuery.Binding(Jsons.numberNode(n), LongFieldType))
        }

    override val globalCursor: MetaField = OracleSourceCdcScn

    override val globalMetaFields: Set<MetaField> =
        setOf(OracleSourceCdcScn, CommonMetaField.CDC_UPDATED_AT, CommonMetaField.CDC_DELETED_AT)

    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: ObjectNode
    ) {
        recordData.set<JsonNode>(
            CommonMetaField.CDC_UPDATED_AT.id,
            CdcOffsetDateTimeMetaFieldType.jsonEncoder.encode(timestamp),
        )
        if (globalStateValue == null) {
            return
        }
        val debeziumState: ValidDebeziumWarmStartState =
            OracleSourceDebeziumOperations.deserializeStateInternal(globalStateValue)
        val position: OracleSourcePosition =
            OracleSourceDebeziumOperations.position(debeziumState.offset)
        recordData.set<JsonNode>(
            OracleSourceCdcScn.id,
            CdcIntegerMetaFieldType.jsonEncoder.encode(position.scn)
        )
    }
}
