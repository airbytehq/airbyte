/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql.typing_deduping

import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType
import io.airbyte.integrations.base.destination.typing_deduping.Array
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.StreamId.Companion.concatenateRawTableName
import io.airbyte.integrations.base.destination.typing_deduping.Struct
import io.airbyte.integrations.destination.mysql.MySQLNameTransformer
import io.airbyte.protocol.models.v0.DestinationSyncMode
import java.time.Instant
import java.time.LocalDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeFormatterBuilder
import java.util.Locale
import java.util.Optional
import java.util.function.Function
import java.util.stream.Collectors
import java.util.stream.Collectors.toSet
import java.util.stream.Stream
import org.jooq.Condition
import org.jooq.DataType
import org.jooq.Field
import org.jooq.Name
import org.jooq.Param
import org.jooq.SQLDialect
import org.jooq.SortField
import org.jooq.conf.ParamType
import org.jooq.impl.DSL
import org.jooq.impl.DSL.cast
import org.jooq.impl.DSL.castNull
import org.jooq.impl.DSL.field
import org.jooq.impl.DSL.name
import org.jooq.impl.DSL.quotedName
import org.jooq.impl.DSL.sql
import org.jooq.impl.DSL.table
import org.jooq.impl.DefaultDataType
import org.jooq.impl.SQLDataType

class MysqlSqlGenerator : JdbcSqlGenerator(namingTransformer = MySQLNameTransformer()) {
    override val dialect = SQLDialect.MYSQL
    override val structType = JSON_TYPE
    override val arrayType = JSON_TYPE
    override val widestType = JSON_TYPE

    override fun buildStreamId(
        namespace: String,
        name: String,
        rawNamespaceOverride: String
    ): StreamId {
        // Wrap everything in getIdentifier() calls to truncate long names.
        // I don't understand why the MysqlNameTransformer doesn't call getIdentifier
        // in convertStreamName (or convertStreamName in getIdentifier?)
        // and those methods have so many uses that I don't feel confident in modifying them :/
        // so just call the truncate here, even though it's pretty gross.
        return StreamId(
            namingTransformer.getIdentifier(namingTransformer.getNamespace(namespace)),
            namingTransformer.getIdentifier(namingTransformer.convertStreamName(name)),
            namingTransformer.getIdentifier(namingTransformer.getNamespace(rawNamespaceOverride)),
            namingTransformer.getIdentifier(
                namingTransformer.convertStreamName(
                    concatenateRawTableName(namespace, name),
                ),
            ),
            namespace,
            name,
        )
    }

    override fun toDialectType(airbyteProtocolType: AirbyteProtocolType): DataType<*> {
        return when (airbyteProtocolType) {
            AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE -> SQLDataType.VARCHAR(1024)
            AirbyteProtocolType.TIME_WITH_TIMEZONE -> SQLDataType.VARCHAR(1024)
            AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE ->
                DefaultDataType(
                        null,
                        LocalDateTime::class.java,
                        "datetime",
                    )
                    .precision(6)
            AirbyteProtocolType.TIME_WITHOUT_TIMEZONE -> SQLDataType.TIME(6)
            AirbyteProtocolType.STRING -> SQLDataType.CLOB
            else -> super.toDialectType(airbyteProtocolType)
        }
    }

    override fun extractRawDataFields(
        columns: LinkedHashMap<ColumnId, AirbyteType>,
        useExpensiveSaferCasting: Boolean
    ): MutableList<Field<*>> {
        return columns.entries
            .stream()
            .map<Field<out Any>> { column: Map.Entry<ColumnId, AirbyteType> ->
                val type: AirbyteType = column.value
                val isStruct: Boolean = type is Struct
                val isArray: Boolean = type is Array

                var extractedValue: Field<*> = extractColumnAsJson(column.key)
                if (!(isStruct || isArray || (type === AirbyteProtocolType.UNKNOWN))) {
                    // Primitive types need to use JSON_VALUE to (a) strip quotes from strings, and
                    // (b) cast json null to sql null.
                    extractedValue =
                        DSL.function(
                            "JSON_VALUE",
                            String::class.java,
                            extractedValue,
                            DSL.`val`("$"),
                        )
                }
                if (isStruct) {
                    return@map DSL.case_()
                        .`when`<Any?>(
                            extractedValue
                                .isNull()
                                .or(
                                    DSL.function<String>(
                                            "JSON_TYPE",
                                            String::class.java,
                                            extractedValue,
                                        )
                                        .ne("OBJECT"),
                                ),
                            DSL.`val`<Any?>(null as Any?),
                        )
                        .else_(extractedValue)
                        .`as`(quotedName(column.key.name))
                } else if (isArray) {
                    return@map DSL.case_()
                        .`when`<Any?>(
                            extractedValue
                                .isNull()
                                .or(
                                    DSL.function<String>(
                                            "JSON_TYPE",
                                            String::class.java,
                                            extractedValue,
                                        )
                                        .ne("ARRAY"),
                                ),
                            DSL.`val`<Any?>(null as Any?),
                        )
                        .else_(extractedValue)
                        .`as`(quotedName(column.key.name))
                } else {
                    val castedValue: Field<*> =
                        castedField(extractedValue, type, useExpensiveSaferCasting)
                    if (type !is AirbyteProtocolType) {
                        return@map castedValue.`as`(quotedName(column.key.name))
                    }
                    return@map when (type) {
                        AirbyteProtocolType.TIME_WITH_TIMEZONE ->
                            DSL.case_()
                                .`when`<Any?>(
                                    castedValue.notLikeRegex(
                                        "^[0-9]{2}:[0-9]{2}:[0-9]{2}([.][0-9]+)?([-+][0-9]{2}(:?[0-9]{2})?|Z)$"
                                    ),
                                    DSL.`val`<Any?>(null as Any?),
                                )
                                .else_(castedValue)
                                .`as`(quotedName(column.key.name))
                        AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE ->
                            DSL.case_()
                                .`when`<Any?>(
                                    castedValue.notLikeRegex(
                                        "^[0-9]+-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}([.][0-9]+)?([-+][0-9]{2}(:?[0-9]{2})?|Z)$"
                                    ),
                                    DSL.`val`<Any?>(null as Any?),
                                )
                                .else_(castedValue)
                                .`as`(quotedName(column.key.name))
                        else -> castedValue.`as`(quotedName(column.key.name))
                    }
                }
            }
            .collect(Collectors.toList())
    }

    override fun castedField(
        field: Field<*>,
        type: AirbyteProtocolType,
        useExpensiveSaferCasting: Boolean
    ): Field<*> {
        return if (type == AirbyteProtocolType.BOOLEAN) {
            // for some reason, CAST('true' AS UNSIGNED) throws an error
            // so we manually build a case statement to do the string equality check
            DSL.case_() // The coerce just tells jooq that we're assuming `field` is a string value
                .`when`(field.coerce(String::class.java).eq(DSL.`val`("true")), DSL.`val`(true))
                .`when`(field.coerce(String::class.java).eq(DSL.`val`("false")), DSL.`val`(false))
                .else_(DSL.`val`(null as Boolean?))
        } else {
            cast(field, toDialectType(type))
        }
    }

    override fun createTable(stream: StreamConfig, suffix: String, force: Boolean): Sql {
        // jooq doesn't currently support creating indexes as part of a create table statement, even
        // though
        // mysql supports this. So we'll just create the indexes afterward.
        // Fortunately, adding indexes to an empty table is pretty cheap.
        val statements: MutableList<Sql> = ArrayList()
        val finalTableName: Name = name(stream.id.finalNamespace, stream.id.finalName + suffix)

        statements.add(super.createTable(stream, suffix, force))

        // jooq tries to autogenerate the name if you just do createIndex(), but it creates a
        // fully-qualified
        // name, which isn't valid mysql syntax.
        // mysql indexes only need to unique per-table, so we can just hardcode some names here.
        if (stream.destinationSyncMode === DestinationSyncMode.APPEND_DEDUP) {
            // An index for our ROW_NUMBER() PARTITION BY pk ORDER BY cursor, extracted_at function
            val indexColumns: List<Field<*>> =
                Stream.of(
                        stream.primaryKey.stream().map { pk ->
                            getIndexColumnField(
                                pk,
                                stream.columns[pk]!!,
                            )
                        }, // if cursor is present, then a stream containing its name
                        // but if no cursor, then empty stream
                        stream.cursor.stream().map { cursor ->
                            getIndexColumnField(
                                cursor,
                                stream.columns[cursor]!!,
                            )
                        },
                        Stream.of<Field<Any>>(
                            field(name(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT))
                        ),
                    )
                    .flatMap(Function.identity())
                    // Remove duplicates. It's theoretically possible for a stream to declare the
                    // PK and cursor to be the same column,
                    // and mysql complains if an index declares the same column twice.
                    .collect(toSet())
                    .toList()
            statements.add(
                Sql.of(
                    dslContext
                        .createIndex("dedup_idx")
                        .on(
                            table(finalTableName),
                            indexColumns,
                        )
                        .sql,
                ),
            )
        }
        statements.add(
            Sql.of(
                dslContext
                    .createIndex("extracted_at_idx")
                    .on(
                        finalTableName,
                        name(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT),
                    )
                    .sql,
            ),
        )

        statements.add(
            Sql.of(
                dslContext
                    .createIndex("raw_id_idx")
                    .on(
                        finalTableName,
                        name(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID),
                    )
                    .sql,
            ),
        )

        return Sql.concat(statements)
    }

    private fun getIndexColumnField(column: ColumnId, airbyteType: AirbyteType): Field<*> {
        // mysql restricts the total key length of an index, and our varchar/text columns alone
        // would
        // exceed that limit. So we restrict the index to only looking at the first 50 chars of
        // varchar/text columns.
        // jooq doesn't support this syntax, so we have to build it manually.
        val dialectType: DataType<*> = toDialectType(airbyteType)
        val typeName: String = dialectType.typeName
        if (
            "varchar".equals(typeName, ignoreCase = true) ||
                "text".equals(typeName, ignoreCase = true) ||
                "clob".equals(typeName, ignoreCase = true)
        ) {
            // this produces something like `col_name`(50)
            // so the overall create index statement is roughly
            // CREATE INDEX foo ON `the_table` (`col_name`(50), ...)
            val colDecl: String = dslContext.render(quotedName(column.name)) + "(" + 50 + ")"
            return field(sql(colDecl))
        } else {
            return field(quotedName(column.name))
        }
    }

    override fun buildAirbyteMetaColumn(columns: LinkedHashMap<ColumnId, AirbyteType>): Field<*> {
        // For now, mysql doesn't support safecast.
        // So we just pass through any existing entries in the meta column.
        // Use a sql literal because jooq's interface is being dumb about varargs in DSL.coalesce
        return field(
                sql(
                    """COALESCE(${JavaBaseConstants.COLUMN_NAME_AB_META}, CAST('{"changes":[]}' AS JSON))"""
                )
            )
            .`as`(JavaBaseConstants.COLUMN_NAME_AB_META)
    }

    override fun getFinalTableMetaColumns(
        includeMetaColumn: Boolean
    ): LinkedHashMap<String, DataType<*>> {
        val metaColumns: LinkedHashMap<String, DataType<*>> =
            super.getFinalTableMetaColumns(includeMetaColumn)
        // Override this column to be a TIMESTAMP instead of VARCHAR
        metaColumns[JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT] =
            SQLDataType.TIMESTAMP(6).nullable(false)
        return metaColumns
    }

    override fun cdcDeletedAtNotNullCondition(): Condition {
        return field(name(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT))
            .isNotNull()
            .and(jsonTypeof(extractColumnAsJson(cdcDeletedAtColumn)).ne("NULL"))
    }

    override fun getRowNumber(
        primaryKey: List<ColumnId>,
        cursorField: Optional<ColumnId>
    ): Field<Int> {
        val primaryKeyFields: List<Field<*>> =
            primaryKey
                .stream()
                .map { columnId: ColumnId ->
                    field(
                        quotedName(columnId.name),
                    )
                }
                .collect(Collectors.toList<Field<*>>())
        val orderedFields: MutableList<SortField<Any>> = ArrayList()
        // mysql DESC implicitly sorts nulls last, so we don't need to specify it explicitly
        cursorField.ifPresent { columnId: ColumnId ->
            orderedFields.add(
                field(quotedName(columnId.name)).desc(),
            )
        }
        orderedFields.add(
            field(quotedName(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT)).desc(),
        )
        return DSL.rowNumber()
            .over()
            .partitionBy(primaryKeyFields)
            .orderBy(orderedFields)
            .`as`(ROW_NUMBER_COLUMN_NAME)
    }

    override fun createSchema(schema: String): Sql {
        // Similar to all the other namespace-related stuff... create a database instead of schema.
        return Sql.of(dslContext.createDatabaseIfNotExists(quotedName(schema)).sql)
    }

    // as usual, "schema" is actually "database" in mysql land.
    override fun renameTable(schema: String, originalName: String, newName: String): String =
        dslContext
            .alterTable(name(schema, originalName))
            // mysql requires you to specify the target database name
            .renameTo(name(schema, newName))
            .sql

    // mysql doesn't support `create table (columnDecls...) AS select...`.
    // It only allows `create table AS select...`.
    override fun createV2RawTableFromV1Table(
        rawTableName: Name,
        namespace: String,
        tableName: String
    ) =
        dslContext
            .createTable(rawTableName)
            .`as`(
                DSL.select(
                        field(JavaBaseConstants.COLUMN_NAME_AB_ID)
                            .`as`(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID),
                        field(JavaBaseConstants.COLUMN_NAME_DATA)
                            .`as`(JavaBaseConstants.COLUMN_NAME_DATA),
                        field(JavaBaseConstants.COLUMN_NAME_EMITTED_AT)
                            .`as`(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT),
                        cast(null, timestampWithTimeZoneType)
                            .`as`(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT),
                        castNull(JSON_TYPE).`as`(JavaBaseConstants.COLUMN_NAME_AB_META),
                    )
                    .from(table(name(namespace, tableName))),
            )
            .getSQL(ParamType.INLINED)

    override fun formatTimestampLiteral(instant: Instant): String {
        return TIMESTAMP_FORMATTER.format(instant.atOffset(ZoneOffset.UTC))
    }

    private fun extractColumnAsJson(column: ColumnId): Field<Any> {
        return DSL.function(
            "JSON_EXTRACT",
            JSON_TYPE,
            field(name(JavaBaseConstants.COLUMN_NAME_DATA)),
            jsonPath(column),
        )
    }

    private fun jsonTypeof(field: Field<*>): Field<String> {
        return DSL.function("JSON_TYPE", SQLDataType.VARCHAR, field)
    }

    companion object {
        val JSON_TYPE: DefaultDataType<Any> =
            DefaultDataType(
                null,
                Any::class.java,
                "json",
            )

        val TIMESTAMP_FORMATTER: DateTimeFormatter =
            DateTimeFormatterBuilder()
                .append(DateTimeFormatter.ISO_LOCAL_DATE_TIME) // 2024-01-23T12:34:56
                .appendOffset("+HH:MM", "+00:00") // produce +00:00 instead of Z
                .toFormatter()

        private val MYSQL_TYPE_NAME_TO_JDBC_TYPE: Map<String, String> =
            ImmutableMap.of(
                "text",
                "clob",
                "bit",
                "boolean", // this is atrocious
                "datetime",
                "datetime(6)",
            )

        private fun jsonPath(column: ColumnId): Param<String> {
            // We wrap the name in doublequotes for special character handling, and then escape the
            // quoted string.
            // For example, let's say we have a column called f'oo"bar\baz
            // This translates to a json path $."f'oo\"bar\\baz"
            // jooq then renders it into a sql string, like '$."f\'oo\\"bar\\\\baz"'
            val escapedName: String =
                column.originalName.replace("\\", "\\\\").replace("\"", "\\\"")
            return DSL.`val`("$.\"$escapedName\"")
        }

        private fun jdbcTypeNameFromPostgresTypeName(mysqlType: String): String {
            return MYSQL_TYPE_NAME_TO_JDBC_TYPE.getOrDefault(
                mysqlType.lowercase(Locale.getDefault()),
                mysqlType.lowercase(
                    Locale.getDefault(),
                ),
            )
        }
    }
}
