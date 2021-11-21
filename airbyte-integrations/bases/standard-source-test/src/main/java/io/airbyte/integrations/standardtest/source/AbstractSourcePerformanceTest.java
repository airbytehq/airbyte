/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.source;

import static org.junit.jupiter.api.Assertions.fail;

import com.google.common.collect.Lists;
import io.airbyte.db.Database;
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
import java.util.StringJoiner;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This abstract class contains common helpers and boilerplate for comprehensively testing that all
 * data types in a source can be read and handled correctly by the connector and within Airbyte's
 * type system.
 */
public abstract class AbstractSourcePerformanceTest extends AbstractSourceConnectorTest {

  protected static final Logger c = LoggerFactory.getLogger(AbstractSourcePerformanceTest.class);
  private static final String TEST_VALUE_TEMPLATE = "\"Some test value %s\"";
  protected String databaseName = "test";

  protected int numberOfColumns; // 240 is near the max value for varchar(8) type
  // 200 is near the max value for 1 batch call,if need more - implement multiple batching for single
  // stream
  protected int numberOfDummyRecords; // 200;
  protected int numberOfStreams;

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
   * The stream name template will be used for a test tables. Override it if default name is not valid
   * for your source.
   *
   * @return Test steam name template
   */
  protected String getTestStreamNameTemplate() {
    return "test_%S";
  }

  /**
   * Setup the test database. All tables and data described in the registered tests will be put there.
   *
   * @return configured test database
   * @throws Exception - might throw any exception during initialization.
   */
  protected abstract Database setupDatabase() throws Exception;

  /**
   * Get a create table template for a DB
   *
   * @return a create tabple template, ex. "CREATE TABLE test.%s(id INTEGER PRIMARY KEY, %s)"
   */
  protected abstract String getCreateTableTemplate();

  /**
   * Get a INSERT query template for a DB
   *
   * @return an INSERT into table query template, ex. "INSERT INTO test.%s (%s) VALUES %s"
   */
  protected abstract String getInsertQueryTemplate();

  /**
   * Get a test field'stype that will be used in DB for table creation.
   *
   * @return a test's field type. Ex: varchar(8)
   */
  protected abstract String getTestFieldType();

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    // DO NOTHING. Mandatory to override. DB will be setup as part of each test
  }

  /**
   * Provide a source namespace. It's allocated place for table creation. It also known ask "Database
   * Schema" or "Dataset"
   *
   * @return source name space
   */
  protected abstract String getNameSpace();

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

  protected String prepareCreateTableQuery(final int numberOfColumns,
                                           final String currentTableName) {

    StringJoiner sj = new StringJoiner(",");
    for (int i = 0; i < numberOfColumns; i++) {
      sj.add(String.format(" %s%s %s", getTestColumnName(), i, getTestFieldType()));
    }

    return String.format(getCreateTableTemplate(), databaseName, currentTableName, sj.toString());
  }

  // ex. INSERT INTO test.test_1 (id, test_column0, test_column1) VALUES (101,"zzz0", "sss0"), ("102",
  // "zzzz1", "sss1");
  protected String prepareInsertQueryTemplate(final int numberOfColumns, final int recordsNumber) {

    StringJoiner fieldsNames = new StringJoiner(",");
    fieldsNames.add("id");

    StringJoiner baseInsertQuery = new StringJoiner(",");
    baseInsertQuery.add("%s");

    for (int i = 0; i < numberOfColumns; i++) {
      fieldsNames.add(getTestColumnName() + i);
      baseInsertQuery.add(String.format(TEST_VALUE_TEMPLATE, i));
    }

    StringJoiner insertGroupValuesJoiner = new StringJoiner(",");

    for (int currentRecordNumber = 0; currentRecordNumber < recordsNumber; currentRecordNumber++) {
      insertGroupValuesJoiner
          .add("(" + String.format(baseInsertQuery.toString(), currentRecordNumber) + ")");
    }

    return String
        .format(getInsertQueryTemplate(), databaseName, "%s", fieldsNames.toString(),
            insertGroupValuesJoiner.toString());
  }

  /**
   * Configures streams for all registered data type tests.
   *
   * @return configured catalog
   */
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
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
              getNameSpace(), fields)
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
