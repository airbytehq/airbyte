/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.google.common.collect.ImmutableMap;
import java.util.Map;
import org.junit.jupiter.api.Test;

class PgLsnTest {

  private static final Map<String, Long> TEST_LSNS = ImmutableMap.<String, Long>builder()
      .put("0/15E7A10", 22968848L)
      .put("0/15E7B08", 22969096L)
      .put("16/15E7B08", 94512249608L)
      .put("16/FFFFFFFF", 98784247807L)
      .put("7FFFFFFF/FFFFFFFF", Long.MAX_VALUE)
      .put("0/0", 0L)
      .build();

  @Test
  void testLsnToLong() {
    TEST_LSNS.forEach(
        (key, value) -> assertEquals(value, PgLsn.lsnToLong(key), String.format("Conversion failed. lsn: %s long value: %s", key, value)));
  }

  @Test
  void testLongToLsn() {
    TEST_LSNS.forEach(
        (key, value) -> assertEquals(key, PgLsn.longToLsn(value), String.format("Conversion failed. lsn: %s long value: %s", key, value)));
  }

}
