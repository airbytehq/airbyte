/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_error_reporter;

import io.airbyte.commons.lang.Exceptions;
import io.sentry.protocol.SentryException;
import io.sentry.protocol.SentryStackFrame;
import io.sentry.protocol.SentryStackTrace;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SentryExceptionHelper {

  private static final Logger LOGGER = LoggerFactory.getLogger(SentryExceptionHelper.class);

  public static final String ERROR_MAP_MESSAGE_KEY = "errorMessage";
  public static final String ERROR_MAP_TYPE_KEY = "errorType";

  public enum ERROR_MAP_KEYS {
    ERROR_MAP_MESSAGE_KEY,
    ERROR_MAP_TYPE_KEY
  }

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
      if (stacktrace.startsWith("AirbyteDbtError: ")) {
        return buildNormalizationDbtSentryExceptions(stacktrace);
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

      if (!stackFrames.isEmpty()) {
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

    if (sentryExceptions.isEmpty())
      return Optional.empty();

    return Optional.of(sentryExceptions);
  }

  private static Optional<List<SentryException>> buildJavaSentryExceptions(final String stacktrace) {
    final List<SentryException> sentryExceptions = new ArrayList<>();

    // separate chained exceptions
    // e.g "\nCaused by: "
    final String exceptionSeparator = "\nCaused by: ";
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

      if (!stackFrames.isEmpty()) {
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

    if (sentryExceptions.isEmpty())
      return Optional.empty();

    return Optional.of(sentryExceptions);
  }

  private static Optional<List<SentryException>> buildNormalizationDbtSentryExceptions(final String stacktrace) {
    final List<SentryException> sentryExceptions = new ArrayList<>();

    Map<ERROR_MAP_KEYS, String> usefulErrorMap = getUsefulErrorMessageAndTypeFromDbtError(stacktrace);

    // if our errorMessage from the function != stacktrace then we know we've pulled out something
    // useful
    if (!usefulErrorMap.get(ERROR_MAP_KEYS.ERROR_MAP_MESSAGE_KEY).equals(stacktrace)) {
      final SentryException usefulException = new SentryException();
      usefulException.setValue(usefulErrorMap.get(ERROR_MAP_KEYS.ERROR_MAP_MESSAGE_KEY));
      usefulException.setType(usefulErrorMap.get(ERROR_MAP_KEYS.ERROR_MAP_TYPE_KEY));
      sentryExceptions.add(usefulException);
    }

    if (sentryExceptions.isEmpty())
      return Optional.empty();

    return Optional.of(sentryExceptions);
  }

  public static Map<ERROR_MAP_KEYS, String> getUsefulErrorMessageAndTypeFromDbtError(String stacktrace) {
    // the dbt 'stacktrace' is really just all the log messages at 'error' level, stuck together.
    // therefore there is not a totally consistent structure to these,
    // see the docs: https://docs.getdbt.com/guides/legacy/debugging-errors
    // the logic below is built based on the ~450 unique dbt errors we encountered before this PR
    // and is a best effort to isolate the useful part of the error logs for debugging and grouping
    // and bring some semblance of exception 'types' to differentiate between errors.
    Map<ERROR_MAP_KEYS, String> errorMessageAndType = new HashMap<>();
    String[] stacktraceLines = stacktrace.split("\n");

    boolean defaultNextLine = false;
    // TODO: this whole code block is quite ugh, commented to try and make each part clear but could be
    // much more readable.
    mainLoop: for (int i = 0; i < stacktraceLines.length; i++) {
      // This order is important due to how these errors can co-occur.
      // This order attempts to keep error definitions consistent based on our observations of possible
      // dbt error structures.
      try {
        // Database Errors
        if (stacktraceLines[i].contains("Database Error in model")) {
          // Database Error : SQL compilation error
          if (stacktraceLines[i + 1].contains("SQL compilation error")) {
            errorMessageAndType.put(ERROR_MAP_KEYS.ERROR_MAP_MESSAGE_KEY,
                String.format("%s %s", stacktraceLines[i + 1].trim(), stacktraceLines[i + 2].trim()));
            errorMessageAndType.put(ERROR_MAP_KEYS.ERROR_MAP_TYPE_KEY, "DbtDatabaseSQLCompilationError");
            break;
          }
          // Database Error: Invalid input
          else if (stacktraceLines[i + 1].contains("Invalid input")) {
            for (String followingLine : Arrays.copyOfRange(stacktraceLines, i + 1, stacktraceLines.length)) {
              if (followingLine.trim().startsWith("context:")) {
                errorMessageAndType.put(ERROR_MAP_KEYS.ERROR_MAP_MESSAGE_KEY,
                    String.format("%s\n%s", stacktraceLines[i + 1].trim(), followingLine.trim()));
                errorMessageAndType.put(ERROR_MAP_KEYS.ERROR_MAP_TYPE_KEY, "DbtDatabaseInvalidInputError");
                break mainLoop;
              }
            }
          }
          // Database Error: Syntax error
          else if (stacktraceLines[i + 1].contains("syntax error at or near \"")) {
            errorMessageAndType.put(ERROR_MAP_KEYS.ERROR_MAP_MESSAGE_KEY,
                String.format("%s\n%s", stacktraceLines[i + 1].trim(), stacktraceLines[i + 2].trim()));
            errorMessageAndType.put(ERROR_MAP_KEYS.ERROR_MAP_TYPE_KEY, "DbtDatabaseSyntaxError");
            break;
          }
          // Database Error: default
          else {
            errorMessageAndType.put(ERROR_MAP_KEYS.ERROR_MAP_TYPE_KEY, "DbtDatabaseError");
            defaultNextLine = true;
          }
        }
        // Unhandled Error
        else if (stacktraceLines[i].contains("Unhandled error while executing model")) {
          errorMessageAndType.put(ERROR_MAP_KEYS.ERROR_MAP_TYPE_KEY, "DbtUnhandledError");
          defaultNextLine = true;
        }
        // Compilation Errors
        else if (stacktraceLines[i].contains("Compilation Error")) {
          // Compilation Error: Ambiguous Relation
          if (stacktraceLines[i + 1].contains("When searching for a relation, dbt found an approximate match.")) {
            errorMessageAndType.put(ERROR_MAP_KEYS.ERROR_MAP_MESSAGE_KEY,
                String.format("%s %s", stacktraceLines[i + 1].trim(), stacktraceLines[i + 2].trim()));
            errorMessageAndType.put(ERROR_MAP_KEYS.ERROR_MAP_TYPE_KEY, "DbtCompilationAmbiguousRelationError");
            break;
          }
          // Compilation Error: default
          else {
            errorMessageAndType.put(ERROR_MAP_KEYS.ERROR_MAP_TYPE_KEY, "DbtCompilationError");
            defaultNextLine = true;
          }
        }
        // Runtime Errors
        else if (stacktraceLines[i].contains("Runtime Error")) {
          // Runtime Error: Database error
          for (String followingLine : Arrays.copyOfRange(stacktraceLines, i + 1, stacktraceLines.length)) {
            if ("Database Error".equals(followingLine.trim())) {
              errorMessageAndType.put(ERROR_MAP_KEYS.ERROR_MAP_MESSAGE_KEY,
                  String.format("%s", stacktraceLines[Arrays.stream(stacktraceLines).toList().indexOf(followingLine) + 1].trim()));
              errorMessageAndType.put(ERROR_MAP_KEYS.ERROR_MAP_TYPE_KEY, "DbtRuntimeDatabaseError");
              break mainLoop;
            }
          }
          // Runtime Error: default
          errorMessageAndType.put(ERROR_MAP_KEYS.ERROR_MAP_TYPE_KEY, "DbtRuntimeError");
          defaultNextLine = true;
        }
        // Database Error: formatted differently, catch last to avoid counting other types of errors as
        // Database Error
        else if ("Database Error".equals(stacktraceLines[i].trim())) {
          errorMessageAndType.put(ERROR_MAP_KEYS.ERROR_MAP_TYPE_KEY, "DbtDatabaseError");
          defaultNextLine = true;
        }
        // handle the default case without repeating code
        if (defaultNextLine) {
          errorMessageAndType.put(ERROR_MAP_KEYS.ERROR_MAP_MESSAGE_KEY, stacktraceLines[i + 1].trim());
          break;
        }
      } catch (final ArrayIndexOutOfBoundsException e) {
        // this means our logic is slightly off, our assumption of where error lines are is incorrect
        LOGGER.warn("Failed trying to parse useful error message out of dbt error, defaulting to full stacktrace");
      }
    }
    if (errorMessageAndType.isEmpty()) {
      // For anything we haven't caught, just return full stacktrace
      errorMessageAndType.put(ERROR_MAP_KEYS.ERROR_MAP_MESSAGE_KEY, stacktrace);
      errorMessageAndType.put(ERROR_MAP_KEYS.ERROR_MAP_TYPE_KEY, "AirbyteDbtError");
    }
    return errorMessageAndType;
  }

}
