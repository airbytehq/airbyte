/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import java.nio.file.Path;
import org.junit.jupiter.api.Disabled;

/**
 * Integration test testing {@link RedshiftStagingS3Destination}. The default Redshift integration
 * test credentials contain S3 credentials - this automatically causes COPY to be selected.
 */
@Disabled
public class RedshiftS3StagingInsertDestinationAcceptanceTest extends RedshiftDestinationAcceptanceTest {

  public JsonNode getStaticConfig() {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/config_staging.json")));
  }

}
