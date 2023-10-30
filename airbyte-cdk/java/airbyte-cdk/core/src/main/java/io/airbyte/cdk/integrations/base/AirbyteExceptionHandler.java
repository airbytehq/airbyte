/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.base;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.apache.commons.io.filefilter.SuffixFileFilter;
import org.jetbrains.annotations.NotNull;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AirbyteExceptionHandler implements Thread.UncaughtExceptionHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteExceptionHandler.class);
  public static final String logMessage = "Something went wrong in the connector. See the logs for more details.";

  // Basic deinterpolation helpers to avoid doing _really_ dumb deinterpolation.
  // E.g. if "id" is in the list of strings to remove, we don't want to modify the message "Invalid identifier".
  private static final String REGEX_PREFIX = "(^|[^A-Za-z0-9_])";
  private static final String REGEX_SUFFIX = "($|[^A-Za-z0-9_])";

  /**
   * If this list is populated, then the exception handler will attempt to deinterpolate the error
   * message before emitting a trace message. This is useful for connectors which (a) emit a single
   * exception class, and (b) rely on that exception's message to distinguish between error types.
   * <p>
   * If this is active, then the trace message will:
   * <ol>
   *   <li>Not contain the stacktrace at all. This causes Sentry to use its fallback grouping
   *   (using exception class and message)</li>
   *   <li>Contain the original exception message as the external message, and a mangled message
   *   as the internal message.</li>
   * </ol>
   */
  public static final List<String> STRINGS_TO_REMOVE = new ArrayList<>();

  @Override
  public void uncaughtException(final Thread thread, final Throwable throwable) {
    // This is a naive AirbyteTraceMessage emission in order to emit one when any error occurs in a
    // connector.
    // If a connector implements AirbyteTraceMessage emission itself, this code will result in an
    // additional one being emitted.
    // this is fine tho because:
    // "The earliest AirbyteTraceMessage where type=error will be used to populate the FailureReason for
    // the sync."
    // from the spec:
    // https://docs.google.com/document/d/1ctrj3Yh_GjtQ93aND-WH3ocqGxsmxyC3jfiarrF6NY0/edit#
    LOGGER.error(logMessage, throwable);

    // Attempt to deinterpolate the error message before emitting a trace message
    final String mangledMessage = STRINGS_TO_REMOVE.stream().reduce(
        throwable.getMessage(),
        AirbyteExceptionHandler::deinterpolate);
    if (mangledMessage.equals(throwable.getMessage())) {
      // If deinterpolating did not modify the message, then emit our default trace message
      AirbyteTraceMessageUtility.emitSystemErrorTrace(throwable, logMessage);
    } else {
      AirbyteTraceMessageUtility.emitCustomErrorTrace(throwable.getMessage(), mangledMessage);
    }

    terminate();
  }

  @NotNull
  private static String deinterpolate(final String message, final String targetString) {
    final String quotedTarget = '(' + Pattern.quote(targetString) + ')';
    final String targetRegex = REGEX_PREFIX + quotedTarget + REGEX_SUFFIX;
    final Pattern pattern = Pattern.compile(targetRegex);
    final Matcher matcher = pattern.matcher(message);

    // The pattern has three capturing groups:
    // 1. The character before the target string (or an empty string, if it matched start-of-string)
    // 2. The target string
    // 3. The character after the target string (or empty string for end-of-string)
    // We want to preserve the characters before and after the target string, so we use $1 and $3 to reinsert them
    // but the target string is replaced with just '?'
    return matcher.replaceAll("$1?$3");
  }

  public static void addAllStringsInConfig(final JsonNode node) {
    if (node.isTextual()) {
      STRINGS_TO_REMOVE.add(node.asText());
    } else if (node.isContainerNode()) {
      for (final JsonNode subNode : node) {
        addAllStringsInConfig(subNode);
      }
    }
  }

  // by doing this in a separate method we can mock it to avoid closing the jvm and therefore test
  // properly
  protected void terminate() {
    System.exit(1);
  }

}
