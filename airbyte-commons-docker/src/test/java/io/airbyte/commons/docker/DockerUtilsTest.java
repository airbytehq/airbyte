/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.docker;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class DockerUtilsTest {

  @Test
  void testGetTaggedImageName() {
    String repository = "airbyte/repo";
    String tag = "12.3";
    assertEquals("airbyte/repo:12.3", DockerUtils.getTaggedImageName(repository, tag));
  }

}
