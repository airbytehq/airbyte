/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class PostgresSourceOperationsTest {

  @Test
  public void testParseMoneyValue() {
    assertEquals("1000000.00", PostgresSourceOperations.parseMoneyValue("1000000.00"));
    assertEquals("1000000", PostgresSourceOperations.parseMoneyValue("$1000000"));
    assertEquals("-1000000.01", PostgresSourceOperations.parseMoneyValue("-1,000,000.01"));
    assertEquals("1000000.0", PostgresSourceOperations.parseMoneyValue("1,000,000.0"));
    assertEquals("1000000.0", PostgresSourceOperations.parseMoneyValue("1|000|000.0"));
    assertEquals("-1000000.001", PostgresSourceOperations.parseMoneyValue("-£1,000,000.001"));
  }

}
