/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.source.performancetest;

import io.airbyte.integrations.standardtest.source.AbstractSourceConnectorTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;

/**
 * This abstract class contains common methods for both steams - Fill Db scripts and Performance
 * tests.
 */
public abstract class AbstractSourceBasePerformanceTest extends AbstractSourceConnectorTest {

  private static final String TEST_COLUMN_NAME = "test_column";
  private static final String TEST_STREAM_NAME_TEMPLATE = "test_%S";

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
