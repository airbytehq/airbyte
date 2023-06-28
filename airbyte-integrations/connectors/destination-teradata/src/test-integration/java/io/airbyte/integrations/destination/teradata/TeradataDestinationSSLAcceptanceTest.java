/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TeradataDestinationSSLAcceptanceTest extends TeradataDestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(TeradataDestinationSSLAcceptanceTest.class);

  protected String getConfigFileName() {
    return "secrets/sslconfig.json";
  }

}
