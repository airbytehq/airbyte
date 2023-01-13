/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.source.performancetest;

import static org.junit.jupiter.api.Assertions.fail;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This abstract class contains common methods for Performance tests.
 */
public abstract class AbstractSourcePerformanceTest extends AbstractSourceBasePerformanceTest {

  protected static final Logger c = LoggerFactory.getLogger(AbstractSourcePerformanceTest.class);
  private static final String ID_COLUMN_NAME = "id";
  protected JsonNode config;

  /**
   * Setup the test database. All tables and data described in the registered tests will be put there.
   *
   * @throws Exception - might throw any exception during initialization.
   */
  protected abstract void setupDatabase(String dbName) throws Exception;

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {}

  /**
   * This is a data provider for performance tests, Each argument's group would be ran as a separate
   * test. Set the "testArgs" in test class of your DB in @BeforeTest method.
   *
   * 1st arg - a name of DB that will be used in jdbc connection string. 2nd arg - a schemaName that
   * will be ised as a NameSpace in Configured Airbyte Catalog. 3rd arg - a number of expected records
   * retrieved in each stream. 4th arg - a number of columns in each stream\table that will be used
   * for Airbyte Cataloq configuration 5th arg - a number of streams to read in configured airbyte
   * Catalog. Each stream\table in DB should be names like "test_0", "test_1",..., test_n.
   *
   * Example: Stream.of( Arguments.of("test1000tables240columns200recordsDb", "dbo", 200, 240, 1000),
   * Arguments.of("test5000tables240columns200recordsDb", "dbo", 200, 240, 1000),
   * Arguments.of("newregular25tables50000records", "dbo", 50052, 8, 25),
   * Arguments.of("newsmall1000tableswith10000rows", "dbo", 10011, 8, 1000) );
   */
  protected abstract Stream<Arguments> provideParameters();

  @ParameterizedTest
  @MethodSource("provideParameters")
  public void testPerformance(final String dbName,
                              final String schemaName,
                              final int numberOfDummyRecords,
                              final int numberOfColumns,
                              final int numberOfStreams)
      throws Exception {

    setupDatabase(dbName);

    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog(schemaName, numberOfStreams,
        numberOfColumns);
    final Map<String, Integer> mapOfExpectedRecordsCount = prepareMapWithExpectedRecords(
        numberOfStreams, numberOfDummyRecords);
    final Map<String, Integer> checkStatusMap = runReadVerifyNumberOfReceivedMsgs(catalog, null,
        mapOfExpectedRecordsCount);
    validateNumberOfReceivedMsgs(checkStatusMap);

  }

  /**
   * The column name will be used for a PK column in the test tables. Override it if default name is
   * not valid for your source.
   *
   * @return Id column name
   */
  protected String getIdColumnName() {
    return ID_COLUMN_NAME;
  }

  protected void validateNumberOfReceivedMsgs(final Map<String, Integer> checkStatusMap) {
    // Iterate through all streams map and check for streams where
    final Map<String, Integer> failedStreamsMap = checkStatusMap.entrySet().stream()
        .filter(el -> el.getValue() != 0).collect(Collectors.toMap(Entry::getKey, Entry::getValue));

    if (!failedStreamsMap.isEmpty()) {
      fail("Non all messages were delivered. " + failedStreamsMap.toString());
    }
    c.info("Finished all checks, no issues found for {} of streams", checkStatusMap.size());
  }

  protected Map<String, Integer> prepareMapWithExpectedRecords(final int streamNumber,
                                                               final int expectedRecordsNumberInEachStream) {
    final Map<String, Integer> resultMap = new HashMap<>(); // streamName&expected records in stream

    for (int currentStream = 0; currentStream < streamNumber; currentStream++) {
      final String streamName = String.format(getTestStreamNameTemplate(), currentStream);
      resultMap.put(streamName, expectedRecordsNumberInEachStream);
    }
    return resultMap;
  }

  /**
   * Configures streams for all registered data type tests.
   *
   * @return configured catalog
   */
  protected ConfiguredAirbyteCatalog getConfiguredCatalog(final String nameSpace,
                                                          final int numberOfStreams,
                                                          final int numberOfColumns) {
    final List<ConfiguredAirbyteStream> streams = new ArrayList<>();

    for (int currentStream = 0; currentStream < numberOfStreams; currentStream++) {

      // CREATE TABLE test.test_1_int(id INTEGER PRIMARY KEY, test_column int)
      final List<Field> fields = new ArrayList<>();

      fields.add(Field.of(getIdColumnName(), JsonSchemaType.NUMBER));
      for (int currentColumnNumber = 0;
          currentColumnNumber < numberOfColumns;
          currentColumnNumber++) {
        fields.add(Field.of(getTestColumnName() + currentColumnNumber, JsonSchemaType.STRING));
      }

      final AirbyteStream airbyteStream = CatalogHelpers
          .createAirbyteStream(String.format(getTestStreamNameTemplate(), currentStream),
              nameSpace, fields)
          .withSourceDefinedCursor(true)
          .withSourceDefinedPrimaryKey(List.of(List.of(getIdColumnName())))
          .withSupportedSyncModes(
              Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));

      final ConfiguredAirbyteStream configuredAirbyteStream = new ConfiguredAirbyteStream()
          .withSyncMode(SyncMode.INCREMENTAL)
          .withCursorField(Lists.newArrayList(getIdColumnName()))
          .withDestinationSyncMode(DestinationSyncMode.APPEND)
          .withStream(airbyteStream);

      streams.add(configuredAirbyteStream);

    }

    return new ConfiguredAirbyteCatalog().withStreams(streams);
  }

}
