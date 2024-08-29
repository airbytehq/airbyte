package io.airbyte.integrations.destination.teradata.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.Array;
import io.airbyte.integrations.base.destination.typing_deduping.Sql;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.Struct;
import io.airbyte.integrations.base.destination.typing_deduping.Union;
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import org.jetbrains.annotations.NotNull;
import org.jooq.SQLDialect;
import org.jooq.conf.ParamType;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.stream.Collectors;

import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.quotedName;
import static org.jooq.impl.DSL.table;

/**
 * Orchestration class handling init, write, and reset of the destination write process.
 * See MysqlDestinationHandler.kt for an example child class and JdbcDestinationHandler for the abstract implementation
 * <p>
 * TODO: override/implement whatever necessary from the parent class to make integration tests pass
 */
public class TeradataDestinationHandler extends JdbcDestinationHandler<MinimumDestinationState> {
    private final static String DESTINATION_STATE_TABLE_COLUMN_STATE = "destination_state";
    private final static String DESTINATION_STATE_TABLE_COLUMN_UPDATED_AT = "updated_at";
    private final Logger LOGGER = LoggerFactory.getLogger(JdbcDestinationHandler.class);


    public TeradataDestinationHandler(String databaseName, JdbcDatabase jdbcDatabase, String rawTableSchema) {
        super(databaseName, jdbcDatabase, rawTableSchema, SQLDialect.DEFAULT);
    }

    @Override
    protected MinimumDestinationState toDestinationState(@NotNull JsonNode jsonNode) {
        return new MinimumDestinationState.Impl(jsonNode.hasNonNull("needsSoftReset") && jsonNode.get("needsSoftReset").asBoolean());
    }

    @NotNull
    @Override
    protected String toJdbcTypeName(@NotNull AirbyteType airbyteType) {
        // This is mostly identical to the postgres implementation, but swaps jsonb to super
        if (airbyteType instanceof final AirbyteProtocolType airbyteProtocolType) {
            return toJdbcTypeName(airbyteProtocolType);
        }
        return switch (airbyteType.getTypeName()) {
            case Struct.TYPE, UnsupportedOneOf.TYPE, Array.TYPE -> "json";
            // No nested Unions supported so this will definitely not result in infinite recursion.
            case Union.TYPE -> toJdbcTypeName(((Union) airbyteType).chooseType());
            default -> throw new IllegalArgumentException("Unsupported AirbyteType: " + airbyteType);
        };
    }


    private String toJdbcTypeName(final AirbyteProtocolType airbyteProtocolType) {
        return switch (airbyteProtocolType) {
            case STRING, BOOLEAN -> "varchar";
            case NUMBER -> "float";
            case INTEGER -> "integer";
            case TIMESTAMP_WITH_TIMEZONE -> "timestamp with time zone";
            case TIMESTAMP_WITHOUT_TIMEZONE -> "timestamp";
            case TIME_WITH_TIMEZONE -> "time with time zone";
            case TIME_WITHOUT_TIMEZONE -> "time";
            case DATE -> "date";
            case UNKNOWN -> "json";
        };
    }

    @Override
    public void commitDestinationStates(@NotNull Map<StreamId, ? extends MinimumDestinationState> destinationStates) {
        try {
            if (destinationStates.isEmpty()) {
                return;
            }

            // Delete all state records where the stream name+namespace match one of our states
            List<String> sqlStatementsDestinationState = new ArrayList<>();
            sqlStatementsDestinationState.add(getDeleteStatesSql(destinationStates));

            for (Map.Entry<StreamId, ? extends MinimumDestinationState> entry : destinationStates.entrySet()) {
                StreamId streamId = entry.getKey();
                MinimumDestinationState value = entry.getValue();
                String stateJson = Jsons.serialize(value);


                // Reinsert all of our states
                var insertStatesStep = getDslContext()
                        .insertInto(table(quotedName(getRawTableNamespace(), DESTINATION_STATE_TABLE_NAME)))
                        .columns(
                                field(quotedName(DESTINATION_STATE_TABLE_COLUMN_NAME), String.class),
                                field(quotedName(DESTINATION_STATE_TABLE_COLUMN_NAMESPACE), String.class),
                                field(quotedName(DESTINATION_STATE_TABLE_COLUMN_STATE), String.class),
                                field(quotedName(DESTINATION_STATE_TABLE_COLUMN_UPDATED_AT))
                        ).values(
                                streamId.getOriginalName(),
                                streamId.getOriginalNamespace(),
                                stateJson,
                                null
                        ).getSQL(ParamType.INLINED);

                sqlStatementsDestinationState.add(insertStatesStep);
            }


            executeWithinTransaction(sqlStatementsDestinationState);
        } catch (Exception e) {
            LOGGER.warn("Failed to commit destination states", e);
        }
    }

    @Override
    protected Map<AirbyteStreamNameNamespacePair, MinimumDestinationState> getAllDestinationStates() {
        try {
            String sqlStatement = getDslContext()
                    .createTable(quotedName(getRawTableNamespace(), DESTINATION_STATE_TABLE_NAME))
                    .column(quotedName(DESTINATION_STATE_TABLE_COLUMN_NAME), SQLDataType.VARCHAR(256))
                    .column(quotedName(DESTINATION_STATE_TABLE_COLUMN_NAMESPACE), SQLDataType.VARCHAR(256))
                    .column(quotedName(DESTINATION_STATE_TABLE_COLUMN_STATE), SQLDataType.VARCHAR(256))
                    .column(quotedName(DESTINATION_STATE_TABLE_COLUMN_UPDATED_AT), getStateTableUpdatedAtType())
                    .getSQL(ParamType.INLINED);

            try {
                getJdbcDatabase().execute(sqlStatement);
            } catch (SQLException e) {
                if (e.getMessage().contains("already exists")) {
                    LOGGER.warn("Table already exists: {}", sqlStatement);
                } else {
                    AirbyteTraceMessageUtility.emitTransientErrorTrace(e, "Connector failed while creating table ");
                    throw new RuntimeException(e);
                }
            }

            // Fetch all records from it.
            return getJdbcDatabase()
                    .queryJsons(
                            getDslContext().select(
                                            field(quotedName(DESTINATION_STATE_TABLE_COLUMN_NAME)),
                                            field(quotedName(DESTINATION_STATE_TABLE_COLUMN_NAMESPACE)),
                                            field(quotedName(DESTINATION_STATE_TABLE_COLUMN_STATE)),
                                            field(quotedName(DESTINATION_STATE_TABLE_COLUMN_UPDATED_AT))
                                    ).from(quotedName(getRawTableNamespace(), DESTINATION_STATE_TABLE_NAME))
                                    .getSQL()
                    )
                    .stream()
                    .map(recordJson -> {
                        ObjectNode record = (ObjectNode) recordJson;
                        Map<String, JsonNode> newFields = new HashMap<>();

                        record.fieldNames().forEachRemaining(fieldName ->
                                newFields.put(fieldName.toLowerCase(Locale.getDefault()), record.get(fieldName))
                        );

                        record.setAll(newFields);
                        return record;
                    })
                    .sorted(Comparator.comparing(it -> {
                        JsonNode updatedAtNode = it.get(DESTINATION_STATE_TABLE_COLUMN_UPDATED_AT);
                        return updatedAtNode != null ? OffsetDateTime.parse(updatedAtNode.asText()) : OffsetDateTime.MIN;
                    }))
                    .collect(Collectors.toMap(
                            it -> new AirbyteStreamNameNamespacePair(
                                    it.get(DESTINATION_STATE_TABLE_COLUMN_NAME).asText(),
                                    it.get(DESTINATION_STATE_TABLE_COLUMN_NAMESPACE).asText()),
                            it -> {
                                JsonNode stateTextNode = it.get(DESTINATION_STATE_TABLE_COLUMN_STATE);
                                JsonNode stateNode = stateTextNode != null
                                        ? Jsons.deserialize(stateTextNode.asText())
                                        : Jsons.emptyObject();
                                return toDestinationState(stateNode);
                            },
                            (existing, replacement) -> replacement,
                            LinkedHashMap::new
                    ));

        } catch (Exception e) {
            LOGGER.warn("Failed to retrieve destination states", e);
            return Collections.emptyMap();
        }
    }

    @Override
    protected boolean isFinalTableEmpty(StreamId id) throws Exception {
        return !getJdbcDatabase().queryBoolean(
                getDslContext()
                        .select(
                                DSL.case_()
                                        .when(
                                                DSL.field(
                                                        DSL.select(DSL.count())
                                                                .from(DSL.name(id.getFinalNamespace(), id.getFinalName()))
                                                ).gt(0),
                                                DSL.inline(1)
                                        )
                                        .otherwise(DSL.inline(0))
                                        .as("exists_flag")
                        )
                        .getSQL(ParamType.INLINED)
        );
    }

    @Override
    protected String getDeleteStatesSql(Map<StreamId, ? extends MinimumDestinationState> destinationStates) {
        return getDslContext()
                .deleteFrom(DSL.table(quotedName(getRawTableNamespace(), DESTINATION_STATE_TABLE_NAME)))
                .where(
                        destinationStates.keySet()
                                .stream()
                                .map(streamId ->
                                        DSL.field(quotedName(DESTINATION_STATE_TABLE_COLUMN_NAME))
                                                .eq(streamId.getOriginalName())
                                                .and(
                                                        DSL.field(quotedName(DESTINATION_STATE_TABLE_COLUMN_NAMESPACE))
                                                                .eq(streamId.getOriginalNamespace())
                                                )
                                )
                                .reduce(DSL.noCondition(), (obj, arg2) -> obj.or(arg2))
                )
                .getSQL(ParamType.INLINED);
    }


    //TODO: CLEANUP
    @Override
    public void execute(Sql sql) {
        List<List<String>> transactions = sql.transactions();
        transactions.forEach(transaction -> {
            try {
                getJdbcDatabase().executeWithinTransaction(transaction);
            } catch (SQLException e) {
                if (e.getMessage().contains("does not exist")) {
                    // ignore table does not exists error
                    LOGGER.info(e.toString());
                } else if (e.getMessage().contains("with the specified name already exists")) {
                    // ignore if db already exists
                    LOGGER.info(e.toString());
                } else {
                    throw new RuntimeException(e);
                }
            }
        });

    }

}
