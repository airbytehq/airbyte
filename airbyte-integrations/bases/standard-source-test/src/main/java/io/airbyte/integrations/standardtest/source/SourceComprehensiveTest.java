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
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.*;
import io.airbyte.protocol.models.*;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.SyncMode;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.DockerProcessFactory;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.db.Database;
import io.airbyte.workers.protocols.airbyte.AirbyteSource;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteSource;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;
import java.util.stream.Collectors;

import static io.airbyte.protocol.models.SyncMode.FULL_REFRESH;
import static org.junit.jupiter.api.Assertions.*;

public abstract class SourceComprehensiveTest {

  private static final long JOB_ID = 0L;
  private static final int JOB_ATTEMPT = 0;

  private static final Logger LOGGER = LoggerFactory.getLogger(SourceComprehensiveTest.class);
  private static final String DEFAULT_CREATE_TABLE_SQL = "CREATE TABLE %1$s(test_column %2$s);";
  private static final String DEFAULT_INSERT_SQL = "INSERT INTO %1$s VALUES (%2$s);";

  private TestDestinationEnv testEnv;
  private JsonNode config;
  private final List<DataTypeTest> dataTypeTests = new ArrayList<>();

  private Path jobRoot;
  protected Path localRoot;
  private ProcessFactory processFactory;

  /**
   * Name of the docker image that the tests will run against.
   *
   * @return docker image name
   */
  protected abstract String getImageName();

  protected abstract JsonNode setupConfig(TestDestinationEnv testEnv) throws Exception;

  protected abstract Database setupDatabase(JsonNode config) throws Exception;

  protected abstract void initTests();

  /**
   * Function that performs any clean up of external resources required for the test. e.g. delete a
   * postgres database. This function will be called after EACH test. It MUST remove all data in the
   * destination so that there is no contamination across tests.
   *
   * @param testEnv - information about the test environment.
   * @throws Exception - can throw any exception, test framework will handle.
   */
  protected abstract void tearDown(TestDestinationEnv testEnv) throws Exception;

  public void addDataTypeTest(DataTypeTest test) {
    dataTypeTests.add(test);
    test.setTestNumber(dataTypeTests.stream().filter(t -> t.getSourceType().equals(test.getSourceType())).count());
  }

  @BeforeEach
  public void setUpInternal() throws Exception {
    final Path testDir = Path.of("/tmp/airbyte_tests/");
    Files.createDirectories(testDir);
    final Path workspaceRoot = Files.createTempDirectory(testDir, "test");
    jobRoot = Files.createDirectories(Path.of(workspaceRoot.toString(), "job"));
    localRoot = Files.createTempDirectory(testDir, "output");
    testEnv = new TestDestinationEnv(localRoot);

    config = setupConfig(testEnv);
    setupDatabaseInternal();

    processFactory = new DockerProcessFactory(
        workspaceRoot,
        workspaceRoot.toString(),
        localRoot.toString(),
        "host");
  }

  @AfterEach
  public void tearDownInternal() throws Exception {
    tearDown(testEnv);
  }

  /**
   * Configuring all streams in the input catalog to full refresh mode, verifies that a read operation
   * produces some RECORD messages.
   */
  @Test
  public void testFullRefreshRead() throws Exception {
    ConfiguredAirbyteCatalog catalog = withFullRefreshSyncModes(getConfiguredCatalog());
    List<AirbyteMessage> allMessages = runRead(catalog);
    LOGGER.info("Size: " + allMessages.size());
    final List<AirbyteMessage> recordMessages = allMessages.stream().filter(m -> m.getType() == Type.RECORD).collect(Collectors.toList());

    recordMessages.forEach(msg -> LOGGER.info(msg.toString()));

    assertFalse(recordMessages.isEmpty(), "Expected a full refresh sync to produce records");

    allMessages = runRead(catalog);
    LOGGER.info("Size: " + allMessages.size());
    recordMessages.forEach(msg -> LOGGER.info(msg.toString()));
  }

  private void setupDatabaseInternal() throws Exception {
    Database database = setupDatabase(config);

    initTests();

    for (DataTypeTest test : dataTypeTests) {
      database.query(ctx -> {
        ctx.fetch(test.getCreateSQL());
        test.getInsertSQLs().forEach(ctx::fetch);
        return null;
      });
    }
//    database.query(ctx -> {
//      ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
//      ctx.fetch("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
//      ctx.fetch("CREATE TABLE starships(id INTEGER, name VARCHAR(200));");
//      ctx.fetch("INSERT INTO starships (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');");
//      return null;
//    });

    database.close();
  }

  private ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return new ConfiguredAirbyteCatalog().withStreams(
            dataTypeTests
                    .stream()
                    .map(test -> new ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.FULL_REFRESH)
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withStream(CatalogHelpers.createAirbyteStream(
                                    String.format("%s.%s", config.get("database").asText(), test.getName()),
                                    Field.of("test_column", test.getAirbyteType()))
                                    .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH))))
                    .collect(Collectors.toList())
    );
  }

  private ConfiguredAirbyteCatalog withFullRefreshSyncModes(ConfiguredAirbyteCatalog catalog) {
    final ConfiguredAirbyteCatalog clone = Jsons.clone(catalog);
    for (ConfiguredAirbyteStream configuredStream : clone.getStreams()) {
      if (configuredStream.getStream().getSupportedSyncModes().contains(FULL_REFRESH)) {
        configuredStream.setSyncMode(FULL_REFRESH);
        configuredStream.setDestinationSyncMode(DestinationSyncMode.OVERWRITE);
      }
    }
    return clone;
  }

  private List<AirbyteMessage> runRead(ConfiguredAirbyteCatalog configuredCatalog) throws Exception {
    final StandardTapConfig sourceConfig = new StandardTapConfig()
            .withSourceConnectionConfiguration(config)
            .withState(null)
            .withCatalog(configuredCatalog);

    final AirbyteSource source = new DefaultAirbyteSource(new AirbyteIntegrationLauncher(JOB_ID, JOB_ATTEMPT, getImageName(), processFactory));
    final List<AirbyteMessage> messages = new ArrayList<>();
    source.start(sourceConfig, jobRoot);
    while (!source.isFinished()) {
      source.attemptRead().ifPresent(messages::add);
    }
    source.close();

    return messages;
  }

  public static class TestDestinationEnv {

    private final Path localRoot;

    public TestDestinationEnv(Path localRoot) {
      this.localRoot = localRoot;
    }

    public Path getLocalRoot() {
      return localRoot;
    }

  }

  public static class DataTypeTest {

    private final String sourceType;
    private final Field.JsonSchemaPrimitive airbyteType;
    private final List<String> values = new ArrayList<>();
    private String createTablePatternSQL;
    private String insertPatternSQL;
    private long testNumber;

    public DataTypeTest(String sourceType, Field.JsonSchemaPrimitive airbyteType) {
      this.sourceType = sourceType;
      this.airbyteType = airbyteType;
      setCreateTablePatternSQL(DEFAULT_CREATE_TABLE_SQL);
      setInsertPatternSQL(DEFAULT_INSERT_SQL);
    }

    public DataTypeTest addInsertValue(String insertValue) {
      values.add(insertValue);
      return this;
    }

    public String getName() {
      return "test_" + testNumber + "_" + sourceType;
    }

    public String getSourceType() {
      return sourceType;
    }

    public Field.JsonSchemaPrimitive getAirbyteType() {
      return airbyteType;
    }

    public List<String> getValues() {
      return values;
    }

    public DataTypeTest setCreateTablePatternSQL(String createTablePatternSQL) {
      this.createTablePatternSQL = createTablePatternSQL;
      return this;
    }

    public DataTypeTest setInsertPatternSQL(String insertPatternSQL) {
      this.insertPatternSQL = insertPatternSQL;
      return this;
    }

    public void setTestNumber(long testNumber) {
      this.testNumber = testNumber;
    }

    public String getCreateSQL() {
      return String.format(createTablePatternSQL, getName(), getSourceType());
    }

    public List<String> getInsertSQLs() {
      return values.stream().map(value -> String.format(insertPatternSQL, getName(), value)).collect(Collectors.toList());
    }
  }

}
