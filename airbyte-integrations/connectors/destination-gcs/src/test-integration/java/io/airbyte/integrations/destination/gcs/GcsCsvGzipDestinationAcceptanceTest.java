/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs;

import com.amazonaws.services.s3.model.S3Object;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig.Flattening;
import io.airbyte.integrations.standardtest.destination.ProtocolVersion;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.zip.GZIPInputStream;

public class GcsCsvGzipDestinationAcceptanceTest extends GcsCsvDestinationAcceptanceTest {

  @Override
  public ProtocolVersion getProtocolVersion() {
    return ProtocolVersion.V1;
  }

  @Override
  protected JsonNode getFormatConfig() {
    // config without compression defaults to GZIP
    return Jsons.jsonNode(Map.of(
        "format_type", outputFormat,
        "flattening", Flattening.ROOT_LEVEL.getValue()));
  }

  protected Reader getReader(final S3Object s3Object) throws IOException {
    return new InputStreamReader(new GZIPInputStream(s3Object.getObjectContent()), StandardCharsets.UTF_8);
  }

}
