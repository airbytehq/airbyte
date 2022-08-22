/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.google.common.collect.ImmutableMap;
import java.util.Map;
import org.junit.jupiter.api.Test;

@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class PgLsnTest {

  private static final Map<String, Long> TEST_LSNS = ImmutableMap.<String, Long>builder()
      .put("0/15E7A10", 22968848L)
      .put("0/15E7B08", 22969096L)
      .put("16/15E7B08", 94512249608L)
      .put("16/FFFFFFFF", 98784247807L)
      .put("7FFFFFFF/FFFFFFFF", Long.MAX_VALUE)
      .put("0/0", 0L)
      .build();

  // Example Map used to run test case.
  private static final Map<String, Long> EXPECTED_TEST_LSNS = ImmutableMap.<String, Long>builder()
      .put("PgLsn{lsn=22968848}", 22968848L)
      .put("PgLsn{lsn=22969096}", 22969096L)
      .put("PgLsn{lsn=94512249608}", 94512249608L)
      .put("PgLsn{lsn=98784247807}", 98784247807L)
      .put("PgLsn{lsn=9223372036854775807}", Long.MAX_VALUE)
      .put("PgLsn{lsn=0}", 0L)
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

  // Added Test Case to test .toString() method in PgLsn.java
  @Test
  void testLsnToString() {
    EXPECTED_TEST_LSNS.forEach(
        (key, value) -> assertEquals(key, PgLsn.fromLong(value).toString(), String.format("Conversion failed. string: %s lsn: %s", key, value)));
  }

}
