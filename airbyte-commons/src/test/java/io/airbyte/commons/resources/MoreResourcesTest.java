/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.commons.resources;

import static org.junit.jupiter.api.Assertions.*;

import com.google.common.collect.Sets;
import java.io.IOException;
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

  @Test
  void testWriteResource() throws IOException {
    final String contents = "something to remember";
    MoreResources.writeResource("file.txt", contents);
    assertEquals(contents, MoreResources.readResource("file.txt"));
  }

}
