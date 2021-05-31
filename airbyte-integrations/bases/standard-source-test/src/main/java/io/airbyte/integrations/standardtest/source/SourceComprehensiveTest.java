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

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.protocol.models.*;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.SyncMode;
import io.airbyte.db.Database;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.*;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.*;

public abstract class SourceComprehensiveTest extends SourceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(SourceComprehensiveTest.class);
  private static final String DEFAULT_CREATE_TABLE_SQL = "CREATE TABLE %1$s(id integer primary key, test_column %2$s);";
  private static final String DEFAULT_INSERT_SQL = "INSERT INTO %1$s VALUES (%2$s, %3$s);";

  private final List<DataTypeTest> dataTypeTests = new ArrayList<>();

  /**
   * Setup the test database. All tables and data described in the registered tests will be put there.
   * @return             configured test database
   * @throws Exception - might throw any exception during initialization.
   */
  protected abstract Database setupDatabase() throws Exception;

  /**
   * Put all required tests here using method {@link #addDataTypeTest(DataTypeTest)}
   */
  protected abstract void initTests();

  @Override
  protected void setup(TestDestinationEnv testEnv) throws Exception {
    setupDatabaseInternal();
  }

  /**
   * Configuring all streams in the input catalog to full refresh mode, verifies that a read operation
   * produces some RECORD messages.
   */
  @Test
  public void testDataTypes() throws Exception {
    ConfiguredAirbyteCatalog catalog = getConfiguredCatalog();
    List<AirbyteMessage> allMessages = runRead(catalog);
    LOGGER.info("Size: " + allMessages.size());
    final List<AirbyteMessage> recordMessages = allMessages.stream().filter(m -> m.getType() == Type.RECORD).collect(Collectors.toList());

    recordMessages.forEach(msg -> LOGGER.info(msg.toString()));

    assertFalse(recordMessages.isEmpty(), "Expected a full refresh sync to produce records");

    allMessages = runRead(catalog);
    LOGGER.info("Size: " + allMessages.size());
    recordMessages.forEach(msg -> LOGGER.info(msg.toString()));
  }

  /**
   * Creates all tables and insert data described in the registered data type tests.
   * @throws Exception  might raise exception if configuration goes wrong or tables creation/insert scripts failed.
   */
  private void setupDatabaseInternal() throws Exception {
    Database database = setupDatabase();

    initTests();

    for (DataTypeTest test : dataTypeTests) {
      database.query(ctx -> {
        ctx.fetch(test.getCreateSQL());
        LOGGER.info("Table " + test.getName() + " is created.");
        test.getInsertSQLs().forEach(ctx::fetch);
        LOGGER.info("Values " + test.values + " are inserted into " + test.getName());
        return null;
      });
    }

    database.close();
  }

  /**
   * Configures streams for all registered data type tests.
   * @return configured catalog
   */
  private ConfiguredAirbyteCatalog getConfiguredCatalog() throws Exception {
    final JsonNode config = getConfig();

    return new ConfiguredAirbyteCatalog().withStreams(
            dataTypeTests
                    .stream()
                    .map(test ->
                            new ConfiguredAirbyteStream()
                                    .withSyncMode(SyncMode.INCREMENTAL)
                                    .withCursorField(Lists.newArrayList("id"))
                                    .withDestinationSyncMode(DestinationSyncMode.APPEND)
                                    .withStream(CatalogHelpers.createAirbyteStream(
                                            String.format("%s", test.getName()),
                                            String.format("%s", config.get("database").asText()),
                                            Field.of("id", Field.JsonSchemaPrimitive.NUMBER),
                                            Field.of("test_column", test.airbyteType))
                                            .withSourceDefinedCursor(true)
                                            .withSourceDefinedPrimaryKey(List.of(List.of("id")))
                                            .withSupportedSyncModes(
                                                    Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))))
                    .collect(Collectors.toList())
    );
  }

  /**
   * Register your test in the run scope.
   * For each test will be created a table with one column of specified type.
   * Note! If you register more than one test with the same type name, they will be run as independent tests with own
   * streams.
   * @param test comprehensive data type test built by {@link DataTypeTestBuilder}
   */
  public void addDataTypeTest(DataTypeTest test) {
    dataTypeTests.add(test);
    test.testNumber = dataTypeTests.stream().filter(t -> t.sourceType.equals(test.sourceType)).count();
  }

  /**
   * The builder allows to setup any comprehensive data type test.
   * @param sourceType  name of the source data type. Duplicates by name will be tested independently from each others.
   *                    Note that this name will be used for connector setup and table creation.
   *                    If source syntax requires more details (E.g. "varchar" type requires length "varchar(50)"),
   *                    you can additionally set custom data type syntax by {@link DataTypeTestBuilder#setFullSourceDataType(String)} method.
   * @param airbyteType corresponding Airbyte data type. It requires for proper configuration {@link ConfiguredAirbyteStream}
   * @return            builder for setup comprehensive test
   */
  public DataTypeTestBuilder dataTypeTestBuilder(String sourceType, Field.JsonSchemaPrimitive airbyteType) {
    return new DataTypeTestBuilder(sourceType, airbyteType);
  }

  public class DataTypeTestBuilder {

    private final DataTypeTest dataTypeTest;

    private DataTypeTestBuilder(String sourceType, Field.JsonSchemaPrimitive airbyteType) {
      this.dataTypeTest = new DataTypeTest();
      this.dataTypeTest.sourceType = sourceType;
      this.dataTypeTest.airbyteType = airbyteType;
      this.dataTypeTest.createTablePatternSQL = DEFAULT_CREATE_TABLE_SQL;
      this.dataTypeTest.insertPatternSQL = DEFAULT_INSERT_SQL;
      this.dataTypeTest.fullSourceDataType = sourceType;
    }

    /**
     * Set custom the create table script pattern. Use it if you source uses untypical table creation sql.
     * Default patter described {@link #DEFAULT_CREATE_TABLE_SQL}
     * Note! The patter should contains two String place holders for the table name and data type.
     * @param createTablePatternSQL creation table sql pattern
     * @return                      builder
     */
    public DataTypeTestBuilder setCreateTablePatternSQL(String createTablePatternSQL) {
      this.dataTypeTest.createTablePatternSQL = createTablePatternSQL;
      return this;
    }

    /**
     * Set custom the insert record script pattern. Use it if you source uses untypical insert record sql.
     * Default patter described {@link #DEFAULT_INSERT_SQL}
     * Note! The patter should contains two String place holders for the table name and value.
     * @param insertPatternSQL creation table sql pattern
     * @return                 builder
     */
    public DataTypeTestBuilder setInsertPatternSQL(String insertPatternSQL) {
      this.dataTypeTest.insertPatternSQL = insertPatternSQL;
      return this;
    }

    /**
     * Allows to set extended data type for the table creation.
     * E.g. The "varchar" type requires in MySQL requires length. In this case fullSourceDataType will be "varchar(50)".
     * @param fullSourceDataType  actual string for the column data type description
     * @return                    builder
     */
    public DataTypeTestBuilder setFullSourceDataType(String fullSourceDataType) {
      this.dataTypeTest.fullSourceDataType = fullSourceDataType;
      return this;
    }

    /**
     * Adds value(s) to the scope of a corresponding test. The values will be inserted into the created table.
     * Note! The value will be inserted into the insert script without any transformations. Make sure that the value is
     * in line with the source syntax.
     * @param insertValue test value
     * @return            builder
     */
    public DataTypeTestBuilder addInsertValue(String...insertValue) {
      this.dataTypeTest.values.addAll(Arrays.asList(insertValue));
      return this;
    }

    public DataTypeTest build() {
      return dataTypeTest;
    }

  }

  private class DataTypeTest {

    private String sourceType;
    private Field.JsonSchemaPrimitive airbyteType;
    private final List<String> values = new ArrayList<>();
    private String createTablePatternSQL;
    private String insertPatternSQL;
    private long testNumber;
    private String fullSourceDataType;

    private String getName() {
      return "test_" + testNumber + "_" + sourceType;
    }

    private String getCreateSQL() {
      return String.format(createTablePatternSQL, getName(), fullSourceDataType);
    }

    private List<String> getInsertSQLs() {
      List<String> insertSQLs = new ArrayList<>();
      int rowId = 1;
      for (String value : values) {
        insertSQLs.add(String.format(insertPatternSQL, getName(), rowId++, value));
      }
      return insertSQLs;
    }
  }

}
