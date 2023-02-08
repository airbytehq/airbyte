/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import java.nio.file.Path;

public class S3DestinationTestUtils {

  private static final String SECRET_PATH = "secrets/s3_dest_min_required_permissions_creds.json";

  public static JsonNode getBaseConfigJsonFilePath() {
    return Jsons.deserialize(IOs.readFile(Path.of(SECRET_PATH)));
  }

}
