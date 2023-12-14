/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Integration test testing the {@link RedshiftInsertDestination}.
 */
public class RedshiftInsertDestinationAcceptanceTest extends RedshiftStagingS3DestinationAcceptanceTest {

  public JsonNode getStaticConfig() throws IOException {
    return Jsons.deserialize(Files.readString(Path.of("secrets/config.json")));
  }

}
