/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_error_reporter;

import io.airbyte.commons.resources.MoreResources;
import io.sentry.protocol.SentryException;
import io.sentry.protocol.SentryStackFrame;
import io.sentry.protocol.SentryStackTrace;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class SentryExceptionHelperTest {

  final SentryExceptionHelper exceptionHelper = new SentryExceptionHelper();
  @Test
  void testBuildSentryExceptionsPython() throws IOException {
    final String stacktrace = MoreResources.readResource("sample_python_stacktrace.txt");

    final List<SentryException> exceptionList = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertNotNull(exceptionList);
    Assertions.assertEquals(2, exceptionList.size());

    assertExceptionContent(exceptionList.get(0), "requests.exceptions.HTTPError", "400 Client Error: Bad Request for url: https://airbyte.com",
        List.of(
            Map.of(
                "abspath", "/airbyte/connector-errors/error.py",
                "lineno", 31,
                "function", "read_records",
                "context_line", "failing_method()"),
            Map.of(
                "abspath", "/airbyte/connector-errors/error.py",
                "lineno", 36,
                "function", "failing_method",
                "context_line", "raise HTTPError(http_error_msg, response=self)")));

    assertExceptionContent(exceptionList.get(1), "RuntimeError", "My other error", List.of(
        Map.of(
            "abspath", "/airbyte/connector-errors/error.py",
            "lineno", 39,
            "function", "<module>",
            "context_line", "main()"),
        Map.of(
            "abspath", "/airbyte/connector-errors/error.py",
            "lineno", 13,
            "function", "main",
            "context_line", "sync_mode(\"incremental\")"),
        Map.of(
            "abspath", "/airbyte/connector-errors/error.py",
            "lineno", 17,
            "function", "sync_mode",
            "context_line", "incremental()"),
        Map.of(
            "abspath", "/airbyte/connector-errors/error.py",
            "lineno", 33,
            "function", "incremental",
            "context_line", "raise RuntimeError(\"My other error\") from err")));

  }

  @Test
  void testBuildSentryExceptionsInvalid() {
    final String stacktrace = "this is not a stacktrace";

    final List<SentryException> exceptionList = SentryExceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertNull(exceptionList);
  }

  @Test
  void testBuildSentryExceptionsJava() throws IOException {
    final String stacktrace = MoreResources.readResource("sample_java_stacktrace.txt");

    final List<SentryException> exceptionList = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertNotNull(exceptionList);
    Assertions.assertEquals(1, exceptionList.size());

    assertExceptionContent(exceptionList.get(0), "java.lang.ArithmeticException", "/ by zero",
        List.of(
            Map.of(
                "filename", "GradleWorkerMain.java",
                "lineno", 74,
                "module", "worker.org.gradle.process.internal.worker.GradleWorkerMain",
                "function", "main"),
            Map.of(
                "module", "jdk.proxy2.$Proxy5",
                "function", "stop"),
            Map.of(
                "filename", "ThrowableCollector.java",
                "lineno", 73,
                "module", "org.junit.platform.engine.support.hierarchical.ThrowableCollector",
                "function", "execute"),
            Map.of(
                "filename", "NodeTestTask.java",
                "lineno", 141,
                "module", "org.junit.platform.engine.support.hierarchical.NodeTestTask",
                "function", "lambda$executeRecursively$8"),
            Map.of(
                "filename", "ExecutableInvoker.java",
                "lineno", 115,
                "module", "org.junit.jupiter.engine.execution.ExecutableInvoker$ReflectiveInterceptorCall",
                "function", "lambda$ofVoidMethod$0"),
            Map.of(
                "isNative", true,
                "module", "jdk.internal.reflect.NativeMethodAccessorImpl",
                "function", "invoke0"),
            Map.of(
                "filename", "AirbyteTraceMessageUtilityTest.java",
                "lineno", 61,
                "module", "io.airbyte.integrations.base.AirbyteTraceMessageUtilityTest",
                "function", "testCorrectStacktraceFormat")));
  }

  @Test
  void testBuildSentryExceptionsJavaChained() throws IOException {
    final String stacktrace = MoreResources.readResource("sample_java_stacktrace_chained.txt");

    final List<SentryException> exceptionList = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertNotNull(exceptionList);
    Assertions.assertEquals(2, exceptionList.size());

    assertExceptionContent(exceptionList.get(0), "java.util.concurrent.CompletionException",
        "io.airbyte.workers.DefaultReplicationWorker$DestinationException: Destination process exited with non-zero exit code 1",
        List.of(
            Map.of(
                "filename", "Thread.java",
                "lineno", 833,
                "module", "java.lang.Thread",
                "function", "run"),
            Map.of(
                "filename", "ThreadPoolExecutor.java",
                "lineno", 635,
                "module", "java.util.concurrent.ThreadPoolExecutor$Worker",
                "function", "run"),
            Map.of(
                "filename", "CompletableFuture.java",
                "lineno", 315,
                "module", "java.util.concurrent.CompletableFuture",
                "function", "encodeThrowable")));

    assertExceptionContent(exceptionList.get(1), "io.airbyte.workers.DefaultReplicationWorker$DestinationException",
        "Destination process exited with non-zero exit code 1", List.of(
            Map.of(
                "filename", "CompletableFuture.java",
                "lineno", 1804,
                "module", "java.util.concurrent.CompletableFuture$AsyncRun",
                "function", "run"),
            Map.of(
                "filename", "DefaultReplicationWorker.java",
                "lineno", 397,
                "module", "io.airbyte.workers.DefaultReplicationWorker",
                "function", "lambda$getDestinationOutputRunnable$7")));
  }

  private void assertExceptionContent(final SentryException exception,
                                      final String type,
                                      final String value,
                                      final List<Map<String, Object>> frames) {
    Assertions.assertEquals(type, exception.getType());
    Assertions.assertEquals(value, exception.getValue());

    final SentryStackTrace stackTrace = exception.getStacktrace();
    Assertions.assertNotNull(stackTrace);
    final List<SentryStackFrame> sentryFrames = stackTrace.getFrames();
    Assertions.assertNotNull(sentryFrames);
    Assertions.assertEquals(frames.size(), sentryFrames.size());

    for (int i = 0; i < frames.size(); i++) {
      final Map<String, Object> expectedFrame = frames.get(i);
      final SentryStackFrame sentryFrame = sentryFrames.get(i);

      if (expectedFrame.containsKey("module")) {
        Assertions.assertEquals(expectedFrame.get("module"), sentryFrame.getModule());
      }

      if (expectedFrame.containsKey("filename")) {
        Assertions.assertEquals(expectedFrame.get("filename"), sentryFrame.getFilename());
      }

      if (expectedFrame.containsKey("abspath")) {
        Assertions.assertEquals(expectedFrame.get("abspath"), sentryFrame.getAbsPath());
      }

      if (expectedFrame.containsKey("function")) {
        Assertions.assertEquals(expectedFrame.get("function"), sentryFrame.getFunction());
      }

      if (expectedFrame.containsKey("lineno")) {
        Assertions.assertEquals(expectedFrame.get("lineno"), sentryFrame.getLineno());
      }

      if (expectedFrame.containsKey("context_line")) {
        Assertions.assertEquals(expectedFrame.get("context_line"), sentryFrame.getContextLine());
      }

      if (expectedFrame.containsKey("isNative")) {
        Assertions.assertEquals(expectedFrame.get("isNative"), sentryFrame.isNative());
      }
    }
  }

}
