/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
import java.nio.charset.StandardCharsets;
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
  void testWriteBytes() throws IOException {
    final Path path = Files.createTempDirectory("tmp");

    final Path filePath = IOs.writeFile(path.resolve("file"), "abc".getBytes(StandardCharsets.UTF_8));

    assertEquals(path.resolve("file"), filePath);
    assertEquals("abc", IOs.readFile(path, "file"));
  }

  @Test
  void testWriteFileToRandomDir() throws IOException {
    final String contents = "something to remember";
    final String tmpFilePath = IOs.writeFileToRandomTmpDir("file.txt", contents);
    assertEquals(contents, Files.readString(Path.of(tmpFilePath)));
  }

  @Test
  void testGetTailDoesNotExist() throws IOException {
    final List<String> tail = IOs.getTail(100, Path.of(RandomStringUtils.randomAlphanumeric(100)));
    assertEquals(Collections.emptyList(), tail);
  }

  @Test
  void testGetTailExists() throws IOException {
    final Path stdoutFile = Files.createTempFile("job-history-handler-test", "stdout");

    final List<String> head = List.of(
        "line1",
        "line2",
        "line3",
        "line4");

    final List<String> expectedTail = List.of(
        "line5",
        "line6",
        "line7",
        "line8");

    final Writer writer = new BufferedWriter(new FileWriter(stdoutFile.toString(), StandardCharsets.UTF_8, true));

    for (final String line : Iterables.concat(head, expectedTail)) {
      writer.write(line + "\n");
    }

    writer.close();

    final List<String> tail = IOs.getTail(expectedTail.size(), stdoutFile);
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
    final Closeable closeable = Mockito.mock(Closeable.class);

    assertDoesNotThrow(() -> IOs.silentClose(closeable));

    Mockito.doThrow(new IOException()).when(closeable).close();
    assertThrows(RuntimeException.class, () -> IOs.silentClose(closeable));
  }

}
