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

import static org.junit.jupiter.api.Assertions.assertFalse;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.db.Database;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.SyncMode;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class SourceComprehensiveTest extends SourceAbstractTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(SourceComprehensiveTest.class);

  private final List<DataTypeTest> dataTypeTests = new ArrayList<>();

  /**
   * Setup the test database. All tables and data described in the registered tests will be put there.
   *
   * @return configured test database
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
    final List<AirbyteMessage> recordMessages = allMessages.stream().filter(m -> m.getType() == Type.RECORD).collect(Collectors.toList());

    recordMessages.forEach(msg -> LOGGER.debug(msg.toString()));
    assertFalse(recordMessages.isEmpty(), "Expected records from source");
  }

  /**
   * Creates all tables and insert data described in the registered data type tests.
   *
   * @throws Exception might raise exception if configuration goes wrong or tables creation/insert
   *         scripts failed.
   */
  private void setupDatabaseInternal() throws Exception {
    Database database = setupDatabase();

    initTests();

    for (DataTypeTest test : dataTypeTests) {
      database.query(ctx -> {
        ctx.fetch(test.getCreateSQL());
        LOGGER.debug("Table " + test.getName() + " is created.");
        test.getInsertSQLs().forEach(ctx::fetch);
        return null;
      });
    }

    database.close();
  }

  /**
   * Configures streams for all registered data type tests.
   *
   * @return configured catalog
   */
  private ConfiguredAirbyteCatalog getConfiguredCatalog() throws Exception {
    final JsonNode config = getConfig();

    return new ConfiguredAirbyteCatalog().withStreams(
        dataTypeTests
            .stream()
            .map(test -> new ConfiguredAirbyteStream()
                .withSyncMode(SyncMode.INCREMENTAL)
                .withCursorField(Lists.newArrayList("id"))
                .withDestinationSyncMode(DestinationSyncMode.APPEND)
                .withStream(CatalogHelpers.createAirbyteStream(
                    String.format("%s", test.getName()),
                    String.format("%s", config.get("database").asText()),
                    Field.of("id", Field.JsonSchemaPrimitive.NUMBER),
                    Field.of("test_column", test.getAirbyteType()))
                    .withSourceDefinedCursor(true)
                    .withSourceDefinedPrimaryKey(List.of(List.of("id")))
                    .withSupportedSyncModes(
                        Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))))
            .collect(Collectors.toList()));
  }

  /**
   * Register your test in the run scope. For each test will be created a table with one column of
   * specified type. Note! If you register more than one test with the same type name, they will be
   * run as independent tests with own streams.
   *
   * @param test comprehensive data type test
   */
  public void addDataTypeTest(DataTypeTest test) {
    dataTypeTests.add(test);
    test.setTestNumber(dataTypeTests.stream().filter(t -> t.getSourceType().equals(test.getSourceType())).count());
  }

}
