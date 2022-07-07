/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.resources;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.google.common.collect.Sets;
import io.airbyte.commons.io.IOs;
import java.io.File;
import java.io.IOException;
import java.net.URISyntaxException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

class MoreResourcesTest {

  @Test
  void testResourceRead() throws IOException {
    assertEquals("content1\n", MoreResources.readResource("resource_test"));
    assertEquals("content2\n", MoreResources.readResource("subdir/resource_test_sub"));

    assertThrows(IllegalArgumentException.class, () -> MoreResources.readResource("invalid"));
  }

  @Test
  void testResourceReadWithClass() throws IOException {
    assertEquals("content1\n", MoreResources.readResource(MoreResourcesTest.class, "resource_test"));
    assertEquals("content2\n", MoreResources.readResource(MoreResourcesTest.class, "subdir/resource_test_sub"));

    assertEquals("content1\n", MoreResources.readResource(MoreResourcesTest.class, "/resource_test"));
    assertEquals("content2\n", MoreResources.readResource(MoreResourcesTest.class, "/subdir/resource_test_sub"));

    assertThrows(IllegalArgumentException.class, () -> MoreResources.readResource(MoreResourcesTest.class, "invalid"));
  }

  @Test
  void testReadResourceAsFile() throws URISyntaxException {
    final File file = MoreResources.readResourceAsFile("resource_test");
    assertEquals("content1\n", IOs.readFile(file.toPath()));
  }

  @Test
  void testReadBytes() throws IOException {
    assertEquals("content1\n", new String(MoreResources.readBytes("resource_test"), StandardCharsets.UTF_8));
    assertEquals("content2\n", new String(MoreResources.readBytes("subdir/resource_test_sub"), StandardCharsets.UTF_8));

    assertThrows(IllegalArgumentException.class, () -> MoreResources.readBytes("invalid"));
  }

  @Test
  void testResourceReadDuplicateName() throws IOException {
    assertEquals("content1\n", MoreResources.readResource("resource_test_a"));
    assertEquals("content2\n", MoreResources.readResource("subdir/resource_test_a"));
  }

  @Test
  void testListResource() throws IOException {
    assertEquals(
        Sets.newHashSet("subdir", "resource_test_sub", "resource_test_sub_2", "resource_test_a"),
        MoreResources.listResources(MoreResourcesTest.class, "subdir")
            .map(Path::getFileName)
            .map(Path::toString)
            .collect(Collectors.toSet()));
  }

}
