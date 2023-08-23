/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.destination;

import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import org.apache.commons.lang3.RandomStringUtils;

/**
 * This class is used to generate unique namespaces for tests that follow a convention so that we
 * can identify and delete old namespaces. Ideally tests would always clean up their own namespaces,
 * but there are exception cases that can prevent that from happening. We want to be able to
 * identify namespaces for which this has happened from their name so we can take action.
 * <p>
 * The convention we follow is `<test-provided prefix>_YYYYMMDD_<8-character random suffix>`.
 */
public class TestingNamespaces {

  private static final DateTimeFormatter FORMATTER = DateTimeFormatter.ofPattern("yyyyMMdd");
  private static final int SUFFIX_LENGTH = 5;

  /**
   * Generates a namespace that matches our testing namespace convention.
   *
   * @return convention-compliant namespace
   */
  public static String generate() {
    return generate("test_namespace");
  }

  /**
   * Generates a namespace that matches our testing namespace convention.
   *
   * @param prefix prefix to use for the namespace
   * @return convention-compliant namespace
   */
  public static String generate(final String prefix) {
    return prefix + "_" + FORMATTER.format(Instant.now().atZone(ZoneId.of("UTC"))) + "_" + generateSuffix();
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
    final String[] parts = namespace.split("_");
    final Instant namespaceInstant = LocalDate.parse(parts[parts.length - 2], FORMATTER).atStartOfDay().toInstant(ZoneOffset.UTC);
    final Instant now = Instant.now();
    return namespaceInstant.isBefore(now.minus(timeMagnitude, timeUnit));
  }

  private static String generateSuffix() {
    return RandomStringUtils.randomAlphabetic(SUFFIX_LENGTH).toLowerCase();
  }

}
