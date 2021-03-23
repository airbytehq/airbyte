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

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.google.common.collect.Iterables;
import java.io.BufferedWriter;
import java.io.Closeable;
import java.io.FileWriter;
import java.io.IOException;
import java.io.Writer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collections;
import java.util.List;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

class IOsTest {

  @Test
  void testReadWrite() throws IOException {
    final Path path = Files.createTempDirectory("tmp");

    final Path filePath = IOs.writeFile(path, "file", "abc");

    assertEquals(path.resolve("file"), filePath);
    assertEquals("abc", IOs.readFile(path, "file"));
    assertEquals("abc", IOs.readFile(path.resolve("file")));
  }

  @Test
  public void testGetTailDoesNotExist() throws IOException {
    List<String> tail = IOs.getTail(100, Path.of(RandomStringUtils.random(100)));
    assertEquals(Collections.emptyList(), tail);
  }

  @Test
  public void testGetTailExists() throws IOException {
    Path stdoutFile = Files.createTempFile("job-history-handler-test", "stdout");

    List<String> head = List.of(
        "line1",
        "line2",
        "line3",
        "line4");

    List<String> expectedTail = List.of(
        "line5",
        "line6",
        "line7",
        "line8");

    Writer writer = new BufferedWriter(new FileWriter(stdoutFile.toString(), true));

    for (String line : Iterables.concat(head, expectedTail)) {
      writer.write(line + "\n");
    }

    writer.close();

    List<String> tail = IOs.getTail(expectedTail.size(), stdoutFile);
    assertEquals(expectedTail, tail);
  }

  @Test
  void testInputStream() {
    assertThrows(RuntimeException.class, () -> {
      IOs.inputStream(Path.of("idontexist"));
    });
  }

  @Test
  void testSilentClose() throws IOException {
    Closeable closeable = Mockito.mock(Closeable.class);

    assertDoesNotThrow(() -> IOs.silentClose(closeable));

    Mockito.doThrow(new IOException()).when(closeable).close();
    assertThrows(RuntimeException.class, () -> IOs.silentClose(closeable));
  }

}
