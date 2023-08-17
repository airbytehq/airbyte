/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.normalization;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This is copied out of platform
 * (https://github.com/airbytehq/airbyte-platform/blob/main/airbyte-persistence/job-persistence/src/main/java/io/airbyte/persistence/job/errorreporter/SentryExceptionHelper.java#L257)
 */
public class SentryExceptionHelper {

  private static final Logger LOGGER = LoggerFactory.getLogger(SentryExceptionHelper.class);

  /**
   * Keys to known error types.
   */
  public enum ErrorMapKeys {
    ERROR_MAP_MESSAGE_KEY,
    ERROR_MAP_TYPE_KEY
  }

  public static Map<ErrorMapKeys, String> getUsefulErrorMessageAndTypeFromDbtError(final String stacktrace) {
    // the dbt 'stacktrace' is really just all the log messages at 'error' level, stuck together.
    // therefore there is not a totally consistent structure to these,
    // see the docs: https://docs.getdbt.com/guides/legacy/debugging-errors
    // the logic below is built based on the ~450 unique dbt errors we encountered before this PR
    // and is a best effort to isolate the useful part of the error logs for debugging and grouping
    // and bring some semblance of exception 'types' to differentiate between errors.
    final Map<ErrorMapKeys, String> errorMessageAndType = new HashMap<>();
    final String[] stacktraceLines = stacktrace.split("\n");

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
            errorMessageAndType.put(ErrorMapKeys.ERROR_MAP_MESSAGE_KEY,
                String.format("%s %s", stacktraceLines[i + 1].trim(), stacktraceLines[i + 2].trim()));
            errorMessageAndType.put(ErrorMapKeys.ERROR_MAP_TYPE_KEY, "DbtDatabaseSQLCompilationError");
            break;
            // Database Error: Invalid input
          } else if (stacktraceLines[i + 1].contains("Invalid input")) {
            for (final String followingLine : Arrays.copyOfRange(stacktraceLines, i + 1, stacktraceLines.length)) {
              if (followingLine.trim().startsWith("context:")) {
                errorMessageAndType.put(ErrorMapKeys.ERROR_MAP_MESSAGE_KEY,
                    String.format("%s\n%s", stacktraceLines[i + 1].trim(), followingLine.trim()));
                errorMessageAndType.put(ErrorMapKeys.ERROR_MAP_TYPE_KEY, "DbtDatabaseInvalidInputError");
                break mainLoop;
              }
            }
            // Database Error: Syntax error
          } else if (stacktraceLines[i + 1].contains("syntax error at or near \"")) {
            errorMessageAndType.put(ErrorMapKeys.ERROR_MAP_MESSAGE_KEY,
                String.format("%s\n%s", stacktraceLines[i + 1].trim(), stacktraceLines[i + 2].trim()));
            errorMessageAndType.put(ErrorMapKeys.ERROR_MAP_TYPE_KEY, "DbtDatabaseSyntaxError");
            break;
            // Database Error: default
          } else {
            errorMessageAndType.put(ErrorMapKeys.ERROR_MAP_TYPE_KEY, "DbtDatabaseError");
            defaultNextLine = true;
          }
          // Unhandled Error
        } else if (stacktraceLines[i].contains("Unhandled error while executing model")) {
          errorMessageAndType.put(ErrorMapKeys.ERROR_MAP_TYPE_KEY, "DbtUnhandledError");
          defaultNextLine = true;
          // Compilation Errors
        } else if (stacktraceLines[i].contains("Compilation Error")) {
          // Compilation Error: Ambiguous Relation
          if (stacktraceLines[i + 1].contains("When searching for a relation, dbt found an approximate match.")) {
            errorMessageAndType.put(ErrorMapKeys.ERROR_MAP_MESSAGE_KEY,
                String.format("%s %s", stacktraceLines[i + 1].trim(), stacktraceLines[i + 2].trim()));
            errorMessageAndType.put(ErrorMapKeys.ERROR_MAP_TYPE_KEY, "DbtCompilationAmbiguousRelationError");
            break;
            // Compilation Error: default
          } else {
            errorMessageAndType.put(ErrorMapKeys.ERROR_MAP_TYPE_KEY, "DbtCompilationError");
            defaultNextLine = true;
          }
          // Runtime Errors
        } else if (stacktraceLines[i].contains("Runtime Error")) {
          // Runtime Error: Database error
          for (final String followingLine : Arrays.copyOfRange(stacktraceLines, i + 1, stacktraceLines.length)) {
            if ("Database Error".equals(followingLine.trim())) {
              errorMessageAndType.put(ErrorMapKeys.ERROR_MAP_MESSAGE_KEY,
                  String.format("%s", stacktraceLines[Arrays.stream(stacktraceLines).toList().indexOf(followingLine) + 1].trim()));
              errorMessageAndType.put(ErrorMapKeys.ERROR_MAP_TYPE_KEY, "DbtRuntimeDatabaseError");
              break mainLoop;
            }
          }
          // Runtime Error: default
          errorMessageAndType.put(ErrorMapKeys.ERROR_MAP_TYPE_KEY, "DbtRuntimeError");
          defaultNextLine = true;
          // Database Error: formatted differently, catch last to avoid counting other types of errors as
          // Database Error
        } else if ("Database Error".equals(stacktraceLines[i].trim())) {
          errorMessageAndType.put(ErrorMapKeys.ERROR_MAP_TYPE_KEY, "DbtDatabaseError");
          defaultNextLine = true;
        }
        // handle the default case without repeating code
        if (defaultNextLine) {
          errorMessageAndType.put(ErrorMapKeys.ERROR_MAP_MESSAGE_KEY, stacktraceLines[i + 1].trim());
          break;
        }
      } catch (final ArrayIndexOutOfBoundsException e) {
        // this means our logic is slightly off, our assumption of where error lines are is incorrect
        LOGGER.warn("Failed trying to parse useful error message out of dbt error, defaulting to full stacktrace");
      }
    }
    if (errorMessageAndType.isEmpty()) {
      // For anything we haven't caught, just return full stacktrace
      errorMessageAndType.put(ErrorMapKeys.ERROR_MAP_MESSAGE_KEY, stacktrace);
      errorMessageAndType.put(ErrorMapKeys.ERROR_MAP_TYPE_KEY, "AirbyteDbtError");
    }
    return errorMessageAndType;
  }

}
