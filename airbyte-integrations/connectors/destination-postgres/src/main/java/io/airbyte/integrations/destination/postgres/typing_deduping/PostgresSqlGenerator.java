/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.typing_deduping;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_META;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_RAW_ID;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_DATA;
import static java.util.Collections.emptyList;
import static org.jooq.impl.DSL.array;
import static org.jooq.impl.DSL.case_;
import static org.jooq.impl.DSL.cast;
import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.function;
import static org.jooq.impl.DSL.name;
import static org.jooq.impl.DSL.quotedName;
import static org.jooq.impl.DSL.rowNumber;
import static org.jooq.impl.DSL.val;

import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.Array;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.Sql;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.Struct;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
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

  public static final DataType<?> JSONB_TYPE = new DefaultDataType<>(null, Object.class, "jsonb");

  private static final Map<String, String> POSTGRES_TYPE_NAME_TO_JDBC_TYPE = ImmutableMap.of(
      "numeric", "decimal",
      "int8", "bigint",
      "bool", "boolean",
      "timestamptz", "timestamp with time zone",
      "timetz", "time with time zone");

  public PostgresSqlGenerator(final NamingConventionTransformer namingTransformer) {
    super(namingTransformer);
  }

  @Override
  public StreamId buildStreamId(final String namespace, final String name, final String rawNamespaceOverride) {
    // There is a mismatch between convention used in create table query in SqlOperations vs this.
    // For postgres specifically, when a create table is issued without a quoted identifier, it will be
    // converted to lowercase.
    // To keep it consistent when querying raw table in T+D query, convert it to lowercase.
    // TODO: This logic should be unified across Raw and final table operations in a single class
    // operating on a StreamId.
    return new StreamId(
        namingTransformer.getNamespace(namespace),
        namingTransformer.convertStreamName(name),
        namingTransformer.getNamespace(rawNamespaceOverride).toLowerCase(),
        namingTransformer.convertStreamName(StreamId.concatenateRawTableName(namespace, name)).toLowerCase(),
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
    final Name finalTableName = name(stream.id().finalNamespace(), stream.id().finalName() + suffix);

    statements.add(super.createTable(stream, suffix, force));

    if (stream.destinationSyncMode() == DestinationSyncMode.APPEND_DEDUP) {
      // An index for our ROW_NUMBER() PARTITION BY pk ORDER BY cursor, extracted_at function
      final List<Name> pkNames = stream.primaryKey().stream()
          .map(pk -> quotedName(pk.name()))
          .toList();
      statements.add(Sql.of(getDslContext().createIndex().on(
          finalTableName,
          Stream.of(
              pkNames.stream(),
              // if cursor is present, then a stream containing its name
              // but if no cursor, then empty stream
              stream.cursor().stream().map(cursor -> quotedName(cursor.name())),
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
  protected List<String> createIndexSql(final StreamConfig stream, final String suffix) {
    if (stream.destinationSyncMode() == DestinationSyncMode.APPEND_DEDUP && !stream.primaryKey().isEmpty()) {
      return List.of(
          getDslContext().createIndex().on(
              name(stream.id().finalNamespace(), stream.id().finalName() + suffix),
              stream.primaryKey().stream()
                  .map(pk -> quotedName(pk.name()))
                  .toList())
              .getSQL());
    } else {
      return emptyList();
    }
  }

  @Override
  protected List<Field<?>> extractRawDataFields(final LinkedHashMap<ColumnId, AirbyteType> columns, final boolean useExpensiveSaferCasting) {
    return columns
        .entrySet()
        .stream()
        .map(column -> castedField(
            extractColumnAsJson(column.getKey()),
            column.getValue(),
            column.getKey().name(),
            useExpensiveSaferCasting))
        .collect(Collectors.toList());
  }

  @Override
  protected Field<?> castedField(
                                 final Field<?> field,
                                 final AirbyteType type,
                                 final String alias,
                                 final boolean useExpensiveSaferCasting) {
    return castedField(field, type, useExpensiveSaferCasting).as(quotedName(alias));
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

  // TODO this isn't actually used right now... can we refactor this out?
  // (redshift is doing something interesting with this method, so leaving it for now)
  @Override
  protected Field<?> castedField(final Field<?> field, final AirbyteProtocolType type, final boolean useExpensiveSaferCasting) {
    return cast(field, toDialectType(type));
  }

  @Override
  protected Field<?> buildAirbyteMetaColumn(final LinkedHashMap<ColumnId, AirbyteType> columns) {
    final Field<?>[] dataFieldErrors = columns
        .entrySet()
        .stream()
        .map(column -> toCastingErrorCaseStmt(column.getKey(), column.getValue()))
        .toArray(Field<?>[]::new);
    return function(
        "JSONB_BUILD_OBJECT",
        JSONB_TYPE,
        val("errors"),
        function("ARRAY_REMOVE", JSONB_TYPE, array(dataFieldErrors), val((String) null))).as(COLUMN_NAME_AB_META);
  }

  private Field<String> toCastingErrorCaseStmt(final ColumnId column, final AirbyteType type) {
    final Field<Object> extract = extractColumnAsJson(column);
    if (type instanceof Struct) {
      // If this field is a struct, verify that the raw data is an object or null.
      return case_()
          .when(
              extract.isNotNull()
                  .and(jsonTypeof(extract).notIn("object", "null")),
              val("Problem with `" + column.originalName() + "`"))
          .else_(val((String) null));
    } else if (type instanceof Array) {
      // Do the same for arrays.
      return case_()
          .when(
              extract.isNotNull()
                  .and(jsonTypeof(extract).notIn("array", "null")),
              val("Problem with `" + column.originalName() + "`"))
          .else_(val((String) null));
    } else if (type == AirbyteProtocolType.UNKNOWN || type == AirbyteProtocolType.STRING) {
      // Unknown types require no casting, so there's never an error.
      // Similarly, everything can cast to string without error.
      return val((String) null);
    } else {
      // For other type: If the raw data is not NULL or 'null', but the casted data is NULL,
      // then we have a typing error.
      return case_()
          .when(
              extract.isNotNull()
                  .and(jsonTypeof(extract).ne("null"))
                  .and(castedField(extract, type, true).isNull()),
              val("Problem with `" + column.originalName() + "`"))
          .else_(val((String) null));
    }
  }

  @Override
  protected Condition cdcDeletedAtNotNullCondition() {
    return field(name(COLUMN_NAME_AB_LOADED_AT)).isNotNull()
        .and(jsonTypeof(extractColumnAsJson(cdcDeletedAtColumn)).ne("null"));
  }

  @Override
  protected Field<Integer> getRowNumber(final List<ColumnId> primaryKeys, final Optional<ColumnId> cursor) {
    // literally identical to redshift's getRowNumber implementation, changes here probably should
    // be reflected there
    final List<Field<?>> primaryKeyFields =
        primaryKeys != null ? primaryKeys.stream().map(columnId -> field(quotedName(columnId.name()))).collect(Collectors.toList())
            : new ArrayList<>();
    final List<Field<?>> orderedFields = new ArrayList<>();
    // We can still use Jooq's field to get the quoted name with raw sql templating.
    // jooq's .desc returns SortField<?> instead of Field<?> and NULLS LAST doesn't work with it
    cursor.ifPresent(columnId -> orderedFields.add(field("{0} desc NULLS LAST", field(quotedName(columnId.name())))));
    orderedFields.add(field("{0} desc", quotedName(COLUMN_NAME_AB_EXTRACTED_AT)));
    return rowNumber()
        .over()
        .partitionBy(primaryKeyFields)
        .orderBy(orderedFields).as(ROW_NUMBER_COLUMN_NAME);
  }

  @Override
  public boolean existingSchemaMatchesStreamConfig(final StreamConfig stream, final TableDefinition existingTable) {
    // Check that the columns match, with special handling for the metadata columns.
    // This is mostly identical to the redshift implementation, but swaps super to jsonb
    final LinkedHashMap<String, String> intendedColumns = stream.columns().entrySet().stream()
        .collect(LinkedHashMap::new,
            (map, column) -> map.put(column.getKey().name(), toDialectType(column.getValue()).getTypeName()),
            LinkedHashMap::putAll);
    final LinkedHashMap<String, String> actualColumns = existingTable.columns().entrySet().stream()
        .filter(column -> JavaBaseConstants.V2_FINAL_TABLE_METADATA_COLUMNS.stream()
            .noneMatch(airbyteColumnName -> airbyteColumnName.equals(column.getKey())))
        .collect(LinkedHashMap::new,
            (map, column) -> map.put(column.getKey(), jdbcTypeNameFromPostgresTypeName(column.getValue().type())),
            LinkedHashMap::putAll);

    final boolean sameColumns = actualColumns.equals(intendedColumns)
        && "varchar".equals(existingTable.columns().get(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID).type())
        && "timestamptz".equals(existingTable.columns().get(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT).type())
        && "jsonb".equals(existingTable.columns().get(JavaBaseConstants.COLUMN_NAME_AB_META).type());

    return sameColumns;
  }

  /**
   * Extract a raw field, leaving it as jsonb
   */
  private Field<Object> extractColumnAsJson(final ColumnId column) {
    return field("{0} -> {1}", name(COLUMN_NAME_DATA), val(column.originalName()));
  }

  private Field<String> jsonTypeof(final Field<?> field) {
    return function("JSONB_TYPEOF", SQLDataType.VARCHAR, field);
  }

  private static String jdbcTypeNameFromPostgresTypeName(final String redshiftType) {
    return POSTGRES_TYPE_NAME_TO_JDBC_TYPE.getOrDefault(redshiftType, redshiftType);
  }

}
