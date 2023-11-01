/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.base;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.apache.commons.lang3.exception.ExceptionUtils;
import org.jetbrains.annotations.NotNull;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AirbyteExceptionHandler implements Thread.UncaughtExceptionHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteExceptionHandler.class);
  public static final String logMessage = "Something went wrong in the connector. See the logs for more details.";

  // Basic deinterpolation helpers to avoid doing _really_ dumb deinterpolation.
  // E.g. if "id" is in the list of strings to remove, we don't want to modify the message "Invalid
  // identifier".
  private static final String REGEX_PREFIX = "(^|\\W)";
  private static final String REGEX_SUFFIX = "($|\\W)";

  /**
   * If this list is populated, then the exception handler will attempt to deinterpolate the error
   * message before emitting a trace message. This is useful for connectors which (a) emit a single
   * exception class, and (b) rely on that exception's message to distinguish between error types.
   * <p>
   * If this is active, then the trace message will:
   * <ol>
   * <li>Not contain the stacktrace at all. This causes Sentry to use its fallback grouping (using
   * exception class and message)</li>
   * <li>Contain the original exception message as the external message, and a mangled message as the
   * internal message.</li>
   * </ol>
   */
  @VisibleForTesting
  static final List<String> STRINGS_TO_DEINTERPOLATE = new ArrayList<>();
  @VisibleForTesting
  static final Set<Class<? extends Throwable>> THROWABLES_TO_DEINTERPOLATE = new HashSet<>();

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
    final String mangledMessage;
    // If any exception in the chain is of a deinterpolatable type, find it and deinterpolate its
    // message.
    // This assumes that any wrapping exceptions are just noise (e.g. runtime exception).
    final Optional<Throwable> deinterpolatableException = ExceptionUtils.getThrowableList(throwable).stream()
        .filter(t -> THROWABLES_TO_DEINTERPOLATE.stream().anyMatch(deinterpolatableClass -> deinterpolatableClass.isAssignableFrom(t.getClass())))
        .findFirst();
    if (deinterpolatableException.isPresent()) {
      mangledMessage = STRINGS_TO_DEINTERPOLATE.stream()
          // Sort the strings longest to shortest, in case any target string is a substring of another
          // e.g. "airbyte_internal" should be swapped out before "airbyte"
          .sorted(Comparator.comparing(String::length).reversed())
          .reduce(deinterpolatableException.get().getMessage(), AirbyteExceptionHandler::deinterpolate);
    } else {
      mangledMessage = throwable.getMessage();
    }

    // If we did not modify the message (either not a deinterpolatable class, or we tried to
    // deinterpolate
    // but made no changes) then emit our default trace message
    if (mangledMessage.equals(throwable.getMessage())) {
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
    // We want to preserve the characters before and after the target string, so we use $1 and $3 to
    // reinsert them
    // but the target string is replaced with just '?'
    return matcher.replaceAll("$1?$3");
  }

  public static void addThrowableForDeinterpolation(final Class<? extends Throwable> klass) {
    THROWABLES_TO_DEINTERPOLATE.add(klass);
  }

  public static void addStringForDeinterpolation(final String string) {
    STRINGS_TO_DEINTERPOLATE.add(string);
  }

  public static void addAllStringsInConfigForDeinterpolation(final JsonNode node) {
    if (node.isTextual()) {
      addStringForDeinterpolation(node.asText());
    } else if (node.isContainerNode()) {
      for (final JsonNode subNode : node) {
        addAllStringsInConfigForDeinterpolation(subNode);
      }
    }
  }

  // by doing this in a separate method we can mock it to avoid closing the jvm and therefore test
  // properly
  protected void terminate() {
    System.exit(1);
  }

}
