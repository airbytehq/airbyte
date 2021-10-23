/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.cli;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class ClisTest {

  @Test
  void testGetTaggedImageName() {
    final String repository = "airbyte/repo";
    final String tag = "12.3";
    assertEquals("airbyte/repo:12.3", Clis.getTaggedImageName(repository, tag));
  }

}
