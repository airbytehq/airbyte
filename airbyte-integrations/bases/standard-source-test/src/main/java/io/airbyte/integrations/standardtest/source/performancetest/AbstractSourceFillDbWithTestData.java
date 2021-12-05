/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.source.performancetest;

import java.util.StringJoiner;

public abstract class AbstractSourceFillDbWithTestData extends SourceBasePerformanceTest {

  private static final String TEST_VALUE_TEMPLATE = "\"Some test value %s\"";
  private static final String TEST_VALUE_TEMPLATE_POSTGRES = "\'Value id_placeholder\'";

  /**
   * Get a create table template for a DB
   *
   * @return a create tabple template, ex. "CREATE TABLE test.%s(id INTEGER PRIMARY KEY, %s)"
   */
  protected abstract String getCreateTableTemplate();

  /**
   * Get a test field'stype that will be used in DB for table creation.
   *
   * @return a test's field type. Ex: varchar(8)
   */
  protected abstract String getTestFieldType();

  /**
   * Get a INSERT query template for a DB
   *
   * @return an INSERT into table query template, ex. "INSERT INTO test.%s (%s) VALUES %s"
   */
  protected abstract String getInsertQueryTemplate();

  protected String prepareCreateTableQuery(final String dbSchemaName,
                                           final int numberOfColumns,
                                           final String currentTableName) {

    StringJoiner sj = new StringJoiner(",");
    for (int i = 0; i < numberOfColumns; i++) {
      sj.add(String.format(" %s%s %s", getTestColumnName(), i, getTestFieldType()));
    }

    return String.format(getCreateTableTemplate(), dbSchemaName, currentTableName, sj.toString());
  }

  // ex. INSERT INTO test.test_1 (id, test_column0, test_column1) VALUES (101,"zzz0", "sss0"), ("102",
  // "zzzz1", "sss1");
  protected String prepareInsertQueryTemplate(final String dbSchemaName,
                                              final int numberOfColumns,
                                              final int recordsNumber) {

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
        .format(getInsertQueryTemplate(), dbSchemaName, "%s", fieldsNames.toString(),
            insertGroupValuesJoiner.toString());
  }

  // ex. INSERT INTO "test100tables100recordsDb".test_0 (id,test_column0)
  // VALUES (0,'Value t0'), (1,'Value t1');
  protected String prepareInsertQueryTemplatePostgres(final String dbSchemaName,
                                                      final int batchNumber,
                                                      final int numberOfColumns,
                                                      final int recordsNumber) {

    StringJoiner fieldsNames = new StringJoiner(",");
    fieldsNames.add("id");

    StringJoiner baseInsertQuery = new StringJoiner(",");
    baseInsertQuery.add("id_placeholder");

    for (int i = 0; i < numberOfColumns; i++) {
      fieldsNames.add(getTestColumnName() + i);
      baseInsertQuery.add(TEST_VALUE_TEMPLATE_POSTGRES);
    }

    StringJoiner insertGroupValuesJoiner = new StringJoiner(",");

    int batchMessages = batchNumber * 100;

    for (int currentRecordNumber = batchMessages;
        currentRecordNumber < recordsNumber + batchMessages;
        currentRecordNumber++) {
      insertGroupValuesJoiner
          .add("(" + baseInsertQuery.toString()
              .replaceAll("id_placeholder", String.valueOf(currentRecordNumber)) + ")");
    }

    return String
        .format(getInsertQueryTemplate(), dbSchemaName, "%s", fieldsNames.toString(),
            insertGroupValuesJoiner.toString());
  }

}
