/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.base;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.spy;

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteErrorTraceMessage;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteTraceMessage;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
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
  private AirbyteExceptionHandler airbyteExceptionHandler;

  @BeforeEach
  public void setup() {
    System.setOut(new PrintStream(outContent, true, StandardCharsets.UTF_8));

    // mocking terminate() method in AirbyteExceptionHandler, so we don't kill the JVM
    airbyteExceptionHandler = spy(new AirbyteExceptionHandler());
    doNothing().when(airbyteExceptionHandler).terminate();

    AirbyteExceptionHandler.addThrowableForDeinterpolation(RuntimeException.class);
  }

  @Test
  void testTraceMessageEmission() throws Exception {
    runTestWithMessage("error");

    final AirbyteMessage traceMessage = findFirstTraceMessage();
    assertAll(
        () -> assertEquals(AirbyteTraceMessage.Type.ERROR, traceMessage.getTrace().getType()),
        () -> assertEquals(AirbyteExceptionHandler.logMessage, traceMessage.getTrace().getError().getMessage()),
        () -> assertEquals(AirbyteErrorTraceMessage.FailureType.SYSTEM_ERROR, traceMessage.getTrace().getError().getFailureType()));
  }

  @Test
  void testMessageDeinterpolation() throws Exception {
    AirbyteExceptionHandler.addStringForDeinterpolation("foo");
    AirbyteExceptionHandler.addStringForDeinterpolation("bar");

    runTestWithMessage("Error happened in foo.bar");

    final AirbyteMessage traceMessage = findFirstTraceMessage();
    assertAll(
        () -> assertEquals(AirbyteTraceMessage.Type.ERROR, traceMessage.getTrace().getType()),
        () -> assertEquals("Error happened in foo.bar", traceMessage.getTrace().getError().getMessage()),
        () -> assertEquals("Error happened in ?.?", traceMessage.getTrace().getError().getInternalMessage()),
        () -> assertEquals(AirbyteErrorTraceMessage.FailureType.SYSTEM_ERROR, traceMessage.getTrace().getError().getFailureType()),
        () -> Assertions.assertNull(traceMessage.getTrace().getError().getStackTrace(),
            "Stacktrace should be null if deinterpolating the error message"));
  }

  /**
   * We should only deinterpolate whole words, i.e. if the target string is not adjacent to an
   * alphanumeric character.
   */
  @Test
  void testMessageSmartDeinterpolation() throws Exception {
    AirbyteExceptionHandler.addStringForDeinterpolation("foo");
    AirbyteExceptionHandler.addStringForDeinterpolation("bar");

    runTestWithMessage("Error happened in foobar");

    final AirbyteMessage traceMessage = findFirstTraceMessage();
    // We shouldn't deinterpolate at all in this case, so we will get the default trace message
    // behavior.
    assertAll(
        () -> assertEquals(AirbyteExceptionHandler.logMessage, traceMessage.getTrace().getError().getMessage()),
        () -> assertEquals(
            "java.lang.RuntimeException: Error happened in foobar",
            traceMessage.getTrace().getError().getInternalMessage()));
  }

  /**
   * When one of the target strings is a substring of another, we should not deinterpolate the
   * substring.
   */
  @Test
  void testMessageSubstringDeinterpolation() throws Exception {
    AirbyteExceptionHandler.addStringForDeinterpolation("airbyte");
    AirbyteExceptionHandler.addStringForDeinterpolation("airbyte_internal");

    runTestWithMessage("Error happened in airbyte_internal.foo");

    final AirbyteMessage traceMessage = findFirstTraceMessage();
    assertEquals("Error happened in ?.foo", traceMessage.getTrace().getError().getInternalMessage());
  }

  /**
   * We should only deinterpolate specific exception classes.
   */
  @Test
  void testClassDeinterpolation() throws Exception {
    AirbyteExceptionHandler.addStringForDeinterpolation("foo");

    runTestWithMessage(new IOException("Error happened in foo"));

    final AirbyteMessage traceMessage = findFirstTraceMessage();
    // We shouldn't deinterpolate at all in this case, so we will get the default trace message
    // behavior.
    assertAll(
        () -> assertEquals(AirbyteExceptionHandler.logMessage, traceMessage.getTrace().getError().getMessage()),
        () -> assertEquals(
            "java.io.IOException: Error happened in foo",
            traceMessage.getTrace().getError().getInternalMessage()));
  }

  /**
   * We should check the classes of the entire exception chain, not just the root exception.
   */
  @Test
  void testNestedThrowableClassDeinterpolation() throws Exception {
    AirbyteExceptionHandler.addStringForDeinterpolation("foo");

    runTestWithMessage(new Exception(new RuntimeException("Error happened in foo")));

    final AirbyteMessage traceMessage = findFirstTraceMessage();
    // We shouldn't deinterpolate at all in this case, so we will get the default trace message
    // behavior.
    assertEquals("Error happened in ?", traceMessage.getTrace().getError().getInternalMessage());
  }

  private void runTestWithMessage(final String message) throws InterruptedException {
    runTestWithMessage(new RuntimeException(message));
  }

  private void runTestWithMessage(final Throwable throwable) throws InterruptedException {
    // have to spawn a new thread to test the uncaught exception handling,
    // because junit catches any exceptions in main thread, i.e. they're not 'uncaught'
    final Thread thread = new Thread() {

      @SneakyThrows
      public void run() {
        final IntegrationRunner runner = Mockito.mock(IntegrationRunner.class);
        doThrow(throwable).when(runner).run(new String[] {"write"});
        runner.run(new String[] {"write"});
      }

    };
    thread.setUncaughtExceptionHandler(airbyteExceptionHandler);
    thread.start();
    thread.join();
    System.out.flush();
  }

  @AfterEach
  public void teardown() {
    System.setOut(originalOut);
    AirbyteExceptionHandler.STRINGS_TO_DEINTERPOLATE.clear();
    AirbyteExceptionHandler.THROWABLES_TO_DEINTERPOLATE.clear();
  }

  private AirbyteMessage findFirstTraceMessage() {
    final Optional<AirbyteMessage> maybeTraceMessage = Arrays.stream(outContent.toString(StandardCharsets.UTF_8).split("\n"))
        .map(line -> Jsons.deserialize(line, AirbyteMessage.class))
        .filter(message -> message.getType() == AirbyteMessage.Type.TRACE)
        .findFirst();
    assertTrue(maybeTraceMessage.isPresent(), "Expected to find a trace message in stdout");
    return maybeTraceMessage.get();
  }

}
