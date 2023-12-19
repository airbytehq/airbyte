/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_META;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_DATA;
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
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.Struct;
import io.airbyte.integrations.base.destination.typing_deduping.Union;
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf;
import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;
import org.jooq.Condition;
import org.jooq.DataType;
import org.jooq.Field;
import org.jooq.SQLDialect;
import org.jooq.impl.DefaultDataType;
import org.jooq.impl.SQLDataType;

public class RedshiftSqlGenerator extends JdbcSqlGenerator {

  public static final String CASE_STATEMENT_SQL_TEMPLATE = "CASE WHEN {0} THEN {1} ELSE {2} END ";
  public static final String CASE_STATEMENT_NO_ELSE_SQL_TEMPLATE = "CASE WHEN {0} THEN {1} END ";
  private static final Map<String, String> REDSHIFT_TYPE_NAME_TO_JDBC_TYPE = ImmutableMap.of(
      "numeric", "decimal",
      "int8", "bigint",
      "bool", "boolean",
      "timestamptz", "timestamp with time zone",
      "timetz", "time with time zone");
  private static final String COLUMN_ERROR_MESSAGE_FORMAT = "Problem with `%s`";
  private static final String AIRBYTE_META_COLUMN_ERRORS_KEY = "errors";

  public RedshiftSqlGenerator(final NamingConventionTransformer namingTransformer) {
    super(namingTransformer);
  }

  /**
   * This method returns Jooq internal DataType, Ideally we need to implement DataType interface with
   * all the required fields for Jooq typed query construction
   *
   * @return
   */
  private DataType<?> getSuperType() {
    return new DefaultDataType<>(null, String.class, "super");
  }

  @Override
  protected DataType<?> getStructType() {
    return getSuperType();
  }

  @Override
  protected DataType<?> getArrayType() {
    return getSuperType();
  }

  @Override
  protected DataType<?> getWidestType() {
    return getSuperType();
  }

  @Override
  protected SQLDialect getDialect() {
    return SQLDialect.POSTGRES;
  }

  /**
   * Notes about Redshift specific SQL * 16MB Limit on the total size of the SQL sent in a session *
   * Default mode of casting within SUPER is lax mode, to enable strict use SET
   * cast_super_null_on_error='OFF'; * *
   * https://docs.aws.amazon.com/redshift/latest/dg/super-configurations.html *
   * https://docs.aws.amazon.com/redshift/latest/dg/r_MERGE.html#r_MERGE_usage_notes * * (Cannot use
   * WITH clause in MERGE statement).
   * https://cloud.google.com/bigquery/docs/migration/redshift-sql#merge_statement * *
   * https://docs.aws.amazon.com/redshift/latest/dg/r_WITH_clause.html#r_WITH_clause-usage-notes *
   * Primary keys are informational only and not enforced
   * (https://docs.aws.amazon.com/redshift/latest/dg/t_Defining_constraints.html) TODO: Look at SORT
   * KEYS, DISTKEY in redshift for optimizing the query performance.
   */

  @Override
  protected Field<?> castedField(final Field<?> field, final AirbyteType type, final String alias) {
    if (type instanceof final AirbyteProtocolType airbyteProtocolType) {
      switch (airbyteProtocolType) {
        case STRING -> {
          return field(CASE_STATEMENT_SQL_TEMPLATE,
              jsonTypeOf(field).ne("string").and(field.isNotNull()),
              jsonSerialize(field),
              castedField(field, airbyteProtocolType)).as(quotedName(alias));
        }
        default -> {
          return castedField(field, airbyteProtocolType).as(quotedName(alias));
        }
      }

    }
    // Redshift SUPER can silently cast an array type to struct and vice versa.
    return switch (type.getTypeName()) {
      case Struct.TYPE, UnsupportedOneOf.TYPE -> field(CASE_STATEMENT_NO_ELSE_SQL_TEMPLATE,
          jsonTypeOf(field).eq("object"),
          cast(field, getStructType())).as(quotedName(alias));
      case Array.TYPE -> field(CASE_STATEMENT_NO_ELSE_SQL_TEMPLATE,
          jsonTypeOf(field).eq("array"),
          cast(field, getArrayType())).as(quotedName(alias));
      // No nested Unions supported so this will definitely not result in infinite recursion.
      case Union.TYPE -> castedField(field, ((Union) type).chooseType(), alias);
      default -> throw new IllegalArgumentException("Unsupported AirbyteType: " + type);
    };
  }

  @Override
  protected List<Field<?>> extractRawDataFields(LinkedHashMap<ColumnId, AirbyteType> columns) {
    return columns
        .entrySet()
        .stream()
        .map(column -> castedField(field(quotedName(COLUMN_NAME_DATA, column.getKey().originalName())), column.getValue(), column.getKey().name()))
        .collect(Collectors.toList());
  }

  private Field<String> jsonTypeOf(final Field<?> field) {
    return function("JSON_TYPEOF", SQLDataType.VARCHAR, field);
  }

  private Field<String> jsonSerialize(final Field<?> field) {
    return function("JSON_SERIALIZE", SQLDataType.VARCHAR, field);
  }

  /**
   * Redshift ARRAY_CONCAT supports only 2 arrays, recursively build ARRAY_CONCAT for n arrays.
   *
   * @param arrays
   * @return
   */
  Field<?> arrayConcatStmt(List<Field<?>> arrays) {
    if (arrays.isEmpty()) {
      return field("ARRAY()"); // Return an empty string if the list is empty
    }

    // Base case: if there's only one element, return it
    if (arrays.size() == 1) {
      return arrays.get(0);
    }

    // Recursive case: construct ARRAY_CONCAT function call
    Field<?> lastValue = arrays.get(arrays.size() - 1);
    Field<?> recursiveCall = arrayConcatStmt(arrays.subList(0, arrays.size() - 1));

    return function("ARRAY_CONCAT", getSuperType(), recursiveCall, lastValue);
  }

  Field<?> toCastingErrorCaseStmt(final ColumnId column, final AirbyteType type) {
    final Field<?> field = field(quotedName(COLUMN_NAME_DATA, column.originalName()));
    // Just checks if data is not null but casted data is null. This also accounts for conditional
    // casting result of array and struct.
    // TODO: Timestamp format issues can result in null values when cast, add regex check if destination
    // supports regex functions.
    return field(CASE_STATEMENT_SQL_TEMPLATE,
        field.isNotNull().and(castedField(field, type, column.name()).isNull()),
        function("ARRAY", getSuperType(), val(COLUMN_ERROR_MESSAGE_FORMAT.formatted(column.name()))), field("ARRAY()"));
  }

  @Override
  protected Field<?> buildAirbyteMetaColumn(final LinkedHashMap<ColumnId, AirbyteType> columns) {
    final List<Field<?>> dataFields = columns
        .entrySet()
        .stream()
        .map(column -> toCastingErrorCaseStmt(column.getKey(), column.getValue()))
        .collect(Collectors.toList());
    return function("OBJECT", getSuperType(), val(AIRBYTE_META_COLUMN_ERRORS_KEY), arrayConcatStmt(dataFields)).as(COLUMN_NAME_AB_META);

  }

  @Override
  public boolean existingSchemaMatchesStreamConfig(final StreamConfig stream, final TableDefinition existingTable) {
    // Check that the columns match, with special handling for the metadata columns.
    final LinkedHashMap<String, String> intendedColumns = stream.columns().entrySet().stream()
        .collect(LinkedHashMap::new,
            (map, column) -> map.put(column.getKey().name(), toDialectType(column.getValue()).getTypeName()),
            LinkedHashMap::putAll);
    final LinkedHashMap<String, String> actualColumns = existingTable.columns().entrySet().stream()
        .filter(column -> JavaBaseConstants.V2_FINAL_TABLE_METADATA_COLUMNS.stream()
            .noneMatch(airbyteColumnName -> airbyteColumnName.equals(column.getKey())))
        .collect(LinkedHashMap::new,
            (map, column) -> map.put(column.getKey(), jdbcTypeNameFromRedshiftTypeName(column.getValue().type())),
            LinkedHashMap::putAll);

    final boolean sameColumns = actualColumns.equals(intendedColumns)
        && "varchar".equals(existingTable.columns().get(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID).type())
        && "timestamptz".equals(existingTable.columns().get(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT).type())
        && "super".equals(existingTable.columns().get(JavaBaseConstants.COLUMN_NAME_AB_META).type());

    return sameColumns;
  }

  /**
   * Return ROW_NUMBER() OVER (PARTITION BY primaryKeys ORDER BY cursor DESC NULLS LAST,
   * _airbyte_extracted_at DESC)
   *
   * @param primaryKeys
   * @param cursor
   * @return
   */
  @Override
  protected Field<Integer> getRowNumber(List<ColumnId> primaryKeys, Optional<ColumnId> cursor) {
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
  protected Condition cdcDeletedAtNotNullCondition() {
    return field(name(COLUMN_NAME_AB_LOADED_AT)).isNotNull()
        .and(function("JSON_TYPEOF", SQLDataType.VARCHAR, field(quotedName(COLUMN_NAME_DATA, cdcDeletedAtColumn.name())))
            .ne("null"));
  }

  @Override
  protected Field<Timestamp> currentTimestamp() {
    return function("GETDATE", SQLDataType.TIMESTAMP);
  }

  @Override
  public boolean shouldRetry(Exception e) {
    return false;
  }

  private static String jdbcTypeNameFromRedshiftTypeName(final String redshiftType) {
    return REDSHIFT_TYPE_NAME_TO_JDBC_TYPE.getOrDefault(redshiftType, redshiftType);
  }

}
