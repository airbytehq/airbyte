package io.airbyte.integrations.destination.teradata.typing_deduping;

import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.Sql;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import org.jetbrains.annotations.NotNull;
import org.jooq.Condition;
import org.jooq.DSLContext;
import org.jooq.DataType;
import org.jooq.Field;
import org.jooq.Name;
import org.jooq.SQLDialect;
import org.jooq.conf.ParamType;
import org.jooq.impl.DSL;
import org.jooq.impl.DefaultDataType;
import org.jooq.impl.SQLDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.stream.Collectors;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_ID;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_META;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_RAW_ID;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_DATA;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_EMITTED_AT;
import static io.airbyte.integrations.base.destination.typing_deduping.Sql.separately;
import static io.airbyte.integrations.base.destination.typing_deduping.Sql.transactionally;
import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.inline;
import static org.jooq.impl.DSL.name;
import static org.jooq.impl.DSL.quotedName;
import static org.jooq.impl.DSL.rowNumber;

public class TeradataSqlGenerator extends JdbcSqlGenerator {
    private static final String NUMBERED_ROWS_CTE_ALIAS = "numbered_rows";
    private static final String TYPING_CTE_ALIAS = "intermediate_data";
    public static final DataType<Object> JSON_TYPE = new DefaultDataType<>(SQLDialect.DEFAULT, Object.class, "JSON");
    private static final Logger log = LoggerFactory.getLogger(TeradataSqlGenerator.class);

    public TeradataSqlGenerator(@NotNull NamingConventionTransformer namingTransformer, boolean cascadeDrop) {
        super(namingTransformer, cascadeDrop);
    }

    @NotNull
    @Override
    protected DataType<?> getStructType() {
        return JSON_TYPE;
    }

    @NotNull
    @Override
    protected DataType<?> getArrayType() {
        return JSON_TYPE;
    }

    @NotNull
    @Override
    protected DataType<?> getWidestType() {
        return JSON_TYPE;
    }

    @NotNull
    @Override
    protected SQLDialect getDialect() {
        return SQLDialect.DEFAULT;
    }

    @NotNull
    @Override
    protected List<Field<?>> extractRawDataFields(@NotNull LinkedHashMap<ColumnId, AirbyteType> columns, boolean useExpensiveSaferCasting) {
        List<Field<?>> fields = new ArrayList<>();

        columns.forEach((key, value) -> {
                    if (value.equals(AirbyteProtocolType.UNKNOWN) || value.getTypeName().equals("STRUCT") || value.getTypeName().equals("ARRAY")) {
                        fields.add(
                                field("cast(" + name(COLUMN_NAME_DATA) + ".JSONExtract('$." + field(key.getOriginalName()) + "') as " + toDialectType(value) + ")").as(key.getName())
                        );
                    } else if (value.equals(AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE)) {
                        fields.add(
                                field("case when " + name(COLUMN_NAME_DATA) + ".JSONExtractValue('$." + field(key.getOriginalName()) + "') like any ('%__:__', '%Z') then cast("
                                        + name(COLUMN_NAME_DATA) + ".JSONExtractValue('$." + field(key.getOriginalName()) + "') as " + toDialectType(value) + ") else TO_TIMESTAMP_TZ("
                                        + name(COLUMN_NAME_DATA) + ".JSONExtractValue('$." + field(key.getOriginalName()) + "'), 'YYYY-MM-DD\"T\"HH24:MI:SSTZHTZM') end ").as(key.getName())
                        );
                    } else if (value.equals(AirbyteProtocolType.TIME_WITH_TIMEZONE)) {
                        fields.add(
                                field("case when " + name(COLUMN_NAME_DATA) + ".JSONExtractValue('$." + field(key.getOriginalName()) + "') like any ('%__:__', '%Z') then cast("
                                        + name(COLUMN_NAME_DATA) + ".JSONExtractValue('$." + field(key.getOriginalName()) + "') as " + toDialectType(value) + ") else cast(TO_TIMESTAMP_TZ("
                                        + name(COLUMN_NAME_DATA) + ".JSONExtractValue('$." + field(key.getOriginalName()) + "'), 'HH24:MI:SSTZHTZM') as " + toDialectType(value)
                                        + ") end ").as(key.getName())
                        );
                    } else if (value.equals(AirbyteProtocolType.STRING)) {
                        fields.add(
                                field("case when "
                                        + "cast(" + name(COLUMN_NAME_DATA) + ".JSONExtract('$." + field(key.getOriginalName()) + ".*') as " + toDialectType(value) + ") is not null "
                                        + "then SUBSTRING(cast(" + name(COLUMN_NAME_DATA) + ".JSONExtract('$." + field(key.getOriginalName()) + "') as " + toDialectType(value) + ") FROM 2 FOR LENGTH (cast(" + name(COLUMN_NAME_DATA) + ".JSONExtract('$." + field(key.getOriginalName()) + "') as " + toDialectType(value) + "))" + "-2) "
                                        + "else cast(" + name(COLUMN_NAME_DATA) + ".JSONExtractValue('$." + field(key.getOriginalName()) + "') as " + toDialectType(value) + ") END").as(key.getName())
                        );
                    } else {
                        fields.add(
                                field("cast(" + name(COLUMN_NAME_DATA) + ".JSONExtractValue('$." + field(key.getOriginalName()) + "') as " + toDialectType(value) + ")").as(key.getName())
                        );
                    }
                }
        );
        return fields;
    }

    @NotNull
    @Override
    protected Field<?> buildAirbyteMetaColumn(@NotNull LinkedHashMap<ColumnId, AirbyteType> columns) {
        return inline("{}").as(COLUMN_NAME_AB_META);
    }

    @Override
    protected Condition cdcDeletedAtNotNullCondition() {
        return field(name(COLUMN_NAME_AB_LOADED_AT)).isNotNull()
                .and(extractColumnAsJson(getCdcDeletedAtColumn()).notEqual("null"));
    }

    private Field<Object> extractColumnAsJson(final ColumnId column) {

        return field("cast(" + field(name(COLUMN_NAME_DATA) + ".JSONExtract('$." + field(column.getOriginalName()) + "') as VARCHAR(100)") + ")");
    }

    @NotNull
    @Override
    protected Field<Integer> getRowNumber(@NotNull List<ColumnId> primaryKeys, @NotNull Optional<ColumnId> cursor) {
        // literally identical to redshift's getRowNumber implementation, changes here probably should
        // be reflected there
        final List<Field<?>> primaryKeyFields =
                primaryKeys.stream().map(columnId -> field(quotedName(columnId.getName()))).collect(Collectors.toList());
        final List<Field<?>> orderedFields = new ArrayList<>();
        // We can still use Jooq's field to get the quoted name with raw sql templating.
        // jooq's .desc returns SortField<?> instead of Field<?> and NULLS LAST doesn't work with it
        cursor.ifPresent(columnId -> orderedFields.add(field("{0} desc NULLS LAST", field(quotedName(columnId.getName())))));
        orderedFields.add(field("{0} desc", quotedName(COLUMN_NAME_AB_EXTRACTED_AT)));
        return rowNumber()
                .over()
                .partitionBy(primaryKeyFields)
                .orderBy(orderedFields).as(ROW_NUMBER_COLUMN_NAME);
    }

    @Override
    public @NotNull DataType<?> toDialectType(AirbyteProtocolType airbyteProtocolType) {
        if (airbyteProtocolType.equals(AirbyteProtocolType.STRING)) {
            return SQLDataType.VARCHAR.length(1000);
        } else if (airbyteProtocolType.equals(AirbyteProtocolType.BOOLEAN)) {
            return SQLDataType.VARCHAR.length(5);
        } else if (airbyteProtocolType.equals(AirbyteProtocolType.INTEGER)) {
            return SQLDataType.INTEGER;
        } else if (airbyteProtocolType.equals(AirbyteProtocolType.NUMBER)) {
            return SQLDataType.FLOAT;
        }
        return super.toDialectType(airbyteProtocolType);
    }

    @Override
    public @NotNull Sql createTable(final @NotNull StreamConfig stream, final @NotNull String suffix, final boolean force) {
        String finalTableIdentifier = stream.getId().getFinalName() + suffix.toLowerCase(Locale.getDefault());

        if (!force) {
            return separately(
                    createTableSql(stream.getId().getFinalNamespace(), finalTableIdentifier, stream.getColumns())
            );
        }

        return separately(
                String.format("DROP TABLE %s.%s;", stream.getId().getFinalNamespace(), finalTableIdentifier),
                createTableSql(stream.getId().getFinalNamespace(), finalTableIdentifier, stream.getColumns())
        );
    }

    @Override
    protected @NotNull String createTableSql(@NotNull String namespace, @NotNull String tableName, @NotNull LinkedHashMap<ColumnId, AirbyteType> columns) {
        DSLContext dsl = getDslContext();
        String createTableSql = dsl.createTable(DSL.name(namespace, tableName))
                .columns(buildFinalTableFields(columns, getFinalTableMetaColumns(true)))
                .getSQL();
        log.info("CreateTableSQL: {}", createTableSql);
        return addMultisetKeyword(createTableSql);
    }

    private String addMultisetKeyword(String createQuery) {
        int createIndex = createQuery.toUpperCase().indexOf("CREATE");
        if (createIndex == -1) {
            // 'CREATE' keyword not found
            return createQuery;
        }
        int endIndex = createIndex + 6; // length of 'CREATE' keyword
        String beforeCreate = createQuery.substring(0, endIndex);
        String afterCreate = createQuery.substring(endIndex);

        return beforeCreate + " MULTISET " + afterCreate + " NO PRIMARY INDEX";
    }

    //TODO: Check with parten implementation if something is missing
    @Override
    public @NotNull Sql overwriteFinalTable(StreamId stream, @NotNull String finalSuffix) {
        String spaceName = stream.getFinalNamespace();
        String tableName = stream.getFinalName() + finalSuffix;
        String newTableName = stream.getFinalName();


        return separately(
                String.format("DROP TABLE %s.%s;", spaceName, newTableName),
                String.format("RENAME TABLE %s.%s TO %s.%s;", spaceName, tableName, spaceName, newTableName)
        );
    }

    @Override
    public @NotNull Sql migrateFromV1toV2(StreamId streamId, @NotNull String namespace, @NotNull String tableName) {
        log.info("namespace: {}, tablename: {}", namespace, tableName);
        log.info("stream id namespace: {}, stream id tablename: {}", streamId.getRawNamespace(), streamId.getRawName());
        var rawTableName = DSL.name(streamId.getRawNamespace(), streamId.getRawName());
        return transactionally(
                createV2RawTableFromV1Table(rawTableName, namespace, tableName)
        );
    }

    @Override
    public @NotNull String createV2RawTableFromV1Table(@NotNull Name rawTableName, @NotNull String namespace, @NotNull String tableName) {
        String query = String.format("CREATE TABLE %s AS ( SELECT %s %s, %s %s, CAST(NULL AS TIMESTAMP WITH TIME ZONE) %s, %s %s, CAST(NULL AS JSON) %s FROM %s.%s) WITH DATA", rawTableName, COLUMN_NAME_AB_ID, COLUMN_NAME_AB_RAW_ID, COLUMN_NAME_EMITTED_AT, COLUMN_NAME_AB_EXTRACTED_AT, COLUMN_NAME_AB_LOADED_AT, COLUMN_NAME_DATA, COLUMN_NAME_DATA, COLUMN_NAME_AB_META, namespace, tableName);
        log.info("create createV2RawTableFromV1Table: {}", query);
        return query;
    }

    @NotNull
    @Override
    public Sql createSchema(@NotNull String schema) {
        return Sql.of(String.format("CREATE DATABASE \"%s\" AS PERMANENT = 120e6, SPOOL = 120e6;", schema));
    }

    @Override
    protected Sql insertAndDeleteTransaction(
            StreamConfig streamConfig,
            String finalSuffix,
            Optional<Instant> minRawTimestamp,
            boolean useExpensiveSaferCasting
    ) {
        String finalSchema = streamConfig.getId().getFinalNamespace();
        String finalTable = streamConfig.getId().getFinalName() +
                (finalSuffix != null ? finalSuffix.toLowerCase(Locale.getDefault()) : "");
        String rawSchema = streamConfig.getId().getRawNamespace();
        String rawTable = streamConfig.getId().getRawName();

        // Poor person's guarantee of ordering of fields by using same source of ordered list of
        // columns to
        // generate fields.
        var rawTableRowsWithCast =
                DSL.name(TYPING_CTE_ALIAS).as(
                        selectFromRawTable(
                                rawSchema,
                                rawTable,
                                streamConfig.getColumns(),
                                getFinalTableMetaColumns(false),
                                rawTableCondition(
                                        streamConfig.getDestinationSyncMode(),
                                        streamConfig.getColumns().containsKey(getCdcDeletedAtColumn()),
                                        minRawTimestamp
                                ),
                                useExpensiveSaferCasting
                        )
                );

        List<Field<?>> finalTableFields = buildFinalTableFields(
                streamConfig.getColumns(),
                getFinalTableMetaColumns(true)
        );

        Field<Integer> rowNumber = getRowNumber(
                streamConfig.getPrimaryKey(),
                streamConfig.getCursor()
        );

        var filteredRows =
                DSL.name(NUMBERED_ROWS_CTE_ALIAS).as(
                        DSL.select(finalTableFields)
                                .select(rowNumber)
                                .from(rawTableRowsWithCast)
                );

        // Used for append-dedupe mode.
        String insertStmtWithDedupe =
                insertIntoFinalTable(
                        finalSchema,
                        finalTable,
                        streamConfig.getColumns(),
                        getFinalTableMetaColumns(true)
                )
                        .select(
                                DSL.with(rawTableRowsWithCast)
                                        .with(filteredRows)
                                        .select(finalTableFields)
                                        .from(filteredRows)
                                        .where(DSL.field(DSL.name(ROW_NUMBER_COLUMN_NAME), Integer.class).eq(1))
                        )
                        .getSQL(ParamType.INLINED);

        // Used for append and overwrite modes.
        String insertStmt =
                insertIntoFinalTable(
                        finalSchema,
                        finalTable,
                        streamConfig.getColumns(),
                        getFinalTableMetaColumns(true)
                )
                        .select(
                                DSL.with(rawTableRowsWithCast)
                                        .select(finalTableFields)
                                        .from(rawTableRowsWithCast)
                        )
                        .getSQL(ParamType.INLINED);

        String deleteStmt = deleteFromFinalTable(
                finalSchema,
                finalTable,
                streamConfig.getPrimaryKey(),
                streamConfig.getCursor()
        );

        String deleteCdcDeletesStmt = streamConfig.getColumns().containsKey(getCdcDeletedAtColumn())
                ? deleteFromFinalTableCdcDeletes(finalSchema, finalTable)
                : "";

        String checkpointStmt = checkpointRawTable(rawSchema, rawTable, minRawTimestamp);

        if (streamConfig.getDestinationSyncMode() != DestinationSyncMode.APPEND_DEDUP) {
            return transactionally(insertStmt, checkpointStmt);
        }

        // For append-dedupe
        return transactionally(
                insertStmtWithDedupe,
                deleteStmt,
                deleteCdcDeletesStmt,
                checkpointStmt
        );
    }
}
