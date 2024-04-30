/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination;

import io.airbyte.cdk.integrations.destination.gcs.GcsBaseJsonlDestinationAcceptanceTest;

public class GcsJsonlDestinationAcceptanceTest extends GcsBaseJsonlDestinationAcceptanceTest {

  @Override
  protected String getImageName() {
    return "airbyte/destination-gcs:dev";
  }

}
