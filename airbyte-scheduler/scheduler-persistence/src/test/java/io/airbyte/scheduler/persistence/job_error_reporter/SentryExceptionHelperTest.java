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
  @Test
  void testBuildPythonSentryExceptions() throws IOException {
    final String stacktrace = MoreResources.readResource("sample_python_stacktrace.txt");

    final List<SentryException> exceptionList = SentryExceptionHelper.buildPythonSentryExceptions(stacktrace);
    Assertions.assertNotNull(exceptionList);
    Assertions.assertEquals(2, exceptionList.size());

    assertExceptionContent(exceptionList.get(0), "requests.exceptions.HTTPError", "400 Client Error: Bad Request for url: https://airbyte.com", List.of(
        Map.of(
            "abspath", "/airbyte/connector-errors/error.py",
            "lineno", 31,
            "function", "read_records",
            "context_line", "failing_method()"
        ),
        Map.of(
            "abspath", "/airbyte/connector-errors/error.py",
            "lineno", 36,
            "function", "failing_method",
            "context_line", "raise HTTPError(http_error_msg, response=self)"
        )
    ));

    assertExceptionContent(exceptionList.get(1), "RuntimeError", "My other error", List.of(
        Map.of(
            "abspath", "/airbyte/connector-errors/error.py",
            "lineno", 39,
            "function", "<module>",
            "context_line", "main()"
        ),
        Map.of(
            "abspath", "/airbyte/connector-errors/error.py",
            "lineno", 13,
            "function", "main",
            "context_line", "sync_mode(\"incremental\")"
        ),
        Map.of(
            "abspath", "/airbyte/connector-errors/error.py",
            "lineno", 17,
            "function", "sync_mode",
            "context_line", "incremental()"
        ),
        Map.of(
            "abspath", "/airbyte/connector-errors/error.py",
            "lineno", 33,
            "function", "incremental",
            "context_line", "raise RuntimeError(\"My other error\") from err"
        )
    ));

  }

  void assertExceptionContent(final SentryException exception, final String type, final String value, final List<Map<String, Object>> frames) {
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
    }
  }
}
