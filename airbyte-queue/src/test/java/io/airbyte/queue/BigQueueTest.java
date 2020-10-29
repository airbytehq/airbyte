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

package io.airbyte.queue;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.google.common.base.Charsets;
import io.airbyte.commons.lang.CloseableQueue;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Objects;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class BigQueueTest {

  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");
  private CloseableQueue<byte[]> queue;

  @BeforeEach
  void setup() throws IOException {
    queue = new BigQueue(Files.createTempDirectory(Files.createDirectories(TEST_ROOT), "test"), "test");
  }

  @AfterEach
  void teardown() throws Exception {
    queue.close();
  }

  @Test
  void testPoll() {
    queue.offer(toBytes("hello"));
    assertEquals("hello", new String(Objects.requireNonNull(queue.poll()), Charsets.UTF_8));
  }

  @Test
  void testPeek() {
    queue.offer(toBytes("hello"));
    assertEquals("hello", new String(Objects.requireNonNull(queue.peek()), Charsets.UTF_8));
    assertEquals("hello", new String(Objects.requireNonNull(queue.peek()), Charsets.UTF_8));
    assertEquals("hello", new String(Objects.requireNonNull(queue.poll()), Charsets.UTF_8));
  }

  @Test
  void testSize() {
    assertEquals(0, queue.size());
    queue.offer(toBytes("hello"));
    assertEquals(1, queue.size());
    queue.offer(toBytes("hello"));
    assertEquals(2, queue.size());
  }

  @Test
  void testClosed() throws Exception {
    queue.close();
    assertDoesNotThrow(() -> queue.close());
    assertThrows(IllegalStateException.class, () -> queue.offer(toBytes("hello")));
    assertThrows(IllegalStateException.class, () -> queue.poll());
    assertThrows(IllegalStateException.class, () -> queue.iterator());
  }

  @SuppressWarnings("SameParameterValue")
  private static byte[] toBytes(String string) {
    return string.getBytes(Charsets.UTF_8);
  }

}
