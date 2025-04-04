/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.yellowbrick.typing_deduping;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_META;
import static org.jooq.impl.DSL.case_;
import static org.jooq.impl.DSL.cast;
import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.function;
import static org.jooq.impl.DSL.list;
import static org.jooq.impl.DSL.name;
import static org.jooq.impl.DSL.quotedName;
import static org.jooq.impl.DSL.rowNumber;
import static org.jooq.impl.DSL.val;

import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.Array;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.Struct;
import io.airbyte.integrations.destination.yellowbrick.YellowbrickSqlOperations;
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

public class YellowbrickSqlGenerator extends JdbcSqlGenerator {

  public YellowbrickSqlGenerator(final NamingConventionTransformer namingTransformer) {
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
        getNamingTransformer().getNamespace(namespace),
        getNamingTransformer().convertStreamName(name),
        getNamingTransformer().getNamespace(rawNamespaceOverride).toLowerCase(),
        getNamingTransformer().convertStreamName(StreamId.concatenateRawTableName(namespace, name)).toLowerCase(),
        namespace,
        name);
  }

  /**
   * This method returns Jooq internal DataType, Ideally we need to implement DataType interface with
   * all the required fields for Jooq typed query construction
   *
   * @return
   */
  private DataType<?> getJSONBType() {
    return SQLDataType.JSONB;
  }

  @Override
  protected DataType<?> getStructType() {
    return getJSONBType();
  }

  @Override
  protected DataType<?> getArrayType() {
    return getJSONBType();
  }

  @Override
  protected DataType<?> getWidestType() {
    return getJSONBType();
  }

  @Override
  protected SQLDialect getDialect() {
    return SQLDialect.POSTGRES;
  }

  @Override
  public DataType<?> toDialectType(AirbyteProtocolType airbyteProtocolType) {
    if (airbyteProtocolType.equals(AirbyteProtocolType.STRING)) {
      return SQLDataType.VARCHAR(YellowbrickSqlOperations.YELLOWBRICK_VARCHAR_MAX_BYTE_SIZE);
    }
    return super.toDialectType(airbyteProtocolType);
  }

  @Override
  protected List<Field<?>> extractRawDataFields(final LinkedHashMap<ColumnId, AirbyteType> columns, final boolean useExpensiveSaferCasting) {
    return columns
        .entrySet()
        .stream()
        .map(column -> castedField(
            extractColumnAsJson(column.getKey()),
            column.getValue(),
            column.getKey().getName(),
            useExpensiveSaferCasting))
        .collect(Collectors.toList());
  }

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
    final DataType<?> dialectType = toDialectType(type);
    // jsonb can't directly cast to most types, so convert to text first.
    // also convert jsonb null to proper sql null.
    final Field<String> extractAsText = case_()
        .when(field.isNull().or(jsonTypeof(field).eq("null")), val((String) null))
        .else_(cast(field, SQLDataType.VARCHAR(YellowbrickSqlOperations.YELLOWBRICK_VARCHAR_MAX_BYTE_SIZE)));
    return cast(extractAsText, dialectType);
  }

  @Override
  protected Field<?> buildAirbyteMetaColumn(final LinkedHashMap<ColumnId, AirbyteType> columns) {
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
        list(dataFieldErrors));

    // Constructing the JSON object with the "errors" key
    return cast(field(
        "json_object_str('errors', {0})",
        String.class,
        errorsArray).as(COLUMN_NAME_AB_META), SQLDataType.JSONB);
  }

  private Field<String> toCastingErrorCaseStmt(final ColumnId column, final AirbyteType type) {
    final Field<?> extract = extractColumnAsJson(column);
    if (type instanceof Struct) {
      // If this field is a struct, verify that the raw data is an object or null.
      return case_()
          .when(
              extract.isNotNull()
                  .and(jsonTypeof(extract).notIn("object", "null")),
              val("Problem with `" + column.getOriginalName() + "`"))
          .else_(val((String) null));
    } else if (type instanceof Array) {
      // Do the same for arrays.
      return case_()
          .when(
              extract.isNotNull()
                  .and(jsonTypeof(extract).notIn("array", "null")),
              val("Problem with `" + column.getOriginalName() + "`"))
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
              val("Problem with `" + column.getOriginalName() + "`"))
          .else_(val((String) null));
    }
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

  private Field<?> extractColumnAsJson(ColumnId column) {
    String jsonKey = column.getOriginalName();
    String dataCol = JavaBaseConstants.COLUMN_NAME_DATA;
    String rawSql = String.format("\"%s\"::JSONB:$.%s NULL ON ERROR", dataCol, jsonKey);
    return field(rawSql, SQLDataType.JSONB);
  }

  private Field<String> jsonTypeof(Field<?> jsonField) {
    return function("JSON_TYPEOF", SQLDataType.VARCHAR, jsonField);
  }

}
