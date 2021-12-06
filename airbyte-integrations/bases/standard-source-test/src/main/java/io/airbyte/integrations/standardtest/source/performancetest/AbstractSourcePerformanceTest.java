/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.source.performancetest;

import static org.junit.jupiter.api.Assertions.fail;

import com.google.common.collect.Lists;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import io.airbyte.protocol.models.SyncMode;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This abstract class contains common helpers and boilerplate for comprehensively testing that all
 * data types in a source can be read and handled correctly by the connector and within Airbyte's
 * type system.
 */
public abstract class AbstractSourcePerformanceTest extends SourceBasePerformanceTest {

  protected static final Logger c = LoggerFactory.getLogger(AbstractSourcePerformanceTest.class);
  private static final String ID_COLUMN_NAME = "id";

  /**
   * Setup the test database. All tables and data described in the registered tests will be put there.
   *
   * @throws Exception - might throw any exception during initialization.
   */
  protected abstract void setupDatabase(String dbName) throws Exception;

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
    Map<String, Integer> failedStreamsMap = checkStatusMap.entrySet().stream()
        .filter(el -> el.getValue() != 0).collect(Collectors.toMap(Entry::getKey, Entry::getValue));

    if (!failedStreamsMap.isEmpty()) {
      fail("Non all messages were delivered. " + failedStreamsMap.toString());
    }
    c.info("Finished all checks, no issues found for {} of streams", checkStatusMap.size());
  }

  protected Map<String, Integer> prepareMapWithExpectedRecords(final int streamNumber,
                                                               final int expectedRecordsNumberInEachStream) {
    Map<String, Integer> resultMap = new HashMap<>(); // streamName&expected records in stream

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
    List<ConfiguredAirbyteStream> streams = new ArrayList<>();

    for (int currentStream = 0; currentStream < numberOfStreams; currentStream++) {

      // CREATE TABLE test.test_1_int(id INTEGER PRIMARY KEY, test_column int)
      List<Field> fields = new ArrayList<>();

      fields.add(Field.of(getIdColumnName(), JsonSchemaPrimitive.NUMBER));
      for (int currentColumnNumber = 0;
          currentColumnNumber < numberOfColumns;
          currentColumnNumber++) {
        fields.add(Field.of(getTestColumnName() + currentColumnNumber, JsonSchemaPrimitive.STRING));
      }

      AirbyteStream airbyteStream = CatalogHelpers
          .createAirbyteStream(String.format(getTestStreamNameTemplate(), currentStream),
              nameSpace, fields)
          .withSourceDefinedCursor(true)
          .withSourceDefinedPrimaryKey(List.of(List.of(getIdColumnName())))
          .withSupportedSyncModes(
              Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));

      ConfiguredAirbyteStream configuredAirbyteStream = new ConfiguredAirbyteStream()
          .withSyncMode(SyncMode.INCREMENTAL)
          .withCursorField(Lists.newArrayList(getIdColumnName()))
          .withDestinationSyncMode(DestinationSyncMode.APPEND)
          .withStream(airbyteStream);

      streams.add(configuredAirbyteStream);

    }

    return new ConfiguredAirbyteCatalog().withStreams(streams);
  }

}
