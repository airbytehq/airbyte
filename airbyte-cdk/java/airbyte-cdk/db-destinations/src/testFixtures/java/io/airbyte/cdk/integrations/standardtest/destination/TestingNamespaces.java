/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.standardtest.destination;

import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.time.temporal.ChronoUnit;
import java.util.Optional;
import org.apache.commons.lang3.RandomStringUtils;

/**
 * This class is used to generate unique namespaces for tests that follow a convention so that we
 * can identify and delete old namespaces. Ideally tests would always clean up their own namespaces,
 * but there are exception cases that can prevent that from happening. We want to be able to
 * identify namespaces for which this has happened from their name, so we can take action.
 * <p>
 * The convention we follow is `<test-provided prefix>_test_YYYYMMDD_<8-character random suffix>`.
 */
public class TestingNamespaces {

  private static final DateTimeFormatter FORMATTER = DateTimeFormatter.ofPattern("yyyyMMdd");
  private static final int SUFFIX_LENGTH = 5;
  public static final String STANDARD_PREFIX = "test_";

  /**
   * Generates a namespace that matches our testing namespace convention.
   *
   * @return convention-compliant namespace
   */
  public static String generate() {
    return generate(null);
  }

  /**
   * Generates a namespace that matches our testing namespace convention.
   *
   * @param prefix prefix to use for the namespace
   * @return convention-compliant namespace
   */
  public static String generate(final String prefix) {
    final String userDefinedPrefix = prefix != null ? prefix + "_" : "";
    return userDefinedPrefix + STANDARD_PREFIX + FORMATTER.format(Instant.now().atZone(ZoneId.of("UTC"))) + "_" + generateSuffix();
  }

  public static String generateFromOriginal(final String toOverwrite, final String oldPrefix, final String newPrefix) {
    return toOverwrite.replace(oldPrefix, newPrefix);
  }

  /**
   * Checks if a namespace is older than 2 days.
   *
   * @param namespace to check
   * @return true if the namespace is older than 2 days, otherwise false
   */
  public static boolean isOlderThan2Days(final String namespace) {
    return isOlderThan(namespace, 2, ChronoUnit.DAYS);
  }

  @SuppressWarnings("SameParameterValue")
  private static boolean isOlderThan(final String namespace, final int timeMagnitude, final ChronoUnit timeUnit) {
    return ifTestNamespaceGetDate(namespace)
        .map(namespaceInstant -> namespaceInstant.isBefore(Instant.now().minus(timeMagnitude, timeUnit)))
        .orElse(false);
  }

  private static Optional<Instant> ifTestNamespaceGetDate(final String namespace) {
    final String[] parts = namespace.split("_");

    if (parts.length < 3) {
      return Optional.empty();
    }

    // need to re-add the _ since it gets pruned out by the split.
    if (!STANDARD_PREFIX.equals(parts[parts.length - 3] + "_")) {
      return Optional.empty();
    }

    return parseDateOrEmpty(parts[parts.length - 2]);
  }

  private static Optional<Instant> parseDateOrEmpty(final String dateCandidate) {
    try {
      return Optional.ofNullable(LocalDate.parse(dateCandidate, FORMATTER).atStartOfDay().toInstant(ZoneOffset.UTC));
    } catch (final DateTimeParseException e) {
      return Optional.empty();
    }
  }

  private static String generateSuffix() {
    return RandomStringUtils.randomAlphabetic(SUFFIX_LENGTH).toLowerCase();
  }

}
