/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.source;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.SyncMode;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This abstract class contains common helpers and boilerplate for comprehensively testing that all
 * data types in a source can be read and handled correctly by the connector and within Airbyte's
 * type system.
 */
public abstract class AbstractSourceDatabaseTypeTest extends AbstractSourceConnectorTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractSourceDatabaseTypeTest.class);

  private final List<TestDataHolder> testDataHolders = new ArrayList<>();

  /**
   * The column name will be used for a PK column in the test tables. Override it if default name is
   * not valid for your source.
   *
   * @return Id column name
   */
  protected String getIdColumnName() {
    return "id";
  }

  /**
   * The column name will be used for a test column in the test tables. Override it if default name is
   * not valid for your source.
   *
   * @return Test column name
   */
  protected String getTestColumnName() {
    return "test_column";
  }

  /**
   * Setup the test database. All tables and data described in the registered tests will be put there.
   *
   * @return configured test database
   * @throws Exception - might throw any exception during initialization.
   */
  protected abstract Database setupDatabase() throws Exception;

  /**
   * Put all required tests here using method {@link #addDataTypeTestData(TestDataHolder)}
   */
  protected abstract void initTests();

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    setupDatabaseInternal();
  }

  /**
   * Provide a source namespace. It's allocated place for table creation. It also known ask "Database
   * Schema" or "Dataset"
   *
   * @return source name space
   */
  protected abstract String getNameSpace();

  /**
   * Test the discover command. TODO (liren): This is a new unit test. Some existing databases may
   * fail it, so it is turned off by default. It should be enabled for all databases eventually.
   */
  protected boolean testCatalog() {
    return false;
  }

  /**
   * The test checks that connector can fetch prepared data without failure.
   */
  @Test
  @SuppressWarnings("unchecked")
  public void testDataTypes() throws Exception {
    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog();
    final List<AirbyteMessage> allMessages = runRead(catalog);
    final Map<String, AirbyteStream> streams = runDiscover().getStreams().stream()
        .collect(Collectors.toMap(AirbyteStream::getName, s -> s));
    final List<AirbyteMessage> recordMessages = allMessages.stream().filter(m -> m.getType() == Type.RECORD).collect(Collectors.toList());
    final Map<String, List<String>> expectedValues = new HashMap<>();
    testDataHolders.forEach(testDataHolder -> {
      if (testCatalog()) {
        final AirbyteStream airbyteStream = streams.get(testDataHolder.getNameWithTestPrefix());
        final Map<String, String> jsonSchemaTypeMap = (Map<String, String>) Jsons.deserialize(
            airbyteStream.getJsonSchema().get("properties").get(getTestColumnName()).toString(), Map.class);
        assertEquals(testDataHolder.getAirbyteType().getJsonSchemaTypeMap(), jsonSchemaTypeMap,
            "Expected column type for " + testDataHolder.getNameWithTestPrefix());
      }

      if (!testDataHolder.getExpectedValues().isEmpty()) {
        expectedValues.put(testDataHolder.getNameWithTestPrefix(), testDataHolder.getExpectedValues());
      }
    });

    for (final AirbyteMessage msg : recordMessages) {
      final String streamName = msg.getRecord().getStream();
      final List<String> expectedValuesForStream = expectedValues.get(streamName);
      if (expectedValuesForStream != null) {
        final String value = getValueFromJsonNode(msg.getRecord().getData().get(getTestColumnName()));
        assertTrue(expectedValuesForStream.contains(value),
            String.format("Returned value '%s' from stream %s is not in the expected list: %s",
                value, streamName, expectedValuesForStream));
        expectedValuesForStream.remove(value);
      }
    }

    expectedValues.forEach((streamName, values) -> assertTrue(values.isEmpty(),
        "The streamer " + streamName + " should return all expected values. Missing values: " + values));
  }

  protected String getValueFromJsonNode(final JsonNode jsonNode) throws IOException {
    if (jsonNode != null) {
      if (jsonNode.isArray()) {
        return jsonNode.toString();
      }

      String value = (jsonNode.isBinary() ? Arrays.toString(jsonNode.binaryValue()) : jsonNode.asText());
      value = (value != null && value.equals("null") ? null : value);
      return value;
    }
    return null;
  }

  /**
   * Creates all tables and insert data described in the registered data type tests.
   *
   * @throws Exception might raise exception if configuration goes wrong or tables creation/insert
   *         scripts failed.
   */
  private void setupDatabaseInternal() throws Exception {
    final Database database = setupDatabase();

    initTests();

    for (final TestDataHolder test : testDataHolders) {
      database.query(ctx -> {
        ctx.fetch(test.getCreateSqlQuery());
        LOGGER.debug("Table " + test.getNameWithTestPrefix() + " is created.");
        test.getInsertSqlQueries().forEach(ctx::fetch);
        return null;
      });
    }
  }

  /**
   * Configures streams for all registered data type tests.
   *
   * @return configured catalog
   */
  private ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return new ConfiguredAirbyteCatalog().withStreams(
        testDataHolders
            .stream()
            .map(test -> new ConfiguredAirbyteStream()
                .withSyncMode(SyncMode.INCREMENTAL)
                .withCursorField(Lists.newArrayList(getIdColumnName()))
                .withDestinationSyncMode(DestinationSyncMode.APPEND)
                .withStream(CatalogHelpers.createAirbyteStream(
                    String.format("%s", test.getNameWithTestPrefix()),
                    String.format("%s", getNameSpace()),
                    Field.of(getIdColumnName(), JsonSchemaType.NUMBER),
                    Field.of(getTestColumnName(), test.getAirbyteType()))
                    .withSourceDefinedCursor(true)
                    .withSourceDefinedPrimaryKey(List.of(List.of(getIdColumnName())))
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
  public void addDataTypeTestData(final TestDataHolder test) {
    testDataHolders.add(test);
    test.setTestNumber(testDataHolders.stream().filter(t -> t.getSourceType().equals(test.getSourceType())).count());
    test.setNameSpace(getNameSpace());
    test.setIdColumnName(getIdColumnName());
    test.setTestColumnName(getTestColumnName());
  }

  private String formatCollection(final Collection<String> collection) {
    return collection.stream().map(s -> "`" + s + "`").collect(Collectors.joining(", "));
  }

  /**
   * Builds a table with all registered test cases with values using Markdown syntax (can be used in
   * the github).
   *
   * @return formatted list of test cases
   */
  public String getMarkdownTestTable() {
    final StringBuilder table = new StringBuilder()
        .append("|**Data Type**|**Insert values**|**Expected values**|**Comment**|**Common test result**|\n")
        .append("|----|----|----|----|----|\n");

    testDataHolders.forEach(test -> table.append(String.format("| %s | %s | %s | %s | %s |\n",
        test.getSourceType(),
        formatCollection(test.getValues()),
        formatCollection(test.getExpectedValues()),
        "",
        "Ok")));
    return table.toString();
  }

  protected void printMarkdownTestTable() {
    LOGGER.info(getMarkdownTestTable());
  }

}
