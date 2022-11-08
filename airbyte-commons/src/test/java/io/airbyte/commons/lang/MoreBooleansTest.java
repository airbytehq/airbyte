/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.lang;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

class MoreBooleansTest {

  @SuppressWarnings("ConstantConditions")
  @Test
  void evaluateNullAsFalse() {
    assertTrue(MoreBooleans.isTruthy(Boolean.TRUE));
    assertFalse(MoreBooleans.isTruthy(Boolean.FALSE));
    assertFalse(MoreBooleans.isTruthy(null));
  }

}
