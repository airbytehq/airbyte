/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.base;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.spy;

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteErrorTraceMessage;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteTraceMessage;
import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Optional;
import lombok.SneakyThrows;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

public class AirbyteExceptionHandlerTest {

  PrintStream originalOut = System.out;
  private final ByteArrayOutputStream outContent = new ByteArrayOutputStream();

  @BeforeEach
  public void setup() {
    System.setOut(new PrintStream(outContent, true, StandardCharsets.UTF_8));
  }

  @Test
  void testTraceMessageEmission() throws Exception {
    // mocking terminate() method in AirbyteExceptionHandler, so we don't kill the JVM
    final AirbyteExceptionHandler airbyteExceptionHandler = spy(new AirbyteExceptionHandler());
    doNothing().when(airbyteExceptionHandler).terminate();

    // have to spawn a new thread to test the uncaught exception handling,
    // because junit catches any exceptions in main thread, i.e. they're not 'uncaught'
    final Thread thread = new Thread() {

      @SneakyThrows
      public void run() {
        final IntegrationRunner runner = Mockito.mock(IntegrationRunner.class);
        doThrow(new RuntimeException("error")).when(runner).run(new String[] {"write"});
        runner.run(new String[] {"write"});
      }

    };
    thread.setUncaughtExceptionHandler(airbyteExceptionHandler);
    thread.start();
    thread.join();
    System.out.flush();

    // now we turn the std out from the thread into json and check it's the expected TRACE message
    final Optional<AirbyteMessage> maybeTraceMessage = findFirstTraceMessage();
    assertTrue(maybeTraceMessage.isPresent());
    final AirbyteMessage traceMessage = maybeTraceMessage.get();
    assertAll(
        () -> Assertions.assertEquals(AirbyteMessage.Type.TRACE, traceMessage.getType()),
        () -> Assertions.assertEquals(AirbyteTraceMessage.Type.ERROR, traceMessage.getTrace().getType()),
        () -> Assertions.assertEquals(AirbyteExceptionHandler.logMessage, traceMessage.getTrace().getError().getMessage()),
        () -> Assertions.assertEquals(AirbyteErrorTraceMessage.FailureType.SYSTEM_ERROR, traceMessage.getTrace().getError().getFailureType())
    );
  }

  @AfterEach
  public void teardown() {
    System.setOut(originalOut);
  }
  private Optional<AirbyteMessage> findFirstTraceMessage() {
    return Arrays.stream(outContent.toString().split("\n"))
        .map(line -> Jsons.deserialize(line, AirbyteMessage.class))
        .filter(message -> message.getType() == AirbyteMessage.Type.TRACE)
        .findFirst();
  }
}
