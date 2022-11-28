/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.text;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;

class NamesTest {

  @Test
  void testToAlphanumericAndUnderscore() {
    assertEquals("users", Names.toAlphanumericAndUnderscore("users"));
    assertEquals("users123", Names.toAlphanumericAndUnderscore("users123"));
    assertEquals("UsErS", Names.toAlphanumericAndUnderscore("UsErS"));
    assertEquals("users_USE_special_____", Names.toAlphanumericAndUnderscore("users USE special !@#$"));
  }

  @Test
  void testDoubleQuote() {
    assertEquals("\"abc\"", Names.doubleQuote("abc"));
    assertEquals("\"abc\"", Names.doubleQuote("\"abc\""));
    assertThrows(IllegalStateException.class, () -> Names.doubleQuote("\"abc"));
    assertThrows(IllegalStateException.class, () -> Names.doubleQuote("abc\""));
  }

  @Test
  void testSimpleQuote() {
    assertEquals("'abc'", Names.singleQuote("abc"));
    assertEquals("'abc'", Names.singleQuote("'abc'"));
    assertThrows(IllegalStateException.class, () -> Names.singleQuote("'abc"));
    assertThrows(IllegalStateException.class, () -> Names.singleQuote("abc'"));
  }

}
