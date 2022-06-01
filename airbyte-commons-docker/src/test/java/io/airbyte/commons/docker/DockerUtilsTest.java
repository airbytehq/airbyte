/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.docker;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class DockerUtilsTest {

  @Test
  void testGetTaggedImageName() {
    final String repository = "airbyte/repo";
    final String tag = "12.3";
    assertEquals("airbyte/repo:12.3", DockerUtils.getTaggedImageName(repository, tag));
  }

}
