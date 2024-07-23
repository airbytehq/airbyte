/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres.typing_deduping

import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType
import io.airbyte.integrations.base.destination.typing_deduping.Array
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.Sql.Companion.concat
import io.airbyte.integrations.base.destination.typing_deduping.Sql.Companion.of
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.StreamId.Companion.concatenateRawTableName
import io.airbyte.integrations.base.destination.typing_deduping.Struct
import io.airbyte.protocol.models.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.v0.DestinationSyncMode
import java.util.*
import java.util.function.Function
import java.util.stream.Collectors
import java.util.stream.Stream
import org.jooq.Condition
import org.jooq.DataType
import org.jooq.Field
import org.jooq.Name
import org.jooq.SQLDialect
import org.jooq.impl.DSL
import org.jooq.impl.DefaultDataType
import org.jooq.impl.SQLDataType

class PostgresSqlGenerator(namingTransformer: NamingConventionTransformer, cascadeDrop: Boolean) :
    JdbcSqlGenerator(namingTransformer, cascadeDrop) {
    override fun buildStreamId(
        namespace: String,
        name: String,
        rawNamespaceOverride: String
    ): StreamId {
        // There is a mismatch between convention used in create table query in SqlOperations vs
        // this.
        // For postgres specifically, when a create table is issued without a quoted identifier, it
        // will be
        // converted to lowercase.
        // To keep it consistent when querying raw table in T+D query, convert it to lowercase.
        // TODO: This logic should be unified across Raw and final table operations in a single
        // class
        // operating on a StreamId.
        val streamName =
            namingTransformer
                .getIdentifier(concatenateRawTableName(namespace, name))
                .lowercase(Locale.getDefault())
        return StreamId(
            namingTransformer.getNamespace(namespace),
            namingTransformer.convertStreamName(name),
            namingTransformer.getNamespace(rawNamespaceOverride).lowercase(Locale.getDefault()),
            streamName,
            namespace,
            name
        )
    }

    override val structType: DataType<*>
        get() = JSONB_TYPE

    override val arrayType: DataType<*>
        get() = JSONB_TYPE

    override val widestType: DataType<*>
        get() = JSONB_TYPE

    override val dialect: SQLDialect
        get() = SQLDialect.POSTGRES

    override fun toDialectType(airbyteProtocolType: AirbyteProtocolType): DataType<*> {
        if (airbyteProtocolType == AirbyteProtocolType.STRING) {
            // https://www.postgresql.org/docs/current/datatype-character.html
            // If specified, the length n must be greater than zero and cannot exceed 10,485,760 (10
            // MB).
            // If you desire to store long strings with no specific upper limit,
            // use text or character varying without a length specifier,
            // rather than making up an arbitrary length limit.
            return SQLDataType.VARCHAR
        }
        return super.toDialectType(airbyteProtocolType)
    }

    override fun createTable(stream: StreamConfig, suffix: String, force: Boolean): Sql {
        val statements: MutableList<Sql> = ArrayList()
        val finalTableName = DSL.name(stream.id.finalNamespace, stream.id.finalName + suffix)

        statements.add(super.createTable(stream, suffix, force))

        if (stream.destinationSyncMode == DestinationSyncMode.APPEND_DEDUP) {
            // An index for our ROW_NUMBER() PARTITION BY pk ORDER BY cursor, extracted_at function
            val pkNames =
                stream.primaryKey.stream().map { pk: ColumnId -> DSL.quotedName(pk.name) }.toList()
            statements.add(
                of(
                    dslContext
                        .createIndex()
                        .on(
                            finalTableName,
                            Stream.of<Stream<Name>>(
                                    pkNames
                                        .stream(), // if cursor is present, then a stream containing
                                    // its name
                                    // but if no cursor, then empty stream
                                    stream.cursor.stream().map<Name> { cursor: ColumnId ->
                                        DSL.quotedName(cursor.name)
                                    },
                                    Stream.of<Name>(
                                        DSL.name(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT)
                                    )
                                )
                                .flatMap<Name>(Function.identity<Stream<Name>>())
                                .toList()
                        )
                        .sql
                )
            )
        }
        statements.add(
            of(
                dslContext
                    .createIndex()
                    .on(finalTableName, DSL.name(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT))
                    .getSQL()
            )
        )

        statements.add(
            of(
                dslContext
                    .createIndex()
                    .on(finalTableName, DSL.name(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID))
                    .getSQL()
            )
        )

        return concat(statements)
    }

    override fun extractRawDataFields(
        columns: LinkedHashMap<ColumnId, AirbyteType>,
        useExpensiveSaferCasting: Boolean
    ): MutableList<Field<*>> {
        return columns.entries
            .stream()
            .map { column: Map.Entry<ColumnId, AirbyteType> ->
                castedField(extractColumnAsJson(column.key), column.value, useExpensiveSaferCasting)
                    .`as`(column.key.name)
            }
            .collect(Collectors.toList())
    }

    override fun castedField(
        field: Field<*>,
        type: AirbyteType,
        useExpensiveSaferCasting: Boolean
    ): Field<*> {
        if (type is Struct) {
            // If this field is a struct, verify that the raw data is an object.
            return DSL.cast(
                DSL.case_()
                    .`when`(
                        field.isNull().or(jsonTypeof(field).ne("object")),
                        DSL.`val`(null as Any?)
                    )
                    .else_(field),
                JSONB_TYPE
            )
        } else if (type is Array) {
            // Do the same for arrays.
            return DSL.cast(
                DSL.case_()
                    .`when`(
                        field.isNull().or(jsonTypeof(field).ne("array")),
                        DSL.`val`(null as Any?)
                    )
                    .else_(field),
                JSONB_TYPE
            )
        } else if (type === AirbyteProtocolType.UNKNOWN) {
            return DSL.cast(field, JSONB_TYPE)
        } else if (type === AirbyteProtocolType.STRING) {
            // we need to render the jsonb to a normal string. For strings, this is the difference
            // between
            // "\"foo\"" and "foo".
            // postgres provides the #>> operator, which takes a json path and returns that
            // extraction as a
            // string.
            // '{}' is an empty json path (it's an empty array literal), so it just stringifies the
            // json value.
            return DSL.field("{0} #>> '{}'", String::class.java, field)
        } else {
            val dialectType = toDialectType(type)
            // jsonb can't directly cast to most types, so convert to text first.
            // also convert jsonb null to proper sql null.
            val extractAsText =
                DSL.case_()
                    .`when`(
                        field.isNull().or(jsonTypeof(field).eq("null")),
                        DSL.`val`(null as String?)
                    )
                    .else_(DSL.cast(field, SQLDataType.VARCHAR))
            return if (useExpensiveSaferCasting) {
                DSL.function(
                    DSL.name("pg_temp", "airbyte_safe_cast"),
                    dialectType,
                    extractAsText,
                    DSL.cast(DSL.`val`(null as Any?), dialectType)
                )
            } else {
                DSL.cast(extractAsText, dialectType)
            }
        }
    }

    protected override fun castedField(
        field: Field<*>,
        type: AirbyteProtocolType,
        useExpensiveSaferCasting: Boolean
    ): Field<*> {
        return DSL.cast(field, toDialectType(type))
    }

    private fun jsonBuildObject(vararg arguments: Field<*>): Field<*> {
        return DSL.function("JSONB_BUILD_OBJECT", JSONB_TYPE, *arguments)
    }

    override fun buildAirbyteMetaColumn(columns: LinkedHashMap<ColumnId, AirbyteType>): Field<*> {
        val dataFieldErrors =
            columns.entries
                .stream()
                .map { column: Map.Entry<ColumnId, AirbyteType> ->
                    toCastingErrorCaseStmt(column.key, column.value)
                }
                .toList()
        val rawTableChangesArray: Field<*> =
            DSL.field(
                "ARRAY(SELECT jsonb_array_elements_text({0}#>'{changes}'))::jsonb[]",
                DSL.field(DSL.name(JavaBaseConstants.COLUMN_NAME_AB_META))
            )

        // Jooq is inferring and casting as int[] for empty fields array call. So explicitly casting
        // it to
        // jsonb[] on empty array
        val finalTableChangesArray: Field<*> =
            if (dataFieldErrors.isEmpty()) DSL.field("ARRAY[]::jsonb[]")
            else
                DSL.function(
                    "ARRAY_REMOVE",
                    JSONB_TYPE,
                    DSL.array(dataFieldErrors).cast(JSONB_TYPE.arrayDataType),
                    DSL.`val`(null as String?)
                )
        return jsonBuildObject(
                DSL.`val`(AB_META_COLUMN_CHANGES_KEY),
                DSL.field("ARRAY_CAT({0}, {1})", finalTableChangesArray, rawTableChangesArray)
            )
            .`as`(JavaBaseConstants.COLUMN_NAME_AB_META)
    }

    private fun nulledChangeObject(fieldName: String): Field<*> {
        return jsonBuildObject(
            DSL.`val`(AB_META_CHANGES_FIELD_KEY),
            DSL.`val`(fieldName),
            DSL.`val`(AB_META_CHANGES_CHANGE_KEY),
            DSL.`val`(AirbyteRecordMessageMetaChange.Change.NULLED),
            DSL.`val`(AB_META_CHANGES_REASON_KEY),
            DSL.`val`(AirbyteRecordMessageMetaChange.Reason.DESTINATION_TYPECAST_ERROR)
        )
    }

    private fun toCastingErrorCaseStmt(column: ColumnId, type: AirbyteType): Field<Any> {
        val extract = extractColumnAsJson(column)
        // If this field is a struct, verify that the raw data is an object or null.
        // Do the same for arrays.
        return when (type) {
            is Struct ->
                DSL.field(
                    CASE_STATEMENT_SQL_TEMPLATE,
                    extract.isNotNull().and(jsonTypeof(extract).notIn("object", "null")),
                    nulledChangeObject(column.originalName),
                    DSL.cast(DSL.`val`(null as Any?), JSONB_TYPE)
                )
            is Array ->
                DSL.field(
                    CASE_STATEMENT_SQL_TEMPLATE,
                    extract.isNotNull().and(jsonTypeof(extract).notIn("array", "null")),
                    nulledChangeObject(column.originalName),
                    DSL.cast(DSL.`val`(null as Any?), JSONB_TYPE)
                )
            AirbyteProtocolType.STRING,
            AirbyteProtocolType.UNKNOWN -> DSL.cast(DSL.`val`(null as Any?), JSONB_TYPE)
            else ->
                DSL.field(
                    CASE_STATEMENT_SQL_TEMPLATE,
                    extract
                        .isNotNull()
                        .and(jsonTypeof(extract).ne("null"))
                        .and(castedField(extract, type, true).isNull()),
                    nulledChangeObject(column.originalName),
                    DSL.cast(DSL.`val`(null as Any?), JSONB_TYPE)
                )
        }
    }

    override fun cdcDeletedAtNotNullCondition(): Condition {
        return DSL.field(DSL.name(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT))
            .isNotNull()
            .and(jsonTypeof(extractColumnAsJson(cdcDeletedAtColumn)).ne("null"))
    }

    override fun getRowNumber(primaryKeys: List<ColumnId>, cursor: Optional<ColumnId>): Field<Int> {
        // literally identical to redshift's getRowNumber implementation, changes here probably
        // should
        // be reflected there
        val primaryKeyFields =
            if (primaryKeys != null)
                primaryKeys
                    .stream()
                    .map { columnId: ColumnId -> DSL.field(DSL.quotedName(columnId.name)) }
                    .collect(Collectors.toList())
            else ArrayList()
        val orderedFields: MutableList<Field<*>> = ArrayList()
        // We can still use Jooq's field to get the quoted name with raw sql templating.
        // jooq's .desc returns SortField<?> instead of Field<?> and NULLS LAST doesn't work with it
        cursor.ifPresent { columnId: ColumnId ->
            orderedFields.add(
                DSL.field("{0} desc NULLS LAST", DSL.field(DSL.quotedName(columnId.name)))
            )
        }
        orderedFields.add(
            DSL.field("{0} desc", DSL.quotedName(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT))
        )
        return DSL.rowNumber()
            .over()
            .partitionBy(primaryKeyFields)
            .orderBy(orderedFields)
            .`as`(ROW_NUMBER_COLUMN_NAME)
    }

    /** Extract a raw field, leaving it as jsonb */
    private fun extractColumnAsJson(column: ColumnId): Field<Any> {
        return DSL.field(
            "{0} -> {1}",
            DSL.name(JavaBaseConstants.COLUMN_NAME_DATA),
            DSL.`val`(column.originalName)
        )
    }

    private fun jsonTypeof(field: Field<*>): Field<String> {
        return DSL.function("JSONB_TYPEOF", SQLDataType.VARCHAR, field)
    }

    companion object {
        @JvmField
        val JSONB_TYPE: DataType<Any> =
            DefaultDataType(SQLDialect.POSTGRES, Any::class.java, "jsonb")

        const val CASE_STATEMENT_SQL_TEMPLATE: String = "CASE WHEN {0} THEN {1} ELSE {2} END "

        private const val AB_META_COLUMN_CHANGES_KEY = "changes"
        private const val AB_META_CHANGES_FIELD_KEY = "field"
        private const val AB_META_CHANGES_CHANGE_KEY = "change"
        private const val AB_META_CHANGES_REASON_KEY = "reason"
    }
}
