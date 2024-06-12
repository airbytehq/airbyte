/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.typing_deduping;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_META;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_RAW_ID;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_DATA;
import static org.jooq.impl.DSL.array;
import static org.jooq.impl.DSL.case_;
import static org.jooq.impl.DSL.cast;
import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.function;
import static org.jooq.impl.DSL.name;
import static org.jooq.impl.DSL.quotedName;
import static org.jooq.impl.DSL.rowNumber;
import static org.jooq.impl.DSL.val;

import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.Array;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.Sql;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.Struct;
import io.airbyte.protocol.models.AirbyteRecordMessageMetaChange.Change;
import io.airbyte.protocol.models.AirbyteRecordMessageMetaChange.Reason;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Optional;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.jooq.Condition;
import org.jooq.DataType;
import org.jooq.Field;
import org.jooq.Name;
import org.jooq.SQLDialect;
import org.jooq.impl.DefaultDataType;
import org.jooq.impl.SQLDataType;

public class PostgresSqlGenerator extends JdbcSqlGenerator {

  public static final DataType<Object> JSONB_TYPE = new DefaultDataType<>(SQLDialect.POSTGRES, Object.class, "jsonb");

  public static final String CASE_STATEMENT_SQL_TEMPLATE = "CASE WHEN {0} THEN {1} ELSE {2} END ";

  private static final String AB_META_COLUMN_CHANGES_KEY = "changes";
  private static final String AB_META_CHANGES_FIELD_KEY = "field";
  private static final String AB_META_CHANGES_CHANGE_KEY = "change";
  private static final String AB_META_CHANGES_REASON_KEY = "reason";

  public PostgresSqlGenerator(final NamingConventionTransformer namingTransformer, final boolean cascadeDrop) {
    super(namingTransformer, cascadeDrop);
  }

  @Override
  public StreamId buildStreamId(final String namespace, final String name, final String rawNamespaceOverride) {
    // There is a mismatch between convention used in create table query in SqlOperations vs this.
    // For postgres specifically, when a create table is issued without a quoted identifier, it will be
    // converted to lowercase.
    // To keep it consistent when querying raw table in T+D query, convert it to lowercase.
    // TODO: This logic should be unified across Raw and final table operations in a single class
    // operating on a StreamId.
    final String streamName = getNamingTransformer().getIdentifier(StreamId.concatenateRawTableName(namespace, name)).toLowerCase();
    return new StreamId(
        getNamingTransformer().getNamespace(namespace),
        getNamingTransformer().convertStreamName(name),
        getNamingTransformer().getNamespace(rawNamespaceOverride).toLowerCase(),
        streamName,
        namespace,
        name);
  }

  @Override
  protected DataType<?> getStructType() {
    return JSONB_TYPE;
  }

  @Override
  protected DataType<?> getArrayType() {
    return JSONB_TYPE;
  }

  @Override
  protected DataType<?> getWidestType() {
    return JSONB_TYPE;
  }

  @Override
  protected SQLDialect getDialect() {
    return SQLDialect.POSTGRES;
  }

  @Override
  public DataType<?> toDialectType(AirbyteProtocolType airbyteProtocolType) {
    if (airbyteProtocolType.equals(AirbyteProtocolType.STRING)) {
      // https://www.postgresql.org/docs/current/datatype-character.html
      // If specified, the length n must be greater than zero and cannot exceed 10,485,760 (10 MB).
      // If you desire to store long strings with no specific upper limit,
      // use text or character varying without a length specifier,
      // rather than making up an arbitrary length limit.
      return SQLDataType.VARCHAR;
    }
    return super.toDialectType(airbyteProtocolType);
  }

  @Override
  public Sql createTable(final StreamConfig stream, final String suffix, final boolean force) {
    final List<Sql> statements = new ArrayList<>();
    final Name finalTableName = name(stream.getId().getFinalNamespace(), stream.getId().getFinalName() + suffix);

    statements.add(super.createTable(stream, suffix, force));

    if (stream.getDestinationSyncMode() == DestinationSyncMode.APPEND_DEDUP) {
      // An index for our ROW_NUMBER() PARTITION BY pk ORDER BY cursor, extracted_at function
      final List<Name> pkNames = stream.getPrimaryKey().stream()
          .map(pk -> quotedName(pk.getName()))
          .toList();
      statements.add(Sql.of(getDslContext().createIndex().on(
          finalTableName,
          Stream.of(
              pkNames.stream(),
              // if cursor is present, then a stream containing its name
              // but if no cursor, then empty stream
              stream.getCursor().stream().map(cursor -> quotedName(cursor.getName())),
              Stream.of(name(COLUMN_NAME_AB_EXTRACTED_AT))).flatMap(Function.identity()).toList())
          .getSQL()));
    }
    statements.add(Sql.of(getDslContext().createIndex().on(
        finalTableName,
        name(COLUMN_NAME_AB_EXTRACTED_AT))
        .getSQL()));

    statements.add(Sql.of(getDslContext().createIndex().on(
        finalTableName,
        name(COLUMN_NAME_AB_RAW_ID))
        .getSQL()));

    return Sql.concat(statements);
  }

  @Override
  protected List<Field<?>> extractRawDataFields(final LinkedHashMap<ColumnId, AirbyteType> columns, final boolean useExpensiveSaferCasting) {
    return columns
        .entrySet()
        .stream()
        .map(column -> castedField(
            extractColumnAsJson(column.getKey()),
            column.getValue(),
            useExpensiveSaferCasting).as(column.getKey().getName()))
        .collect(Collectors.toList());
  }

  protected Field<?> castedField(
                                 final Field<?> field,
                                 final AirbyteType type,
                                 final boolean useExpensiveSaferCasting) {
    if (type instanceof Struct) {
      // If this field is a struct, verify that the raw data is an object.
      return cast(
          case_()
              .when(field.isNull().or(jsonTypeof(field).ne("object")), val((Object) null))
              .else_(field),
          JSONB_TYPE);
    } else if (type instanceof Array) {
      // Do the same for arrays.
      return cast(
          case_()
              .when(field.isNull().or(jsonTypeof(field).ne("array")), val((Object) null))
              .else_(field),
          JSONB_TYPE);
    } else if (type == AirbyteProtocolType.UNKNOWN) {
      return cast(field, JSONB_TYPE);
    } else if (type == AirbyteProtocolType.STRING) {
      // we need to render the jsonb to a normal string. For strings, this is the difference between
      // "\"foo\"" and "foo".
      // postgres provides the #>> operator, which takes a json path and returns that extraction as a
      // string.
      // '{}' is an empty json path (it's an empty array literal), so it just stringifies the json value.
      return field("{0} #>> '{}'", String.class, field);
    } else {
      final DataType<?> dialectType = toDialectType(type);
      // jsonb can't directly cast to most types, so convert to text first.
      // also convert jsonb null to proper sql null.
      final Field<String> extractAsText = case_()
          .when(field.isNull().or(jsonTypeof(field).eq("null")), val((String) null))
          .else_(cast(field, SQLDataType.VARCHAR));
      if (useExpensiveSaferCasting) {
        return function(name("pg_temp", "airbyte_safe_cast"), dialectType, extractAsText, cast(val((Object) null), dialectType));
      } else {
        return cast(extractAsText, dialectType);
      }
    }
  }

  @Override
  protected Field<?> castedField(final Field<?> field, final AirbyteProtocolType type, final boolean useExpensiveSaferCasting) {
    return cast(field, toDialectType(type));
  }

  private Field<?> jsonBuildObject(Field<?>... arguments) {
    return function("JSONB_BUILD_OBJECT", JSONB_TYPE, arguments);
  }

  @Override
  protected Field<?> buildAirbyteMetaColumn(final LinkedHashMap<ColumnId, AirbyteType> columns) {
    final List<Field<Object>> dataFieldErrors = columns
        .entrySet()
        .stream()
        .map(column -> toCastingErrorCaseStmt(column.getKey(), column.getValue()))
        .toList();
    final Field<?> rawTableChangesArray =
        field("ARRAY(SELECT jsonb_array_elements_text({0}#>'{changes}'))::jsonb[]", field(name(COLUMN_NAME_AB_META)));

    // Jooq is inferring and casting as int[] for empty fields array call. So explicitly casting it to
    // jsonb[] on empty array
    final Field<?> finalTableChangesArray = dataFieldErrors.isEmpty() ? field("ARRAY[]::jsonb[]")
        : function("ARRAY_REMOVE", JSONB_TYPE, array(dataFieldErrors).cast(JSONB_TYPE.getArrayDataType()), val((String) null));
    return jsonBuildObject(val(AB_META_COLUMN_CHANGES_KEY),
        field("ARRAY_CAT({0}, {1})", finalTableChangesArray, rawTableChangesArray)).as(COLUMN_NAME_AB_META);
  }

  private Field<?> nulledChangeObject(String fieldName) {
    return jsonBuildObject(val(AB_META_CHANGES_FIELD_KEY), val(fieldName),
        val(AB_META_CHANGES_CHANGE_KEY), val(Change.NULLED),
        val(AB_META_CHANGES_REASON_KEY), val(Reason.DESTINATION_TYPECAST_ERROR));
  }

  private Field<Object> toCastingErrorCaseStmt(final ColumnId column, final AirbyteType type) {
    final Field<Object> extract = extractColumnAsJson(column);

    // If this field is a struct, verify that the raw data is an object or null.
    // Do the same for arrays.
    return switch (type) {
      case Struct ignored -> field(CASE_STATEMENT_SQL_TEMPLATE,
                                        extract.isNotNull().and(jsonTypeof(extract).notIn("object", "null")),
                                        nulledChangeObject(column.getOriginalName()),
                                   cast(val((Object) null), JSONB_TYPE));
      case Array ignored -> field(CASE_STATEMENT_SQL_TEMPLATE,
                                       extract.isNotNull().and(jsonTypeof(extract).notIn("array", "null")),
                                       nulledChangeObject(column.getOriginalName()),
                                       cast(val((Object) null), JSONB_TYPE));
      // Unknown types require no casting, so there's never an error.
      // Similarly, everything can cast to string without error.
      case AirbyteProtocolType airbyteProtocolType
          when (airbyteProtocolType == AirbyteProtocolType.UNKNOWN || airbyteProtocolType == AirbyteProtocolType.STRING) ->
          cast(val((Object) null), JSONB_TYPE);
      default -> field(CASE_STATEMENT_SQL_TEMPLATE,
                            extract.isNotNull()
                                .and(jsonTypeof(extract).ne("null"))
                                .and(castedField(extract, type, true).isNull()),
                            nulledChangeObject(column.getOriginalName()),
                            cast(val((Object) null), JSONB_TYPE));
    };
  }

  @Override
  protected Condition cdcDeletedAtNotNullCondition() {
    return field(name(COLUMN_NAME_AB_LOADED_AT)).isNotNull()
        .and(jsonTypeof(extractColumnAsJson(getCdcDeletedAtColumn())).ne("null"));
  }

  @Override
  protected Field<Integer> getRowNumber(final List<ColumnId> primaryKeys, final Optional<ColumnId> cursor) {
    // literally identical to redshift's getRowNumber implementation, changes here probably should
    // be reflected there
    final List<Field<?>> primaryKeyFields =
        primaryKeys != null ? primaryKeys.stream().map(columnId -> field(quotedName(columnId.getName()))).collect(Collectors.toList())
            : new ArrayList<>();
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

  /**
   * Extract a raw field, leaving it as jsonb
   */
  private Field<Object> extractColumnAsJson(final ColumnId column) {
    return field("{0} -> {1}", name(COLUMN_NAME_DATA), val(column.getOriginalName()));
  }

  private Field<String> jsonTypeof(final Field<?> field) {
    return function("JSONB_TYPEOF", SQLDataType.VARCHAR, field);
  }

}
