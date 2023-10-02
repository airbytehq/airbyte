/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.destination.s3.S3BaseAvroDestinationAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.destination.ProtocolVersion;
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator;

public class S3AvroDestinationAcceptanceTest extends S3BaseAvroDestinationAcceptanceTest {

  @Override
  public ProtocolVersion getProtocolVersion() {
    return ProtocolVersion.V1;
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new S3AvroParquetTestDataComparator();
  }

  @Override
  protected JsonNode getBaseConfigJson() {
    return S3DestinationTestUtils.getBaseConfigJsonFilePath();
  }

}
