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

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.Array;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.Struct;
import io.airbyte.integrations.base.destination.typing_deduping.Union;
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf;
import io.airbyte.integrations.destination.redshift.constants.RedshiftDestinationConstants;
import io.airbyte.protocol.models.AirbyteRecordMessageMetaChange.Change;
import io.airbyte.protocol.models.AirbyteRecordMessageMetaChange.Reason;
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
import org.jooq.impl.SQLDataType;

public class RedshiftSqlGenerator extends JdbcSqlGenerator {

  public static final String CASE_STATEMENT_SQL_TEMPLATE = "CASE WHEN {0} THEN {1} ELSE {2} END ";
  public static final String CASE_STATEMENT_NO_ELSE_SQL_TEMPLATE = "CASE WHEN {0} THEN {1} END ";

  private static final String CHANGE_TRACKER_JSON_TEMPLATE = "{\"field\": \"{0}\", \"change\": \"{1}\", \"reason\": \"{2}\"}";

  private static final String AIRBYTE_META_COLUMN_CHANGES_KEY = "changes";

  private final boolean dropCascade;

  private static boolean isDropCascade(JsonNode config) {
    final JsonNode dropCascadeNode = config.get(RedshiftDestinationConstants.DROP_CASCADE_OPTION);
    return dropCascadeNode != null && dropCascadeNode.asBoolean();
  }

  public RedshiftSqlGenerator(final NamingConventionTransformer namingTransformer, JsonNode config) {
    this(namingTransformer, isDropCascade(config));
  }

  public RedshiftSqlGenerator(final NamingConventionTransformer namingTransformer, boolean dropCascade) {
    super(namingTransformer, dropCascade);
    this.dropCascade = dropCascade;
  }

  /**
   * This method returns Jooq internal DataType, Ideally we need to implement DataType interface with
   * all the required fields for Jooq typed query construction
   *
   * @return
   */
  private DataType<?> getSuperType() {
    return RedshiftDestinationConstants.SUPER_TYPE;
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
  protected Field<?> castedField(final Field<?> field, final AirbyteType type, final boolean useExpensiveSaferCasting) {
    if (type instanceof final AirbyteProtocolType airbyteProtocolType) {
      switch (airbyteProtocolType) {
        case STRING -> {
          return field(CASE_STATEMENT_SQL_TEMPLATE,
              jsonTypeOf(field).ne("string").and(field.isNotNull()),
              jsonSerialize(field),
              castedField(field, airbyteProtocolType, useExpensiveSaferCasting));
        }
        default -> {
          return castedField(field, airbyteProtocolType, useExpensiveSaferCasting);
        }
      }

    }
    // Redshift SUPER can silently cast an array type to struct and vice versa.
    return switch (type.getTypeName()) {
      case Struct.TYPE, UnsupportedOneOf.TYPE -> field(CASE_STATEMENT_NO_ELSE_SQL_TEMPLATE,
          jsonTypeOf(field).eq("object"),
          cast(field, getStructType()));
      case Array.TYPE -> field(CASE_STATEMENT_NO_ELSE_SQL_TEMPLATE,
          jsonTypeOf(field).eq("array"),
          cast(field, getArrayType()));
      // No nested Unions supported so this will definitely not result in infinite recursion.
      case Union.TYPE -> castedField(field, ((Union) type).chooseType(), useExpensiveSaferCasting);
      default -> throw new IllegalArgumentException("Unsupported AirbyteType: " + type);
    };
  }

  @Override
  protected List<Field<?>> extractRawDataFields(final LinkedHashMap<ColumnId, AirbyteType> columns, final boolean useExpensiveSaferCasting) {
    return columns
        .entrySet()
        .stream()
        .map(column -> castedField(
            field(quotedName(COLUMN_NAME_DATA, column.getKey().getOriginalName())),
            column.getValue(),
            useExpensiveSaferCasting).as(column.getKey().getName()))
        .collect(Collectors.toList());
  }

  private Field<String> jsonTypeOf(final Field<?> field) {
    return function("JSON_TYPEOF", SQLDataType.VARCHAR, field);
  }

  private Field<String> jsonSerialize(final Field<?> field) {
    return function("JSON_SERIALIZE", SQLDataType.VARCHAR, field);
  }

  /**
   * Redshift ARRAY_CONCAT supports only 2 arrays. Iteratively nest ARRAY_CONCAT to support more than
   * 2
   *
   * @param arrays
   * @return
   */
  Field<?> arrayConcatStmt(final List<Field<?>> arrays) {
    if (arrays.isEmpty()) {
      return field("ARRAY()"); // Return an empty string if the list is empty
    }

    Field<?> result = arrays.get(0);
    for (int i = 1; i < arrays.size(); i++) {
      // We lose some nice indentation but thats ok. Queryparts
      // are intentionally rendered here to avoid deep stack for function sql rendering.
      result = field(getDslContext().renderNamedOrInlinedParams(function("ARRAY_CONCAT", getSuperType(), result, arrays.get(i))));
    }
    return result;
  }

  Field<?> toCastingErrorCaseStmt(final ColumnId column, final AirbyteType type) {
    final Field<?> field = field(quotedName(COLUMN_NAME_DATA, column.getOriginalName()));
    // Just checks if data is not null but casted data is null. This also accounts for conditional
    // casting result of array and struct.
    // TODO: Timestamp format issues can result in null values when cast, add regex check if destination
    // supports regex functions.
    return field(CASE_STATEMENT_SQL_TEMPLATE,
        field.isNotNull().and(castedField(field, type, true).as(column.getName()).isNull()),
        function("ARRAY", getSuperType(),
            function("JSON_PARSE", getSuperType(), val(
                "{\"field\": \"" + column.getName() + "\", "
                    + "\"change\": \"" + Change.NULLED.value() + "\", "
                    + "\"reason\": \"" + Reason.DESTINATION_TYPECAST_ERROR + "\"}"))),
        field("ARRAY()"));
  }

  @Override
  protected Field<?> buildAirbyteMetaColumn(final LinkedHashMap<ColumnId, AirbyteType> columns) {
    final List<Field<?>> dataFields = columns
        .entrySet()
        .stream()
        .map(column -> toCastingErrorCaseStmt(column.getKey(), column.getValue()))
        .collect(Collectors.toList());
    final Condition rawTableAirbyteMetaExists =
        field(quotedName(COLUMN_NAME_AB_META)).isNotNull()
            .and(function("IS_OBJECT", SQLDataType.BOOLEAN, field(quotedName(COLUMN_NAME_AB_META))))
            .and(field(quotedName(COLUMN_NAME_AB_META, AIRBYTE_META_COLUMN_CHANGES_KEY)).isNotNull())
            .and(function("IS_ARRAY", SQLDataType.BOOLEAN, field(quotedName(COLUMN_NAME_AB_META, AIRBYTE_META_COLUMN_CHANGES_KEY))));
    final Field<?> airbyteMetaChangesArray = function("ARRAY_CONCAT", getSuperType(),
        arrayConcatStmt(dataFields), field(CASE_STATEMENT_SQL_TEMPLATE,
            rawTableAirbyteMetaExists,
            field(quotedName(COLUMN_NAME_AB_META, AIRBYTE_META_COLUMN_CHANGES_KEY)),
            field("ARRAY()")));
    return function("OBJECT", getSuperType(), val(AIRBYTE_META_COLUMN_CHANGES_KEY), airbyteMetaChangesArray).as(COLUMN_NAME_AB_META);

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

  @Override
  protected Condition cdcDeletedAtNotNullCondition() {
    return field(name(COLUMN_NAME_AB_LOADED_AT)).isNotNull()
        .and(function("JSON_TYPEOF", SQLDataType.VARCHAR, field(quotedName(COLUMN_NAME_DATA, getCdcDeletedAtColumn().getName())))
            .ne("null"));
  }

  @Override
  protected Field<Timestamp> currentTimestamp() {
    return function("GETDATE", SQLDataType.TIMESTAMP);
  }

  @Override
  public boolean shouldRetry(final Exception e) {
    return false;
  }

}
