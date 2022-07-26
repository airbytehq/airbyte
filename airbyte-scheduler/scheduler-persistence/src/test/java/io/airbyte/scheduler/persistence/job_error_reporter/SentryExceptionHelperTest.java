/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_error_reporter;

import io.sentry.protocol.SentryException;
import io.sentry.protocol.SentryStackFrame;
import io.sentry.protocol.SentryStackTrace;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class SentryExceptionHelperTest {

  final SentryExceptionHelper exceptionHelper = new SentryExceptionHelper();

  @Test
  void testBuildSentryExceptionsInvalid() {
    final String stacktrace = "this is not a stacktrace";
    final Optional<List<SentryException>> exceptionList = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(exceptionList.isEmpty());
  }

  @Test
  void testBuildSentryExceptionsPartiallyInvalid() {
    final String stacktrace = "Traceback (most recent call last):\n  Oops!";
    final Optional<List<SentryException>> exceptionList = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(exceptionList.isEmpty());
  }

  @Test
  void testBuildSentryExceptionsPythonChained() {
    final String stacktrace =
        """
        Traceback (most recent call last):
          File "/airbyte/connector-errors/error.py", line 31, in read_records
            failing_method()
          File "/airbyte/connector-errors/error.py", line 36, in failing_method
            raise HTTPError(http_error_msg, response=self)
        requests.exceptions.HTTPError: 400 Client Error: Bad Request for url: https://airbyte.com

        The above exception was the direct cause of the following exception:

        Traceback (most recent call last):
          File "/airbyte/connector-errors/error.py", line 39, in <module>
            main()
          File "/airbyte/connector-errors/error.py", line 13, in main
            sync_mode("incremental")
          File "/airbyte/connector-errors/error.py", line 17, in sync_mode
            incremental()
          File "/airbyte/connector-errors/error.py", line 33, in incremental
            raise RuntimeError("My other error") from err
        RuntimeError: My other error
        """;

    final Optional<List<SentryException>> optionalSentryExceptions = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(optionalSentryExceptions.isPresent());
    final List<SentryException> exceptionList = optionalSentryExceptions.get();
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
  void testBuildSentryExceptionsPythonNoValue() {
    final String stacktrace =
        """
        Traceback (most recent call last):
          File "/airbyte/connector-errors/error.py", line 33, in incremental
            raise RuntimeError()
        RuntimeError
        """;

    final Optional<List<SentryException>> optionalSentryExceptions = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(optionalSentryExceptions.isPresent());
    final List<SentryException> exceptionList = optionalSentryExceptions.get();
    Assertions.assertEquals(1, exceptionList.size());

    assertExceptionContent(exceptionList.get(0), "RuntimeError", null, List.of(
        Map.of(
            "abspath", "/airbyte/connector-errors/error.py",
            "lineno", 33,
            "function", "incremental",
            "context_line", "raise RuntimeError()")));
  }

  @Test
  void testBuildSentryExceptionsPythonMultilineValue() {
    final String stacktrace =
        """
        Traceback (most recent call last):
          File "/usr/local/lib/python3.9/site-packages/grpc/_channel.py", line 849, in _end_unary_response_blocking
            raise _InactiveRpcError(state)
        grpc._channel._InactiveRpcError: <_InactiveRpcError of RPC that terminated with:
          status = StatusCode.INTERNAL
          details = "Internal error encountered."
        >

        During handling of the above exception, another exception occurred:

        Traceback (most recent call last):
          File "/usr/local/lib/python3.9/site-packages/google/api_core/exceptions.py", line 553, in _parse_grpc_error_details
            status = rpc_status.from_call(rpc_exc)
        AttributeError: 'NoneType' object has no attribute 'from_call'
        """;

    final Optional<List<SentryException>> optionalSentryExceptions = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(optionalSentryExceptions.isPresent());
    final List<SentryException> exceptionList = optionalSentryExceptions.get();
    Assertions.assertEquals(2, exceptionList.size());

    final String expectedValue =
        """
        <_InactiveRpcError of RPC that terminated with:
          status = StatusCode.INTERNAL
          details = "Internal error encountered."
        >""";

    assertExceptionContent(exceptionList.get(0), "grpc._channel._InactiveRpcError", expectedValue, List.of(
        Map.of(
            "abspath", "/usr/local/lib/python3.9/site-packages/grpc/_channel.py",
            "lineno", 849,
            "function", "_end_unary_response_blocking",
            "context_line", "raise _InactiveRpcError(state)")));

    assertExceptionContent(exceptionList.get(1), "AttributeError", "'NoneType' object has no attribute 'from_call'", List.of(
        Map.of(
            "abspath", "/usr/local/lib/python3.9/site-packages/google/api_core/exceptions.py",
            "lineno", 553,
            "function", "_parse_grpc_error_details",
            "context_line", "status = rpc_status.from_call(rpc_exc)")));
  }

  @Test
  void testBuildSentryExceptionsJava() {
    final String stacktrace =
        """
        java.lang.ArithmeticException: / by zero
        	at io.airbyte.integrations.base.AirbyteTraceMessageUtilityTest.testCorrectStacktraceFormat(AirbyteTraceMessageUtilityTest.java:61)
        	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
        	at org.junit.jupiter.engine.execution.ExecutableInvoker$ReflectiveInterceptorCall.lambda$ofVoidMethod$0(ExecutableInvoker.java:115)
        	at app//org.junit.platform.engine.support.hierarchical.NodeTestTask.lambda$executeRecursively$8(NodeTestTask.java:141)
        	at org.junit.platform.engine.support.hierarchical.ThrowableCollector.execute(ThrowableCollector.java:73)
        	at jdk.proxy2/jdk.proxy2.$Proxy5.stop(Unknown Source)
        	at worker.org.gradle.process.internal.worker.GradleWorkerMain.main(GradleWorkerMain.java:74)
        """;

    final Optional<List<SentryException>> optionalSentryExceptions = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(optionalSentryExceptions.isPresent());
    final List<SentryException> exceptionList = optionalSentryExceptions.get();
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
  void testBuildSentryExceptionsJavaChained() {
    final String stacktrace =
        """
        java.util.concurrent.CompletionException: io.airbyte.workers.DefaultReplicationWorker$DestinationException: Destination process exited with non-zero exit code 1
        	at java.base/java.util.concurrent.CompletableFuture.encodeThrowable(CompletableFuture.java:315)
        	at java.base/java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:635)
        	at java.base/java.lang.Thread.run(Thread.java:833)
        		Suppressed: io.airbyte.workers.exception.WorkerException: Source process exit with code 1. This warning is normal if the job was cancelled.
        				at io.airbyte.workers.internal.DefaultAirbyteSource.close(DefaultAirbyteSource.java:136)
        				at io.airbyte.workers.general.DefaultReplicationWorker.run(DefaultReplicationWorker.java:137)
        				at io.airbyte.workers.general.DefaultReplicationWorker.run(DefaultReplicationWorker.java:65)
        				at io.airbyte.workers.temporal.TemporalAttemptExecution.lambda$getWorkerThread$2(TemporalAttemptExecution.java:158)
        				at java.lang.Thread.run(Thread.java:833)
        Caused by: io.airbyte.workers.DefaultReplicationWorker$DestinationException: Destination process exited with non-zero exit code 1
        	at io.airbyte.workers.DefaultReplicationWorker.lambda$getDestinationOutputRunnable$7(DefaultReplicationWorker.java:397)
        	at java.base/java.util.concurrent.CompletableFuture$AsyncRun.run(CompletableFuture.java:1804)
        	... 3 more
        """;

    final Optional<List<SentryException>> optionalSentryExceptions = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(optionalSentryExceptions.isPresent());
    final List<SentryException> exceptionList = optionalSentryExceptions.get();
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

  @Test
  void testBuildSentryExceptionsJavaMultilineValue() {
    final String stacktrace =
        """
        io.temporal.failure.ApplicationFailure: GET https://storage.googleapis.com/
        {
          "code" : 401,
          "message" : "Invalid Credentials"
        }
        	at com.google.api.client.googleapis.json.GoogleJsonResponseException.from(GoogleJsonResponseException.java:146)
          ... 22 more
        """;

    final Optional<List<SentryException>> optionalSentryExceptions = exceptionHelper.buildSentryExceptions(stacktrace);
    Assertions.assertTrue(optionalSentryExceptions.isPresent());
    final List<SentryException> exceptionList = optionalSentryExceptions.get();
    Assertions.assertEquals(1, exceptionList.size());

    final String expectedValue =
        """
        GET https://storage.googleapis.com/
        {
          "code" : 401,
          "message" : "Invalid Credentials"
        }""";

    assertExceptionContent(exceptionList.get(0), "io.temporal.failure.ApplicationFailure",
        expectedValue, List.of(
            Map.of(
                "filename", "GoogleJsonResponseException.java",
                "lineno", 146,
                "module", "com.google.api.client.googleapis.json.GoogleJsonResponseException",
                "function", "from")));
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
