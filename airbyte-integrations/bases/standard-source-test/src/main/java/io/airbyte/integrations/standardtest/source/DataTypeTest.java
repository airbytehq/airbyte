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

package io.airbyte.integrations.standardtest.source;

import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.Field;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class DataTypeTest {

  private static final String DEFAULT_CREATE_TABLE_SQL = "CREATE TABLE %1$s(id integer primary key, test_column %2$s);";
  private static final String DEFAULT_INSERT_SQL = "INSERT INTO %1$s VALUES (%2$s, %3$s);";

  private final String sourceType;
  private final Field.JsonSchemaPrimitive airbyteType;
  private final List<String> values;
  private final String createTablePatternSQL;
  private final String insertPatternSQL;
  private final String fullSourceDataType;
  private long testNumber;

  DataTypeTest(String sourceType,
               Field.JsonSchemaPrimitive airbyteType,
               List<String> values,
               String createTablePatternSQL,
               String insertPatternSQL,
               String fullSourceDataType) {
    this.sourceType = sourceType;
    this.airbyteType = airbyteType;
    this.values = values;
    this.createTablePatternSQL = createTablePatternSQL;
    this.insertPatternSQL = insertPatternSQL;
    this.fullSourceDataType = fullSourceDataType;
  }

  /**
   * The builder allows to setup any comprehensive data type test.
   *
   * @param sourceType name of the source data type. Duplicates by name will be tested independently
   *        from each others. Note that this name will be used for connector setup and table creation.
   *        If source syntax requires more details (E.g. "varchar" type requires length
   *        "varchar(50)"), you can additionally set custom data type syntax by
   *        {@link DataTypeTestBuilder#fullSourceDataType(String)} method.
   * @param airbyteType corresponding Airbyte data type. It requires for proper configuration
   *        {@link ConfiguredAirbyteStream}
   * @return builder for setup comprehensive test
   */
  public static DataTypeTestBuilder builder(String sourceType, Field.JsonSchemaPrimitive airbyteType) {
    return new DataTypeTestBuilder(sourceType, airbyteType);
  }

  public static class DataTypeTestBuilder {

    private final String sourceType;
    private final Field.JsonSchemaPrimitive airbyteType;
    private final List<String> values = new ArrayList<>();
    private String createTablePatternSQL;
    private String insertPatternSQL;
    private String fullSourceDataType;

    DataTypeTestBuilder(String sourceType, Field.JsonSchemaPrimitive airbyteType) {
      this.sourceType = sourceType;
      this.airbyteType = airbyteType;
      this.createTablePatternSQL = DEFAULT_CREATE_TABLE_SQL;
      this.insertPatternSQL = DEFAULT_INSERT_SQL;
      this.fullSourceDataType = sourceType;
    }

    /**
     * Set custom the create table script pattern. Use it if you source uses untypical table creation
     * sql. Default patter described {@link #DEFAULT_CREATE_TABLE_SQL} Note! The patter should contains
     * two String place holders for the table name and data type.
     *
     * @param createTablePatternSQL creation table sql pattern
     * @return builder
     */
    public DataTypeTestBuilder createTablePatternSQL(String createTablePatternSQL) {
      this.createTablePatternSQL = createTablePatternSQL;
      return this;
    }

    /**
     * Set custom the insert record script pattern. Use it if you source uses untypical insert record
     * sql. Default patter described {@link #DEFAULT_INSERT_SQL} Note! The patter should contains two
     * String place holders for the table name and value.
     *
     * @param insertPatternSQL creation table sql pattern
     * @return builder
     */
    public DataTypeTestBuilder insertPatternSQL(String insertPatternSQL) {
      this.insertPatternSQL = insertPatternSQL;
      return this;
    }

    /**
     * Allows to set extended data type for the table creation. E.g. The "varchar" type requires in
     * MySQL requires length. In this case fullSourceDataType will be "varchar(50)".
     *
     * @param fullSourceDataType actual string for the column data type description
     * @return builder
     */
    public DataTypeTestBuilder fullSourceDataType(String fullSourceDataType) {
      this.fullSourceDataType = fullSourceDataType;
      return this;
    }

    /**
     * Adds value(s) to the scope of a corresponding test. The values will be inserted into the created
     * table. Note! The value will be inserted into the insert script without any transformations. Make
     * sure that the value is in line with the source syntax.
     *
     * @param insertValue test value
     * @return builder
     */
    public DataTypeTestBuilder addInsertValue(String... insertValue) {
      this.values.addAll(Arrays.asList(insertValue));
      return this;
    }

    public DataTypeTest build() {
      return new DataTypeTest(sourceType, airbyteType, values, createTablePatternSQL, insertPatternSQL, fullSourceDataType);
    }

  }

  public void setTestNumber(long testNumber) {
    this.testNumber = testNumber;
  }

  public String getSourceType() {
    return sourceType;
  }

  public Field.JsonSchemaPrimitive getAirbyteType() {
    return airbyteType;
  }

  public String getName() {
    return "test_" + testNumber + "_" + sourceType;
  }

  public String getCreateSQL() {
    return String.format(createTablePatternSQL, getName(), fullSourceDataType);
  }

  public List<String> getInsertSQLs() {
    List<String> insertSQLs = new ArrayList<>();
    int rowId = 1;
    for (String value : values) {
      insertSQLs.add(String.format(insertPatternSQL, getName(), rowId++, value));
    }
    return insertSQLs;
  }

}
