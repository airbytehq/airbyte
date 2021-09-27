/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.app;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class JobLogsTest {

  @Test
  public void testGetLogDirectory() {
    final String actual = JobLogs.getLogDirectory("blah");
    final String expected = "logs/jobs/blah";
    assertEquals(expected, actual);
  }

}
