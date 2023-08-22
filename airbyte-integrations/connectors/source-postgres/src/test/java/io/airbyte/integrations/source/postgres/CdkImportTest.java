/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.postgres;

import static org.junit.Assert.assertTrue;
import static org.junit.jupiter.api.Assertions.*;

import io.airbyte.cdk.CDKConstants;
import org.junit.jupiter.api.Test;

class CdkImportTest {

  /**
   * This test ensures that the CDK is able to be imported and that its version number matches the expected pinned version.
   *
   * This test can be removed once pinned CDK version reaches v0.1, at which point the CDK will be used for base-java imports,
   * and this test will no longer be necessary.
   */
  @Test
  void cdkVersionShouldMatch() {
    // Should fail in unit test phase:
    assertEquals("0.0.2", CDKConstants.VERSION.replace("-SNAPSHOT", ""));
  }

}
