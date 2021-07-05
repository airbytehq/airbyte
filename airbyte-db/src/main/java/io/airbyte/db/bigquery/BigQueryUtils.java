/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.db.bigquery;

import static io.airbyte.db.DataTypeUtils.nullIfInvalid;
import static io.airbyte.db.DataTypeUtils.toISO8601String;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.FieldList;
import com.google.cloud.bigquery.FieldValue;
import com.google.cloud.bigquery.FieldValue.Attribute;
import com.google.cloud.bigquery.FieldValueList;
import com.google.cloud.bigquery.LegacySQLTypeName;
import com.google.cloud.bigquery.QueryParameterValue;
import com.google.cloud.bigquery.StandardSQLTypeName;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Collections;
import java.util.Date;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryUtils.class);

  public static final String BIG_QUERY_DATE_FORMAT = "YYYY-MM-DD";

  public static JsonNode rowToJson(FieldValueList rowValues, FieldList fieldList) {
    ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
    fieldList.forEach(field -> setJsonField(field, rowValues.get(field.getName()), jsonNode));
    return jsonNode;
  }

  private static void setJsonField(Field field, FieldValue fieldValue, ObjectNode node) {
    if (fieldValue.getAttribute().equals(Attribute.PRIMITIVE)) {
      LegacySQLTypeName fieldType = field.getType();
      String fieldName = field.getName();
      switch (fieldType.getStandardType()) {
        case BOOL -> node.put(fieldName, fieldValue.getBooleanValue());
        case INT64 -> node.put(fieldName, fieldValue.getLongValue());
        case FLOAT64 -> node.put(fieldName, fieldValue.getDoubleValue());
        case NUMERIC -> node.put(fieldName, fieldValue.getNumericValue());
        case BIGNUMERIC -> node.put(fieldName, nullIfInvalid(fieldValue::getNumericValue));
        case STRING -> node.put(fieldName, fieldValue.getStringValue());
        case BYTES -> node.put(fieldName, fieldValue.getBytesValue());
        case TIMESTAMP, DATE, TIME, DATETIME -> node
            .put(fieldName, toISO8601String(fieldValue.getTimestampValue()));
        default -> node.put(fieldName, fieldValue.getStringValue());
      }
    }
  }

  public static Date getDateValue(FieldValue fieldValue) {
    Date parsedValue = null;
    String value = fieldValue.getStringValue();
    try {
      parsedValue = new SimpleDateFormat(BIG_QUERY_DATE_FORMAT).parse(value);
    } catch (ParseException e) {
      LOGGER.error("Fail to parse date value : " + value + ". Null is returned.");
    }
    return parsedValue;
  }

  public static JsonSchemaPrimitive getType(StandardSQLTypeName bigQueryType) {
    return switch (bigQueryType) {
      case BOOL -> JsonSchemaPrimitive.BOOLEAN;
      case INT64, FLOAT64, NUMERIC, BIGNUMERIC -> JsonSchemaPrimitive.NUMBER;
      case STRING, BYTES, TIMESTAMP, DATE, TIME, DATETIME -> JsonSchemaPrimitive.STRING;
      default -> JsonSchemaPrimitive.STRING;
    };
  }

  // @TODO probably we need a reverse value transformation. especially for time and date types.
  public static QueryParameterValue getQueryParameter(StandardSQLTypeName paramType, String paramValue) {
    return QueryParameterValue.newBuilder().setType(paramType).setValue(paramValue).build();
  }

}
