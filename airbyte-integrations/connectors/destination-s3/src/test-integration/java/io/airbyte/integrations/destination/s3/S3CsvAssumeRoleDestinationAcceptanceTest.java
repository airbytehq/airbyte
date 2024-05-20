/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.destination.s3.S3BaseCsvDestinationAcceptanceTest;
import java.util.Map;

public class S3CsvAssumeRoleDestinationAcceptanceTest extends S3BaseCsvDestinationAcceptanceTest {

  @Override
  protected JsonNode getBaseConfigJson() {
    return S3DestinationTestUtils.getAssumeRoleConfig();
  }

  @Override
  public Map<String, String> getConnectorEnv() {
    return S3DestinationTestUtils.getAssumeRoleInternalCredentials();
  }

}
