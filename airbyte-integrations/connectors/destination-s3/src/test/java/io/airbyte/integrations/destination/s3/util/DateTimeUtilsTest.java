/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.util;

import static io.airbyte.integrations.destination.s3.util.DateTimeUtils.*;
import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

public class DateTimeUtilsTest {

  @Test
  public void testDateTimeConversion() {

    assertEquals(1537012800000L, getEpochMillis("2018-09-15 12:00:00"));
    assertEquals(1537012800006L, getEpochMillis("2018-09-15 12:00:00.006542"));
    assertEquals(1537012800000L, getEpochMillis("2018/09/15 12:00:00"));
    assertEquals(1537012800000L, getEpochMillis("2018.09.15 12:00:00"));
    assertEquals(1531656000000L, getEpochMillis("2018 Jul 15 12:00:00"));
    assertEquals(1531627200000L, getEpochMillis("2018 Jul 15 12:00:00 GMT+08:00"));
    assertEquals(1531630800000L, getEpochMillis("2018 Jul 15 12:00:00GMT+07"));
    assertEquals(1609462861000L, getEpochMillis("2021-1-1 01:01:01"));
    assertEquals(1609462861000L, getEpochMillis("2021.1.1 01:01:01"));
    assertEquals(1609462861000L, getEpochMillis("2021/1/1 01:01:01"));
    assertEquals(1609459261000L, getEpochMillis("2021-1-1 01:01:01 +01"));
    assertEquals(1609459261000L, getEpochMillis("2021-01-01T01:01:01+01:00"));
    assertEquals(1609459261546L, getEpochMillis("2021-01-01T01:01:01.546+01:00"));
    assertEquals(1609462861000L, getEpochMillis("2021-01-01 01:01:01"));
    assertEquals(1609462861000L, getEpochMillis("2021-01-01 01:01:01 +0000"));
    assertEquals(1609462861000L, getEpochMillis("2021/01/01 01:01:01 +0000"));
    assertEquals(1609462861000L, getEpochMillis("2021-01-01T01:01:01Z"));
    assertEquals(1609466461000L, getEpochMillis("2021-01-01T01:01:01-01:00"));
    assertEquals(1609459261000L, getEpochMillis("2021-01-01T01:01:01+01:00"));
    assertEquals(1609462861000L, getEpochMillis("2021-01-01 01:01:01 UTC"));
    assertEquals(1609491661000L, getEpochMillis("2021-01-01T01:01:01 PST"));
    assertEquals(1609462861000L, getEpochMillis("2021-01-01T01:01:01 +0000"));
    assertEquals(1609462861000L, getEpochMillis("2021-01-01T01:01:01+0000"));
    assertEquals(1609462861000L, getEpochMillis("2021-01-01T01:01:01UTC"));
    assertEquals(1609459261000L, getEpochMillis("2021-01-01T01:01:01+01"));

    assertEquals(18628, getEpochDay("2021-1-1"));
    assertEquals(18628, getEpochDay("2021-01-01"));
    assertEquals(18629, getEpochDay("2021/01/02"));
    assertEquals(18630, getEpochDay("2021.01.03"));
    assertEquals(18631, getEpochDay("2021 Jan 04"));

    assertEquals(3661000000L, getMicroSeconds("01:01:01"));
    assertEquals(3660000000L, getMicroSeconds("01:01"));
    assertEquals(44581541000L, getMicroSeconds("12:23:01.541"));
    assertEquals(44581541214L, getMicroSeconds("12:23:01.541214"));
  }

}
