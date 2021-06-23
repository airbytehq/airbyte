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

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.FieldList;
import com.google.cloud.bigquery.FieldValue;
import com.google.cloud.bigquery.FieldValueList;
import com.google.cloud.bigquery.LegacySQLTypeName;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.DataTypeUtils;
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
      case STRUCT -> node.put(fieldName, ""); // @TODO impl
      case ARRAY -> node.put(fieldName, ""); // @TODO impl
      case TIMESTAMP -> node.put(fieldName, ""); // @TODO impl
      case DATE -> node.put(fieldName, DataTypeUtils.toISO8601String(getDateValue(fieldValue)));
      case TIME -> node.put(fieldName, ""); // @TODO impl
      case DATETIME -> node.put(fieldName, ""); // @TODO impl
      case GEOGRAPHY -> node.put(fieldName, ""); // @TODO impl
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
  /*
   * final int columnTypeInt = r.getMetaData().getColumnType(i); final String columnName =
   * r.getMetaData().getColumnName(i); final JDBCType columnType = safeGetJdbcType(columnTypeInt);
   *
   * // https://www.cis.upenn.edu/~bcpierce/courses/629/jdkdocs/guide/jdbc/getstart/mapping.doc.html
   * switch (columnType) { case BIT, BOOLEAN -> o.put(columnName, r.getBoolean(i)); case TINYINT,
   * SMALLINT -> o.put(columnName, r.getShort(i)); case INTEGER -> putInteger(o, columnName, r, i);
   * case BIGINT -> o.put(columnName, nullIfInvalid(() -> r.getLong(i))); case FLOAT, DOUBLE ->
   * o.put(columnName, nullIfInvalid(() -> r.getDouble(i), Double::isFinite)); case REAL ->
   * o.put(columnName, nullIfInvalid(() -> r.getFloat(i), Float::isFinite)); case NUMERIC, DECIMAL ->
   * o.put(columnName, nullIfInvalid(() -> r.getBigDecimal(i))); case CHAR, VARCHAR, LONGVARCHAR ->
   * o.put(columnName, r.getString(i)); case DATE -> o.put(columnName, toISO8601String(r.getDate(i)));
   * case TIME -> o.put(columnName, toISO8601String(r.getTime(i))); case TIMESTAMP -> { //
   * https://www.cis.upenn.edu/~bcpierce/courses/629/jdkdocs/guide/jdbc/getstart/mapping.doc.html
   * final Timestamp t = r.getTimestamp(i); java.util.Date d = new java.util.Date(t.getTime() +
   * (t.getNanos() / 1000000)); o.put(columnName, toISO8601String(d)); } case BLOB, BINARY, VARBINARY,
   * LONGVARBINARY -> o.put(columnName, r.getBytes(i)); default -> o.put(columnName, r.getString(i));
   * }
   */

}
