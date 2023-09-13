/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

class CDKConstantsTest {

  /* TODO: Remove these canary tests once real tests are in place. */
  @Test
  void getVersion() {
    assertEquals("0.0.2", CDKConstants.VERSION.replace("-SNAPSHOT", ""));
  }

  @Test
  // Comment out this line to force failure:
  @Disabled("This is an intentionally failing test (skipped).")
  void mustFail() {
    fail("This is an intentionally failing test.");
  }

}
