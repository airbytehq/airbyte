/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.source.performancetest;

import io.airbyte.db.Database;
import java.util.StringJoiner;
import java.util.stream.Stream;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This abstract class contains common methods for Fill Db scripts.
 */
public abstract class AbstractSourceFillDbWithTestData extends AbstractSourceBasePerformanceTest {

  private static final String CREATE_DB_TABLE_TEMPLATE = "CREATE TABLE %s.%s(id INTEGER PRIMARY KEY, %s)";
  private static final String INSERT_INTO_DB_TABLE_QUERY_TEMPLATE = "INSERT INTO %s.%s (%s) VALUES %s";
  private static final String TEST_DB_FIELD_TYPE = "varchar(10)";

  protected static final Logger c = LoggerFactory.getLogger(AbstractSourceFillDbWithTestData.class);
  private static final String TEST_VALUE_TEMPLATE_POSTGRES = "\'Value id_placeholder\'";

  /**
   * Setup the test database. All tables and data described in the registered tests will be put there.
   *
   * @return configured test database
   * @throws Exception - might throw any exception during initialization.
   */
  protected abstract Database setupDatabase(String dbName) throws Exception;

  /**
   * The test added test data to a new DB. 1. Set DB creds in static variables above 2. Set desired
   * number for streams, coolumns and records 3. Run the test
   */
  @Disabled
  @ParameterizedTest
  @MethodSource("provideParameters")
  public void addTestData(final String dbName,
                          final String schemaName,
                          final int numberOfDummyRecords,
                          final int numberOfBatches,
                          final int numberOfColumns,
                          final int numberOfStreams)
      throws Exception {

    final Database database = setupDatabase(dbName);

    database.query(ctx -> {
      for (int currentSteamNumber = 0; currentSteamNumber < numberOfStreams; currentSteamNumber++) {

        final String currentTableName = String.format(getTestStreamNameTemplate(), currentSteamNumber);

        ctx.fetch(prepareCreateTableQuery(schemaName, numberOfColumns, currentTableName));
        for (int i = 0; i < numberOfBatches; i++) {
          final String insertQueryTemplate = prepareInsertQueryTemplate(schemaName, i,
              numberOfColumns,
              numberOfDummyRecords);
          ctx.fetch(String.format(insertQueryTemplate, currentTableName));
        }

        c.info("Finished processing for stream " + currentSteamNumber);
      }
      return null;
    });
  }

  /**
   * This is a data provider for fill DB script,, Each argument's group would be ran as a separate
   * test. Set the "testArgs" in test class of your DB in @BeforeTest method.
   *
   * 1st arg - a name of DB that will be used in jdbc connection string. 2nd arg - a schemaName that
   * will be ised as a NameSpace in Configured Airbyte Catalog. 3rd arg - a number of expected records
   * retrieved in each stream. 4th arg - a number of columns in each stream\table that will be use for
   * Airbyte Cataloq configuration 5th arg - a number of streams to read in configured airbyte
   * Catalog. Each stream\table in DB should be names like "test_0", "test_1",..., test_n.
   *
   * Stream.of( Arguments.of("your_db_name", "your_schema_name", 100, 2, 240, 1000) );
   */
  protected abstract Stream<Arguments> provideParameters();

  protected String prepareCreateTableQuery(final String dbSchemaName,
                                           final int numberOfColumns,
                                           final String currentTableName) {

    final StringJoiner sj = new StringJoiner(",");
    for (int i = 0; i < numberOfColumns; i++) {
      sj.add(String.format(" %s%s %s", getTestColumnName(), i, TEST_DB_FIELD_TYPE));
    }

    return String.format(CREATE_DB_TABLE_TEMPLATE, dbSchemaName, currentTableName, sj.toString());
  }

  protected String prepareInsertQueryTemplate(final String dbSchemaName,
                                              final int batchNumber,
                                              final int numberOfColumns,
                                              final int recordsNumber) {

    final StringJoiner fieldsNames = new StringJoiner(",");
    fieldsNames.add("id");

    final StringJoiner baseInsertQuery = new StringJoiner(",");
    baseInsertQuery.add("id_placeholder");

    for (int i = 0; i < numberOfColumns; i++) {
      fieldsNames.add(getTestColumnName() + i);
      baseInsertQuery.add(TEST_VALUE_TEMPLATE_POSTGRES);
    }

    final StringJoiner insertGroupValuesJoiner = new StringJoiner(",");

    final int batchMessages = batchNumber * 100;

    for (int currentRecordNumber = batchMessages;
        currentRecordNumber < recordsNumber + batchMessages;
        currentRecordNumber++) {
      insertGroupValuesJoiner
          .add("(" + baseInsertQuery.toString()
              .replaceAll("id_placeholder", String.valueOf(currentRecordNumber)) + ")");
    }

    return String
        .format(INSERT_INTO_DB_TABLE_QUERY_TEMPLATE, dbSchemaName, "%s", fieldsNames.toString(),
            insertGroupValuesJoiner.toString());
  }

}
