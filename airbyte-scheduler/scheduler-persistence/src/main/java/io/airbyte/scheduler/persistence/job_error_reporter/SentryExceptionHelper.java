/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_error_reporter;

import io.airbyte.commons.lang.Exceptions;
import io.sentry.protocol.SentryException;
import io.sentry.protocol.SentryStackFrame;
import io.sentry.protocol.SentryStackTrace;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class SentryExceptionHelper {

  /**
   * Processes a raw stacktrace string into structured SentryExceptions
   * <p>
   * Currently, Java and Python stacktraces are supported. If an unsupported stacktrace format is
   * encountered, an empty optional will be returned, in which case we can fall back to alternate
   * grouping.
   */
  public Optional<List<SentryException>> buildSentryExceptions(final String stacktrace) {
    return Exceptions.swallowWithDefault(() -> {
      if (stacktrace.startsWith("Traceback (most recent call last):")) {
        return buildPythonSentryExceptions(stacktrace);
      }
      if (stacktrace.contains("\tat ") && stacktrace.contains(".java")) {
        return buildJavaSentryExceptions(stacktrace);
      }

      return Optional.empty();
    }, Optional.empty());
  }

  private static Optional<List<SentryException>> buildPythonSentryExceptions(final String stacktrace) {
    final List<SentryException> sentryExceptions = new ArrayList<>();

    // separate chained exceptions
    // e.g "\n\nThe above exception was the direct cause of the following exception:\n\n"
    // "\n\nDuring handling of the above exception, another exception occurred:\n\n"
    final String exceptionSeparator = "\n\n[\\w ,]+:\n\n";
    final String[] exceptions = stacktrace.split(exceptionSeparator);

    for (final String exceptionStr : exceptions) {
      final SentryStackTrace stackTrace = new SentryStackTrace();
      final List<SentryStackFrame> stackFrames = new ArrayList<>();

      // Use a regex to grab stack trace frame information
      final Pattern framePattern = Pattern.compile("File \"(?<absPath>.+)\", line (?<lineno>\\d+), in (?<function>.+)\\n {4}(?<contextLine>.+)\\n");
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

        // The final part of our stack trace has the exception type and (optionally) a value
        // (e.g. "RuntimeError: This is the value")
        final String remaining = exceptionStr.substring(lastMatchIdx);
        final String[] parts = remaining.split(":", 2);

        if (parts.length > 0) {
          sentryException.setType(parts[0].trim());
          if (parts.length == 2) {
            sentryException.setValue(parts[1].trim());
          }

          sentryExceptions.add(sentryException);
        }
      }
    }

    if (sentryExceptions.size() == 0)
      return Optional.empty();

    return Optional.of(sentryExceptions);
  }

  private static Optional<List<SentryException>> buildJavaSentryExceptions(final String stacktrace) {
    final List<SentryException> sentryExceptions = new ArrayList<>();

    // separate chained exceptions
    // e.g "\nCaused By: "
    final String exceptionSeparator = "\n[\\w ]+: ";
    final String[] exceptions = stacktrace.split(exceptionSeparator);

    for (final String exceptionStr : exceptions) {
      final SentryStackTrace stackTrace = new SentryStackTrace();
      final List<SentryStackFrame> stackFrames = new ArrayList<>();

      // Use a regex to grab stack trace frame information
      final Pattern framePattern = Pattern.compile(
          "\n\tat (?:[\\w.$/]+/)?(?<module>[\\w$.]+)\\.(?<function>[\\w<>$]+)\\((?:(?<filename>[\\w]+\\.java):(?<lineno>\\d+)\\)|(?<desc>[\\w\\s]*))");
      final Matcher matcher = framePattern.matcher(exceptionStr);

      while (matcher.find()) {
        final String module = matcher.group("module");
        final String filename = matcher.group("filename");
        final String lineno = matcher.group("lineno");
        final String function = matcher.group("function");
        final String sourceDescription = matcher.group("desc");

        final SentryStackFrame stackFrame = new SentryStackFrame();
        stackFrame.setModule(module);
        stackFrame.setFunction(function);
        stackFrame.setFilename(filename);

        if (lineno != null) {
          stackFrame.setLineno(Integer.valueOf(lineno));
        }
        if (sourceDescription != null && sourceDescription.equals("Native Method")) {
          stackFrame.setNative(true);
        }

        stackFrames.add(stackFrame);
      }

      if (stackFrames.size() > 0) {
        Collections.reverse(stackFrames);
        stackTrace.setFrames(stackFrames);

        final SentryException sentryException = new SentryException();
        sentryException.setStacktrace(stackTrace);

        // The first section of our stacktrace before the first frame has exception type and value
        final String[] sections = exceptionStr.split("\n\tat ", 2);
        final String[] headerParts = sections[0].split(": ", 2);

        if (headerParts.length > 0) {
          sentryException.setType(headerParts[0].trim());
          if (headerParts.length == 2) {
            sentryException.setValue(headerParts[1].trim());
          }

          sentryExceptions.add(sentryException);
        }
      }
    }

    if (sentryExceptions.size() == 0)
      return Optional.empty();

    return Optional.of(sentryExceptions);
  }

}
