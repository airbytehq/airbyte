/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import org.junit.jupiter.api.TestInstance;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.file.Files;
import java.nio.file.Paths;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public class TeradataDestinationSSLAcceptanceTest extends TeradataDestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(TeradataDestinationSSLAcceptanceTest.class);


  public JsonNode getStaticConfig() throws Exception {
    return Jsons.deserialize(Files.readString(Paths.get("secrets/sslconfig.json")));
  }

}