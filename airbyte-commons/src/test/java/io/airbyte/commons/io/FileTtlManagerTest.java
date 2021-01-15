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

package io.airbyte.commons.io;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class FileTtlManagerTest {

  private Path file1;
  private Path file2;
  private Path file3;

  @BeforeEach

  void setup() throws IOException {
    Path testRoot = Files.createTempDirectory(Path.of("/tmp"), "ttl_test");
    file1 = Files.createFile(testRoot.resolve("file1"));
    file2 = Files.createFile(testRoot.resolve("file2"));
    file3 = Files.createFile(testRoot.resolve("file3"));
  }

  @Test
  void testExpiresAfterTime() throws InterruptedException {
    final FileTtlManager fileTtlManager = new FileTtlManager(1, TimeUnit.SECONDS, 10);

    assertTrue(Files.exists(file1));
    fileTtlManager.register(file1);
    fileTtlManager.register(file2);
    assertTrue(Files.exists(file1));
    Thread.sleep(10001L);
    fileTtlManager.register(file3);
    assertFalse(Files.exists(file1));
  }

  @Test
  void testExpiresAfterSizeLimit() {
    final FileTtlManager fileTtlManager = new FileTtlManager(1, TimeUnit.HOURS, 2);

    assertTrue(Files.exists(file1));
    fileTtlManager.register(file1);
    assertTrue(Files.exists(file1));
    fileTtlManager.register(file2);
    assertTrue(Files.exists(file1));
    fileTtlManager.register(file3);
    assertFalse(Files.exists(file1));
  }

}
