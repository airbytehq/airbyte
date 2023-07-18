/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.io.BufferedInputStream;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;
import org.junit.jupiter.api.Test;

public class IntegrationRunnerBackwardsCompatbilityTest {

  @Test
  void testByteArrayInputStreamVersusScanner() throws Exception {
    final String[] testInputs = new String[] {
      "This is line 1\nThis is line 2\nThis is line 3",
      "This is line 1\n\nThis is line 2\n\n\nThis is line 3",
      "This is line 1\rThis is line 2\nThis is line 3\r\nThis is line 4",
      "This is line 1 with emoji 😊\nThis is line 2 with Greek characters: Α, Β, Χ\nThis is line 3 with Cyrillic characters: Д, Ж, З",
      "This is a very long line that contains a lot of characters...",
      "This is line 1 with an escaped newline \\n character\nThis is line 2 with another escaped newline \\n character",
      "This is line 1\n\n",
      "\nThis is line 2",
      "\n"
    };

    for (final String testInput : testInputs) {
      // get new output
      final InputStream stream1 = new ByteArrayInputStream(testInput.getBytes(StandardCharsets.UTF_8));
      final MockConsumer consumer2 = new MockConsumer();
      try (final BufferedInputStream bis = new BufferedInputStream(stream1);
          final ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
        IntegrationRunner.consumeWriteStream(consumer2, bis, baos);
      }
      final List<String> newOutput = consumer2.getOutput();

      // get old output
      final List<String> oldOutput = new ArrayList<>();
      final InputStream stream2 = new ByteArrayInputStream(testInput.getBytes(StandardCharsets.UTF_8));
      final Scanner scanner = new Scanner(stream2, StandardCharsets.UTF_8).useDelimiter("[\r\n]+");
      while (scanner.hasNext()) {
        oldOutput.add(scanner.next());
      }

      assertEquals(oldOutput, newOutput);
    }
  }

  private static class MockConsumer implements SerializedAirbyteMessageConsumer {

    private final List<String> output = new ArrayList<>();

    @Override
    public void start() {

    }

    @Override
    public void accept(final String message, final Integer sizeInBytes) {
      output.add(message);
    }

    @Override
    public void close() {

    }

    public List<String> getOutput() {
      return new ArrayList<>(output);
    }

  }

}
