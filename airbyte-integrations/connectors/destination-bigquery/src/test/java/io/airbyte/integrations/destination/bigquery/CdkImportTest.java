/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import io.airbyte.cdk.CDKConstants;

class CdkImportTest {

  /**
   * This test ensures that the CDK is able to be imported and that its version number matches the expected pinned version.
   */
  @Test
  void cdkVersionShouldMatch() {
    assertEquals("0.0.1", CDKConstants.VERSION.replace("-SNAPSHOT", ""));
  }

}
