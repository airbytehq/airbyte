/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import io.airbyte.integrations.standardtest.destination.ProtocolVersion;

public class S3JsonlGzipDestinationAcceptanceTest extends S3BaseJsonlGzipDestinationAcceptanceTest {

  @Override
  public ProtocolVersion getProtocolVersion() {
    return ProtocolVersion.V1;
  }

}
