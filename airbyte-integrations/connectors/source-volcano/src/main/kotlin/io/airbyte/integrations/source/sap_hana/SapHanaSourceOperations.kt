/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.sap_hana

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.*
import io.airbyte.cdk.jdbc.*
import io.airbyte.cdk.read.*
import io.airbyte.cdk.util.Jsons
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.time.OffsetDateTime

@Singleton
@Primary
class SapHanaSourceOperations :
    JdbcMetadataQuerier.FieldTypeMapper, SelectQueryGenerator, JdbcAirbyteStreamFactory {

    override fun toFieldType(c: JdbcMetadataQuerier.ColumnMetadata): FieldType =
        when (val type = c.type) {
            is SystemType -> leafType(type)
            else -> PokemonFieldType
        }

    private fun leafType(type: SystemType): JdbcFieldType<*> {
        // This mapping includes literals returned by the JDBC driver as well as
        // *_TYPE_NAME column values from queries to ALL_* system tables.
        return when (type.typeName) {
            "BINARY_FLOAT" -> FloatFieldType
            "BINARY_DOUBLE" -> DoubleFieldType
            "FLOAT",
            "DOUBLE PRECISION",
            "REAL", -> BigDecimalFieldType
            "NUMBER",
            "NUMERIC",
            "DECIMAL",
            "DEC", -> BigDecimalFieldType
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
    }

    override fun generate(ast: SelectQuerySpec): SelectQuery =
        SelectQuery(ast.sql(), ast.select.columns, ast.bindings())

    fun SelectQuerySpec.sql(): String {
        val components: List<String> = listOf(select.sql(), from.sql(), where.sql(), orderBy.sql())
        val sqlWithoutLimit: String = components.filter { it.isNotBlank() }.joinToString(" ")
        val limitClause: String =
            when (limit) {
                NoLimit -> return sqlWithoutLimit
                Limit(0) -> "LIMIT 0"
                is Limit -> "LIMIT ?"
            }
        return "$sqlWithoutLimit $limitClause"
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
            NoFrom -> "FROM DUMMY"
            is From ->
                if (this.namespace == null) "FROM \"$name\"" else "FROM \"$namespace\".\"$name\""
            is FromSample -> {
                val sample: String =
                    if (sampleRateInv == 1L) {
                        ""
                    } else {
                        " TABLESAMPLE BERNOULLI (${sampleRatePercentage.toPlainString()})"
                    }
                val innerFrom: String = From(name, namespace).sql() + sample
                "FROM (SELECT * $innerFrom LIMIT $sampleSize)"
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

    override val globalCursor: MetaField? = null

    override val globalMetaFields: Set<MetaField> = emptySet()

    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: ObjectNode
    ) {
        return
    }
}
