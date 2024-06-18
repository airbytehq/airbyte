/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType
import io.airbyte.integrations.base.destination.typing_deduping.Array
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId
import io.airbyte.integrations.base.destination.typing_deduping.Struct
import io.airbyte.integrations.base.destination.typing_deduping.Union
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf
import io.airbyte.integrations.destination.redshift.constants.RedshiftDestinationConstants
import io.airbyte.protocol.models.AirbyteRecordMessageMetaChange
import java.sql.Timestamp
import java.util.*
import java.util.stream.Collectors
import org.jooq.Condition
import org.jooq.DataType
import org.jooq.Field
import org.jooq.SQLDialect
import org.jooq.impl.DSL
import org.jooq.impl.SQLDataType

open class RedshiftSqlGenerator(
    namingTransformer: NamingConventionTransformer,
    private val dropCascade: Boolean
) : JdbcSqlGenerator(namingTransformer, dropCascade) {
    constructor(
        namingTransformer: NamingConventionTransformer,
        config: JsonNode
    ) : this(namingTransformer, isDropCascade(config))

    private val superType: DataType<*>
        /**
         * This method returns Jooq internal DataType, Ideally we need to implement DataType
         * interface with all the required fields for Jooq typed query construction
         *
         * @return
         */
        get() = RedshiftDestinationConstants.SUPER_TYPE

    override val structType: DataType<*>
        get() = superType

    override val arrayType: DataType<*>
        get() = superType

    override val widestType: DataType<*>
        get() = superType

    override val dialect: SQLDialect
        get() = SQLDialect.POSTGRES

    /**
     * Notes about Redshift specific SQL * 16MB Limit on the total size of the SQL sent in a session
     * * Default mode of casting within SUPER is lax mode, to enable strict use SET
     * cast_super_null_on_error='OFF'; * *
     * https://docs.aws.amazon.com/redshift/latest/dg/super-configurations.html *
     * https://docs.aws.amazon.com/redshift/latest/dg/r_MERGE.html#r_MERGE_usage_notes * * (Cannot
     * use WITH clause in MERGE statement).
     * https://cloud.google.com/bigquery/docs/migration/redshift-sql#merge_statement * *
     * https://docs.aws.amazon.com/redshift/latest/dg/r_WITH_clause.html#r_WITH_clause-usage-notes *
     * Primary keys are informational only and not enforced
     * (https://docs.aws.amazon.com/redshift/latest/dg/t_Defining_constraints.html) TODO: Look at
     * SORT KEYS, DISTKEY in redshift for optimizing the query performance.
     */
    override fun castedField(
        field: Field<*>,
        type: AirbyteType,
        useExpensiveSaferCasting: Boolean
    ): Field<*> {
        if (type is AirbyteProtocolType) {
            return when (type) {
                AirbyteProtocolType.STRING -> {
                    DSL.field(
                        CASE_STATEMENT_SQL_TEMPLATE,
                        jsonTypeOf(field).ne("string").and(field.isNotNull()),
                        jsonSerialize(field),
                        castedField(field, type, useExpensiveSaferCasting)
                    )
                }
                else -> {
                    castedField(field, type, useExpensiveSaferCasting)
                }
            }
        }
        // Redshift SUPER can silently cast an array type to struct and vice versa.
        return when (type.typeName) {
            Struct.TYPE,
            UnsupportedOneOf.TYPE ->
                DSL.field(
                    CASE_STATEMENT_NO_ELSE_SQL_TEMPLATE,
                    jsonTypeOf(field).eq("object"),
                    DSL.cast(field, structType)
                )
            Array.TYPE ->
                DSL.field(
                    CASE_STATEMENT_NO_ELSE_SQL_TEMPLATE,
                    jsonTypeOf(field).eq("array"),
                    DSL.cast(field, arrayType)
                )
            Union.TYPE -> castedField(field, (type as Union).chooseType(), useExpensiveSaferCasting)
            else -> throw IllegalArgumentException("Unsupported AirbyteType: $type")
        }
    }

    override fun extractRawDataFields(
        columns: LinkedHashMap<ColumnId, AirbyteType>,
        useExpensiveSaferCasting: Boolean
    ): MutableList<Field<*>> {
        return columns.entries
            .stream()
            .map { column: Map.Entry<ColumnId, AirbyteType> ->
                castedField(
                        DSL.field(
                            DSL.quotedName(
                                JavaBaseConstants.COLUMN_NAME_DATA,
                                column.key.originalName
                            )
                        ),
                        column.value,
                        useExpensiveSaferCasting
                    )
                    .`as`(column.key.name)
            }
            .collect(Collectors.toList<Field<*>>())
    }

    private fun jsonTypeOf(field: Field<*>): Field<String> {
        return DSL.function("JSON_TYPEOF", SQLDataType.VARCHAR, field)
    }

    private fun jsonSerialize(field: Field<*>): Field<String> {
        return DSL.function("JSON_SERIALIZE", SQLDataType.VARCHAR, field)
    }

    /**
     * Redshift ARRAY_CONCAT supports only 2 arrays. Iteratively nest ARRAY_CONCAT to support more
     * than 2
     *
     * @param arrays
     * @return
     */
    fun arrayConcatStmt(arrays: List<Field<*>?>): Field<*>? {
        if (arrays.isEmpty()) {
            return DSL.field("ARRAY()") // Return an empty string if the list is empty
        }

        var result = arrays[0]
        for (i in 1 until arrays.size) {
            // We lose some nice indentation but thats ok. Queryparts
            // are intentionally rendered here to avoid deep stack for function sql rendering.
            result =
                DSL.field(
                    dslContext.renderNamedOrInlinedParams(
                        DSL.function("ARRAY_CONCAT", superType, result, arrays[i])
                    )
                )
        }
        return result
    }

    fun toCastingErrorCaseStmt(column: ColumnId, type: AirbyteType): Field<*> {
        val field: Field<*> =
            DSL.field(DSL.quotedName(JavaBaseConstants.COLUMN_NAME_DATA, column.originalName))
        // Just checks if data is not null but casted data is null. This also accounts for
        // conditional
        // casting result of array and struct.
        // TODO: Timestamp format issues can result in null values when cast, add regex check if
        // destination
        // supports regex functions.
        return DSL.field(
            CASE_STATEMENT_SQL_TEMPLATE,
            field.isNotNull().and(castedField(field, type, true).`as`(column.name).isNull()),
            DSL.function(
                "ARRAY",
                superType,
                DSL.function(
                    "JSON_PARSE",
                    superType,
                    DSL.`val`(
                        "{\"field\": \"" +
                            column.name +
                            "\", " +
                            "\"change\": \"" +
                            AirbyteRecordMessageMetaChange.Change.NULLED.value() +
                            "\", " +
                            "\"reason\": \"" +
                            AirbyteRecordMessageMetaChange.Reason.DESTINATION_TYPECAST_ERROR +
                            "\"}"
                    )
                )
            ),
            DSL.field("ARRAY()")
        )
    }

    override fun buildAirbyteMetaColumn(columns: LinkedHashMap<ColumnId, AirbyteType>): Field<*> {
        val dataFields =
            columns.entries
                .stream()
                .map { column: Map.Entry<ColumnId, AirbyteType> ->
                    toCastingErrorCaseStmt(column.key, column.value)
                }
                .collect(Collectors.toList())
        val rawTableAirbyteMetaExists: Condition =
            DSL.field(DSL.quotedName(JavaBaseConstants.COLUMN_NAME_AB_META))
                .isNotNull()
                .and(
                    DSL.function<Boolean>(
                        "IS_OBJECT",
                        SQLDataType.BOOLEAN,
                        DSL.field(DSL.quotedName(JavaBaseConstants.COLUMN_NAME_AB_META))
                    )
                )
                .and(
                    DSL.field(
                            DSL.quotedName(
                                JavaBaseConstants.COLUMN_NAME_AB_META,
                                AIRBYTE_META_COLUMN_CHANGES_KEY
                            )
                        )
                        .isNotNull()
                )
                .and(
                    DSL.function<Boolean>(
                        "IS_ARRAY",
                        SQLDataType.BOOLEAN,
                        DSL.field(
                            DSL.quotedName(
                                JavaBaseConstants.COLUMN_NAME_AB_META,
                                AIRBYTE_META_COLUMN_CHANGES_KEY
                            )
                        )
                    )
                )
        val airbyteMetaChangesArray =
            DSL.function(
                "ARRAY_CONCAT",
                superType,
                arrayConcatStmt(dataFields),
                DSL.field(
                    CASE_STATEMENT_SQL_TEMPLATE,
                    rawTableAirbyteMetaExists,
                    DSL.field(
                        DSL.quotedName(
                            JavaBaseConstants.COLUMN_NAME_AB_META,
                            AIRBYTE_META_COLUMN_CHANGES_KEY
                        )
                    ),
                    DSL.field("ARRAY()")
                )
            )
        return DSL.function(
                "OBJECT",
                superType,
                DSL.`val`(AIRBYTE_META_COLUMN_CHANGES_KEY),
                airbyteMetaChangesArray
            )
            .`as`(JavaBaseConstants.COLUMN_NAME_AB_META)
    }

    /**
     * Return ROW_NUMBER() OVER (PARTITION BY primaryKeys ORDER BY cursor DESC NULLS LAST,
     * _airbyte_extracted_at DESC)
     *
     * @param primaryKeys
     * @param cursor
     * @return
     */
    override fun getRowNumber(primaryKeys: List<ColumnId>, cursor: Optional<ColumnId>): Field<Int> {
        // literally identical to postgres's getRowNumber implementation, changes here probably
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

    override fun cdcDeletedAtNotNullCondition(): Condition {
        return DSL.field(DSL.name(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT))
            .isNotNull()
            .and(
                DSL.function<String>(
                        "JSON_TYPEOF",
                        SQLDataType.VARCHAR,
                        DSL.field(
                            DSL.quotedName(
                                JavaBaseConstants.COLUMN_NAME_DATA,
                                cdcDeletedAtColumn.name
                            )
                        )
                    )
                    .ne("null")
            )
    }

    override fun currentTimestamp(): Field<Timestamp> {
        return DSL.function("GETDATE", SQLDataType.TIMESTAMP)
    }

    override fun shouldRetry(e: Exception?): Boolean {
        return false
    }

    companion object {
        const val CASE_STATEMENT_SQL_TEMPLATE: String = "CASE WHEN {0} THEN {1} ELSE {2} END "
        const val CASE_STATEMENT_NO_ELSE_SQL_TEMPLATE: String = "CASE WHEN {0} THEN {1} END "

        private const val AIRBYTE_META_COLUMN_CHANGES_KEY = "changes"

        private fun isDropCascade(config: JsonNode): Boolean {
            val dropCascadeNode = config[RedshiftDestinationConstants.DROP_CASCADE_OPTION]
            return dropCascadeNode != null && dropCascadeNode.asBoolean()
        }
    }
}
