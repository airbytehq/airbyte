package io.airbyte.scheduler.persistence.job_error_reporter;

import io.airbyte.commons.lang.Exceptions;
import io.sentry.protocol.SentryException;
import io.sentry.protocol.SentryStackFrame;
import io.sentry.protocol.SentryStackTrace;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class SentryExceptionHelper {
  public static List<SentryException> buildSentryExceptions(final String stacktrace) {
    // Stack trace parsing should be done on a best-effort basis
    // if we encounter something complex or an unsupported language, we'll fall back to message-based grouping instead
    return Exceptions.swallowWithDefault(() -> {
      if (stacktrace.startsWith("Traceback (most recent call last):")) {
        return buildPythonSentryExceptions(stacktrace);
      }
      if (stacktrace.contains(".java")) {
        return buildJavaSentryExceptions(stacktrace);
      }

      return null;
    }, null);
  }

  public static List<SentryException> buildPythonSentryExceptions(final String stacktrace) {
    final List<SentryException> sentryExceptions = new ArrayList<>();
    final String[] exceptions = stacktrace.split("\n\n"); // chained exceptions are separated by two new lines

    for (final String exceptionStr : exceptions) {
      final SentryStackTrace stackTrace = new SentryStackTrace();
      final List<SentryStackFrame> stackFrames = new ArrayList<>();

      // Use a regex to grab stack trace frame information
      final Pattern framePattern = Pattern.compile("File \"(?<absPath>.+)\", line (?<lineno>[0-9]+), in (?<function>.+)\\n {4}(?<contextLine>.+)\\n");
      final Matcher matcher = framePattern.matcher(exceptionStr);
      int lastMatchIdx = -1;

      while (matcher.find()) {
        final String absPath = matcher.group("absPath");
        final String lineno = matcher.group("lineno");
        final String function = matcher.group("function");
        final String contextLine = matcher.group("contextLine");

        final SentryStackFrame stackFrame = new SentryStackFrame();
        stackFrame.setAbsPath(absPath);
        stackFrame.setLineno(Integer.valueOf(lineno));
        stackFrame.setFunction(function);
        stackFrame.setContextLine(contextLine);
        stackFrames.add(stackFrame);

        lastMatchIdx = matcher.end();
      }

      if (stackFrames.size() > 0) {
        stackTrace.setFrames(stackFrames);

        final SentryException sentryException = new SentryException();
        sentryException.setStacktrace(stackTrace);

        // The final part of our stack trace has the exception type and (optionally) a value (e.g. "RuntimeError: This is the value")
        final String remaining = exceptionStr.substring(lastMatchIdx);
        final String[] parts = remaining.split(": ", 2);

        if (parts.length > 0) {
          sentryException.setType(parts[0]);
          if (parts.length == 2) {
            sentryException.setValue(parts[1]);
          }

          sentryExceptions.add(sentryException);
        }
      }
    }

    return sentryExceptions;
  }

  public static List<SentryException> buildJavaSentryExceptions(final String stacktrace) {
    // TODO
    return null;
  }
}
