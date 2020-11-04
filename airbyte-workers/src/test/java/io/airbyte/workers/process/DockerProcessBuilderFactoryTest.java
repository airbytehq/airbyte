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

package io.airbyte.workers.process;

import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

// todo (cgardens) - these are not truly "unit" tests as they are check resources on the internet.
// we should move them to "integration" tests, when we have facility to do so.
class DockerProcessBuilderFactoryTest {

  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");

  @Test
  public void testImageExists() throws IOException {
    Path workspaceRoot = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), "pbf");

    final DockerProcessBuilderFactory pbf = new DockerProcessBuilderFactory(workspaceRoot, "", "", "");
    assertTrue(pbf.checkImageExists("airbyte/scheduler:dev"));
  }

  @Test
  public void testImageDoesNotExist() throws IOException {
    Path workspaceRoot = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), "pbf");

    final DockerProcessBuilderFactory pbf = new DockerProcessBuilderFactory(workspaceRoot, "", "", "");
    assertFalse(pbf.checkImageExists("airbyte/fake:0.1.2"));
  }

}
