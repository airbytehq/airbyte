/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.source.performancetest;

import io.airbyte.db.Database;
import io.airbyte.integrations.standardtest.source.AbstractSourceConnectorTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;

public abstract class SourceBasePerformanceTest extends AbstractSourceConnectorTest {

  private static final String TEST_COLUMN_NAME = "test_column";
  private static final String TEST_STREAM_NAME_TEMPLATE  = "test_%S";

  /**
   * Setup the test database. All tables and data described in the registered tests will be put there.
   *
   * @return configured test database
   * @throws Exception - might throw any exception during initialization.
   */
  protected abstract Database setupDatabase(String dbName) throws Exception;

  /**
   * The column name will be used for a test column in the test tables. Override it if default name is
   * not valid for your source.
   *
   * @return Test column name
   */
  protected String getTestColumnName() {
    return TEST_COLUMN_NAME;
  }

  /**
   * The stream name template will be used for a test tables. Override it if default name is not valid
   * for your source.
   *
   * @return Test steam name template
   */
  protected String getTestStreamNameTemplate() {
    return TEST_STREAM_NAME_TEMPLATE;
  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    // DO NOTHING. Mandatory to override. DB will be setup as part of each test
  }

}
