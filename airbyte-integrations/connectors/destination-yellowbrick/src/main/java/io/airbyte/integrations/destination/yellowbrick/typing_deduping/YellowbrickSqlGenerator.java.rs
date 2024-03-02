/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.yellowbrick.typing_deduping;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_META;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_DATA;
import static org.jooq.impl.DSL.cast;
import static org.jooq.impl.DSL.case_;
import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.list;
import static org.jooq.impl.DSL.function;
import static org.jooq.impl.DSL.name;
import static org.jooq.impl.DSL.quotedName;
import static org.jooq.impl.DSL.rowNumber;
import static org.jooq.impl.DSL.val;
import org.jooq.CaseConditionStep;

import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.Array;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.Struct;
import io.airbyte.integrations.base.destination.typing_deduping.Union;
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf;
import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import org.jooq.Condition;
import org.jooq.DataType;
import org.jooq.Field;
import org.jooq.SQLDialect;
import org.jooq.impl.DefaultDataType;
import org.jooq.impl.SQLDataType;

public class YellowbrickSqlGenerator extends JdbcSqlGenerator {

  public static final String CASE_STATEMENT_SQL_TEMPLATE = "CASE WHEN {0} THEN {1} ELSE {2} END ";
  public static final String CASE_STATEMENT_NO_ELSE_SQL_TEMPLATE = "CASE WHEN {0} THEN {1} END ";
  private static final String COLUMN_ERROR_MESSAGE_FORMAT = "Problem with `%s`";
  private static final String AIRBYTE_META_COLUMN_ERRORS_KEY = "errors";

  public YellowbrickSqlGenerator(final NamingConventionTransformer namingTransformer) {
    super(namingTransformer);
  }

  /**
   * This method returns Jooq internal DataType, Ideally we need to implement DataType interface with
   * all the required fields for Jooq typed query construction
   *
   * @return
   */
  private DataType<?> getSuperType() {
    return SQLDataType.VARCHAR(64000);
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

  @Override
  public DataType<?> toDialectType(AirbyteProtocolType airbyteProtocolType) {
    if (airbyteProtocolType.equals(AirbyteProtocolType.STRING)) {
      return SQLDataType.VARCHAR(64000);
    }
    return super.toDialectType(airbyteProtocolType);
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
  protected Field<?> castedField(final Field<?> field, final AirbyteType type, final String alias, final boolean useExpensiveSaferCasting) {
    if (type instanceof final AirbyteProtocolType airbyteProtocolType) {
      switch (airbyteProtocolType) {
        case STRING -> {
          return field(CASE_STATEMENT_SQL_TEMPLATE,
              jsonTypeOf(field).ne("string").and(field.isNotNull()),
              jsonSerialize(field),
              castedField(field, airbyteProtocolType, useExpensiveSaferCasting)).as(quotedName(alias));
        }
        default -> {
          return castedField(field, airbyteProtocolType, useExpensiveSaferCasting).as(quotedName(alias));
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
      case Union.TYPE -> castedField(field, ((Union) type).chooseType(), alias, useExpensiveSaferCasting);
      default -> throw new IllegalArgumentException("Unsupported AirbyteType: " + type);
    };
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

/**
  private Field<String> jsonTypeOf(final Field<?> field) {
      return case_()
          // Object detection
          .when(field.like("{%}"), val("object"))
          // Array detection
          .when(field.like("[%]"), val("array"))
          // String detection
          .when(field.like("\"%\""), val("string"))
          // Number detection (simplified)
          .when(field.likeRegex("-?[0-9]+(\\.[0-9]+)?"), val("number"))
          // Boolean detection
          .when(field.in(val("true"), val("false")), val("boolean"))
          // Null detection
          .when(field.equals("null"), val("null"))
          // Default case
          .else_(val("unknown"));
  }
*/
    private CaseConditionStep<String> jsonTypeOf(Field<?> jsonField) {
        // Start building a CASE statement
        Field<String> field = jsonField.cast(String.class);
        return
            case_() // jOOQ DSL for starting a CASE statement
                .when(field.like("{%}"), val("object"))
                .when(field.like("[%]"), val("array"))
                .when(field.like("\"%\""), val("string"))
                // Assuming a simplified regex for numeric detection; adjust as necessary
                .when(field.likeRegex("-?[0-9]+(\\.[0-9]+)?"), val("number"))
                .when(field.equalIgnoreCase("true").or(field.equalIgnoreCase("false")), val("boolean"))
                .when(field.equal("null"), val("null"));
                // Note: No need for .otherwise() if all conditions are covered, or you can add it for unmatched cases
    }

  private Field<String> jsonSerialize(final Field<?> field) {
    //return function("JSON_SERIALIZE", SQLDataType.VARCHAR, field);
    return field.cast(String.class);
  }

/**
  Field<?> toCastingErrorCaseStmt(final ColumnId column, final AirbyteType type) {
    final Field<?> field = field(quotedName(COLUMN_NAME_DATA, column.originalName()));
    // Just checks if data is not null but casted data is null. This also accounts for conditional
    // casting result of array and struct.
    // TODO: Timestamp format issues can result in null values when cast, add regex check if destination
    // supports regex functions.
    return field(CASE_STATEMENT_SQL_TEMPLATE,
        field.isNotNull().and(castedField(field, type, column.name(), true).isNull()),
        function("ARRAY", getSuperType(), val(COLUMN_ERROR_MESSAGE_FORMAT.formatted(column.name()))), field("ARRAY()"));
  }
*/

  private Field<String> toCastingErrorCaseStmt(final ColumnId column, final AirbyteType type) {
    return val((String) null);
  }

  @Override
  protected Field<String> buildAirbyteMetaColumn(final LinkedHashMap<ColumnId, AirbyteType> columns) {
    // First, collect the fields to a List<Field<String>> to avoid unchecked conversion
    List<Field<String>> dataFieldErrorsList = columns
            .entrySet()
            .stream()
            .map(column -> toCastingErrorCaseStmt(column.getKey(), column.getValue()))
            .collect(Collectors.toList());

    // Avoid using raw types by creating an array of Field<?> and casting it to Field<String>[]
    @SuppressWarnings("unchecked") // Suppress warnings for unchecked cast
    Field<String>[] dataFieldErrors = (Field<String>[]) dataFieldErrorsList.toArray(new Field<?>[dataFieldErrorsList.size()]);

    // Constructing the JSON array string of errors
    Field<String> errorsArray = field(
        "json_array_str({0})",
        String.class,
        list(dataFieldErrors) // This uses DSL.list to create a dynamic list of fields for json_array_str
    );

    // Constructing the JSON object with the "errors" key
    return field(
        "json_object_str('errors', {0})",
        String.class,
        errorsArray
    ).as(COLUMN_NAME_AB_META);
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
  protected Field<Integer> getRowNumber(final List<ColumnId> primaryKeys, final Optional<ColumnId> cursor) {
    // literally identical to postgres's getRowNumber implementation, changes here probably should
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
  protected Condition cdcDeletedAtNotNullCondition() {
    return field(name(COLUMN_NAME_AB_LOADED_AT)).isNotNull()
        .and(jsonTypeOf(extractColumnAsJson(cdcDeletedAtColumn)).ne("null"));
  } 

  @Override
  protected Field<Timestamp> currentTimestamp() {
    return function("GETDATE", SQLDataType.TIMESTAMP);
  }

  @Override
  public boolean shouldRetry(final Exception e) {
    return false;
  }

  private Field<Object> extractColumnAsJson(final ColumnId column) {
    return field("json_lookup({0}, '/' || {1}, 'jpointer_simdjson')", name(COLUMN_NAME_DATA), val(column.originalName()));
  }

}
