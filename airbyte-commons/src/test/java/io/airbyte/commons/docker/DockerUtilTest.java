package io.airbyte.commons.docker;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class DockerUtilTest {

  @Test
  void testGetTaggedImageName() {
    String repository = "airbyte/repo";
    String tag = "12.3";
    assertEquals("airbyte/repo:12.3", DockerUtil.getTaggedImageName(repository, tag));
  }
}
