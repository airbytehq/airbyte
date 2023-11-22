/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.standardtest.destination;

import static org.junit.jupiter.api.Assertions.*;

import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import org.junit.jupiter.api.Test;

class TestingNamespacesTest {

  private static final DateTimeFormatter FORMATTER = DateTimeFormatter.ofPattern("yyyyMMdd");

  @Test
  void testGenerate() {
    final String[] namespace = TestingNamespaces.generate().split("_");
    assertEquals("test", namespace[0]);
    assertEquals(FORMATTER.format(Instant.now().atZone(ZoneId.of("UTC")).toLocalDate()), namespace[1]);
    assertFalse(namespace[2].isBlank());
  }

  @Test
  void testGenerateWithPrefix() {
    final String[] namespace = TestingNamespaces.generate("myprefix").split("_");
    assertEquals("myprefix", namespace[0]);
    assertEquals("test", namespace[1]);
    assertEquals(FORMATTER.format(Instant.now().atZone(ZoneId.of("UTC")).toLocalDate()), namespace[2]);
    assertFalse(namespace[3].isBlank());
  }

  @Test
  void testIsOlderThan2Days() {
    assertFalse(TestingNamespaces.isOlderThan2Days("myprefix_test_" + getDate(0) + "_12345"));
    assertTrue(TestingNamespaces.isOlderThan2Days("myprefix_test_" + getDate(2) + "_12345"));
  }

  @Test
  void doesNotFailOnNonConventionalNames() {
    assertFalse(TestingNamespaces.isOlderThan2Days("12345"));
    assertFalse(TestingNamespaces.isOlderThan2Days("test_12345"));
    assertFalse(TestingNamespaces.isOlderThan2Days("hello_test_12345"));
    assertFalse(TestingNamespaces.isOlderThan2Days("myprefix_test1_" + getDate(2) + "_12345"));

  }

  private static String getDate(final int daysAgo) {
    return FORMATTER.format(Instant.now().minus(daysAgo, ChronoUnit.DAYS).atZone(ZoneId.of("UTC")).toLocalDate());
  }

}
