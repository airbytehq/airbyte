/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.yellowbrick.typing_deduping;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_META;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_DATA;
import static org.jooq.impl.DSL.case_;
import static org.jooq.impl.DSL.cast;
import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.list;
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
        namingTransformer.getNamespace(namespace),
        namingTransformer.convertStreamName(name),
        namingTransformer.getNamespace(rawNamespaceOverride).toLowerCase(),
        namingTransformer.convertStreamName(StreamId.concatenateRawTableName(namespace, name)).toLowerCase(),
        namespace,
        name);
  }

  /**
   * This method returns Jooq internal DataType, Ideally we need to implement DataType interface with
   * all the required fields for Jooq typed query construction
   *
   * @return
   */
  private DataType<?> getSuperType() {
    return SQLDataType.VARCHAR(YellowbrickSqlOperations.YELLOWBRICK_VARCHAR_MAX_BYTE_SIZE);
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
            extractColumnAsJson(column.getKey(), column.getValue()),
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
          SQLDataType.VARCHAR(YellowbrickSqlOperations.YELLOWBRICK_VARCHAR_MAX_BYTE_SIZE));
    } else if (type instanceof Array) {
      // Do the same for arrays.
      return cast(
          case_()
              .when(field.isNull().or(jsonTypeof(field).ne("array")), val((Object) null))
              .else_(field),
          SQLDataType.VARCHAR(YellowbrickSqlOperations.YELLOWBRICK_VARCHAR_MAX_BYTE_SIZE));
    } else if (type == AirbyteProtocolType.UNKNOWN) {
      return cast(field, SQLDataType.VARCHAR(YellowbrickSqlOperations.YELLOWBRICK_VARCHAR_MAX_BYTE_SIZE));
    } else if (type == AirbyteProtocolType.STRING) {
      return field;
    } else {
      final DataType<?> dialectType = toDialectType(type);
      // jsonb can't directly cast to most types, so convert to text first.
      // also convert jsonb null to proper sql null.
      final Field<String> extractAsText = case_()
          .when(field.isNull().or(jsonTypeof(field).eq("null")), val((String) null))
          .else_(cast(field, SQLDataType.VARCHAR(YellowbrickSqlOperations.YELLOWBRICK_VARCHAR_MAX_BYTE_SIZE)));
      return cast(extractAsText, dialectType);
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
        errorsArray).as(COLUMN_NAME_AB_META);
  }

  private Field<String> toCastingErrorCaseStmt(final ColumnId column, final AirbyteType type) {
    final Field<Object> extract = extractColumnAsJson(column, type);
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
        .and(jsonTypeof(extractColumnAsJson(cdcDeletedAtColumn, null)).ne("null"));
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

  /**
   * Extract a raw field, leaving it as json
   */
  private Field<Object> extractColumnAsJson(final ColumnId column, final AirbyteType type) {
    if (type != null && type instanceof Struct) {
      String objectPattern = String.format("({.*?})");
      return field("SUBSTRING({0} FROM {1})", name(COLUMN_NAME_DATA), objectPattern);
    } else if (type != null && type instanceof Array) {
      String arrayPattern = String.format(":\\s*(\\[.*?\\])");
      return field("SUBSTRING({0} FROM '\"' || {1} || '\"' || {2})", name(COLUMN_NAME_DATA), val(column.originalName()), arrayPattern);
    } else {
      return field("json_lookup({0}, '/' || {1}, 'jpointer_simdjson')", name(COLUMN_NAME_DATA), val(column.originalName()));
    }
  }

  private Field<String> jsonTypeof(Field<?> jsonField) {
    Field<String> field = cast(jsonField, SQLDataType.VARCHAR(YellowbrickSqlOperations.YELLOWBRICK_VARCHAR_MAX_BYTE_SIZE));
    return case_()
        .when(field.like("{%}"), val("object"))
        .when(field.like("[%]"), val("array"))
        .when(field.like("\"%\""), val("string"))
        .when(field.likeRegex("-?[0-9]+(\\.[0-9]+)?"), val("number"))
        .when(field.equalIgnoreCase("true").or(field.equalIgnoreCase("false")), val("boolean"))
        .when(field.equal("null"), val("null"));
  }

}
