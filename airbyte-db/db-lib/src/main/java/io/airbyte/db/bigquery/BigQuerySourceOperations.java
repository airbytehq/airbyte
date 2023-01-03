/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.bigquery;

import static io.airbyte.db.DataTypeUtils.returnNullIfInvalid;
import static io.airbyte.db.DataTypeUtils.toISO8601String;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ContainerNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.FieldList;
import com.google.cloud.bigquery.FieldValue;
import com.google.cloud.bigquery.FieldValue.Attribute;
import com.google.cloud.bigquery.QueryParameterValue;
import com.google.cloud.bigquery.StandardSQLTypeName;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.DataTypeUtils;
import io.airbyte.db.SourceOperations;
import io.airbyte.db.util.JsonUtil;
import io.airbyte.protocol.models.JsonSchemaType;
import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Collections;
import java.util.Date;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQuerySourceOperations implements SourceOperations<BigQueryResultSet, StandardSQLTypeName> {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQuerySourceOperations.class);

  private final DateFormat BIG_QUERY_DATE_FORMAT = new SimpleDateFormat("yyyy-MM-dd");
  private final DateFormat BIG_QUERY_DATETIME_FORMAT = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss");
  private final DateFormat BIG_QUERY_TIMESTAMP_FORMAT = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSSSS z");

  @Override
  public JsonNode rowToJson(final BigQueryResultSet bigQueryResultSet) {
    final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
    bigQueryResultSet.getFieldList().forEach(field -> setJsonField(field, bigQueryResultSet.getRowValues().get(field.getName()), jsonNode));
    return jsonNode;
  }

  private void fillObjectNode(final String fieldName, final StandardSQLTypeName fieldType, final FieldValue fieldValue, final ContainerNode<?> node) {
    switch (fieldType) {
      case BOOL -> JsonUtil.putBooleanValueIntoJson(node, fieldValue.getBooleanValue(), fieldName);
      case INT64 -> JsonUtil.putLongValueIntoJson(node, fieldValue.getLongValue(), fieldName);
      case FLOAT64 -> JsonUtil.putDoubleValueIntoJson(node, fieldValue.getDoubleValue(), fieldName);
      case NUMERIC -> JsonUtil.putBigDecimalValueIntoJson(node, fieldValue.getNumericValue(), fieldName);
      case BIGNUMERIC -> JsonUtil.putBigDecimalValueIntoJson(node, returnNullIfInvalid(fieldValue::getNumericValue), fieldName);
      case STRING, TIME -> JsonUtil.putStringValueIntoJson(node, fieldValue.getStringValue(), fieldName);
      case BYTES -> JsonUtil.putBytesValueIntoJson(node, fieldValue.getBytesValue(), fieldName);
      case DATE -> JsonUtil.putStringValueIntoJson(node, toISO8601String(getDateValue(fieldValue, BIG_QUERY_DATE_FORMAT)), fieldName);
      case DATETIME -> JsonUtil.putStringValueIntoJson(node, toISO8601String(getDateValue(fieldValue, BIG_QUERY_DATETIME_FORMAT)), fieldName);
      case TIMESTAMP -> JsonUtil.putStringValueIntoJson(node, toISO8601String(fieldValue.getTimestampValue() / 1000), fieldName);
      default -> JsonUtil.putStringValueIntoJson(node, fieldValue.getStringValue(), fieldName);
    }
  }

  private void setJsonField(final Field field, final FieldValue fieldValue, final ObjectNode node) {
    final String fieldName = field.getName();
    if (fieldValue.getAttribute().equals(Attribute.PRIMITIVE)) {
      if (fieldValue.isNull()) {
        node.put(fieldName, (String) null);
      } else {
        fillObjectNode(fieldName, field.getType().getStandardType(), fieldValue, node);
      }
    } else if (fieldValue.getAttribute().equals(Attribute.REPEATED)) {
      final ArrayNode arrayNode = node.putArray(fieldName);
      final StandardSQLTypeName fieldType = field.getType().getStandardType();
      final FieldList subFields = field.getSubFields();
      // Array of primitive
      if (subFields == null || subFields.isEmpty()) {
        fieldValue.getRepeatedValue().forEach(arrayFieldValue -> fillObjectNode(fieldName, fieldType, arrayFieldValue, arrayNode));
        // Array of records
      } else {
        for (final FieldValue arrayFieldValue : fieldValue.getRepeatedValue()) {
          int count = 0; // named get doesn't work here for some reasons.
          final ObjectNode newNode = arrayNode.addObject();
          for (final Field repeatedField : subFields) {
            setJsonField(repeatedField, arrayFieldValue.getRecordValue().get(count++),
                newNode);
          }
        }
      }
    } else if (fieldValue.getAttribute().equals(Attribute.RECORD)) {
      final ObjectNode newNode = node.putObject(fieldName);
      final FieldList subFields = field.getSubFields();
      try {
        // named get doesn't work here with nested arrays and objects; index is the only correlation between
        // field and field value
        if (subFields != null && !subFields.isEmpty()) {
          for (int i = 0; i < subFields.size(); i++) {
            setJsonField(field.getSubFields().get(i), fieldValue.getRecordValue().get(i), newNode);
          }
        }
      } catch (final UnsupportedOperationException e) {
        LOGGER.error("Failed to parse Object field with name: {}, {}", fieldName, e.getMessage());
      }
    }
  }

  public Date getDateValue(final FieldValue fieldValue, final DateFormat dateFormat) {
    Date parsedValue = null;
    final String value = fieldValue.getStringValue();
    try {
      parsedValue = dateFormat.parse(value);
    } catch (final ParseException e) {
      LOGGER.error("Fail to parse date value : " + value + ". Null is returned.");
    }
    return parsedValue;
  }

  @Override
  public JsonSchemaType getAirbyteType(final StandardSQLTypeName bigQueryType) {
    return switch (bigQueryType) {
      case BOOL -> JsonSchemaType.BOOLEAN;
      case INT64 -> JsonSchemaType.INTEGER;
      case FLOAT64, NUMERIC, BIGNUMERIC -> JsonSchemaType.NUMBER;
      case STRING, BYTES, TIMESTAMP, DATE, TIME, DATETIME -> JsonSchemaType.STRING;
      case ARRAY -> JsonSchemaType.ARRAY;
      case STRUCT -> JsonSchemaType.OBJECT;
      default -> JsonSchemaType.STRING;
    };
  }

  private String getFormattedValue(final StandardSQLTypeName paramType, final String paramValue) {
    try {
      return switch (paramType) {
        case DATE -> BIG_QUERY_DATE_FORMAT.format(DataTypeUtils.getDateFormat().parse(paramValue));
        case DATETIME -> BIG_QUERY_DATETIME_FORMAT
            .format(DataTypeUtils.getDateFormat().parse(paramValue));
        case TIMESTAMP -> BIG_QUERY_TIMESTAMP_FORMAT
            .format(DataTypeUtils.getDateFormat().parse(paramValue));
        default -> paramValue;
      };
    } catch (final ParseException e) {
      throw new RuntimeException("Fail to parse value " + paramValue + " to type " + paramType.name(), e);
    }
  }

  public QueryParameterValue getQueryParameter(final StandardSQLTypeName paramType, final String paramValue) {
    final String value = getFormattedValue(paramType, paramValue);
    LOGGER.info("Query parameter for set : " + value + ". Type: " + paramType.name());
    return QueryParameterValue.newBuilder().setType(paramType).setValue(value).build();
  }

}
