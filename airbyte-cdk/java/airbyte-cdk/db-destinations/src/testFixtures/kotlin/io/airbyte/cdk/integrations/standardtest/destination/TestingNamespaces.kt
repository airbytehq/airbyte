/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.destination

import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeParseException
import java.time.temporal.ChronoUnit
import java.util.*
import org.apache.commons.lang3.RandomStringUtils

/**
 * This class is used to generate unique namespaces for tests that follow a convention so that we
 * can identify and delete old namespaces. Ideally tests would always clean up their own namespaces,
 * but there are exception cases that can prevent that from happening. We want to be able to
 * identify namespaces for which this has happened from their name, so we can take action.
 *
 * The convention we follow is `<test-provided prefix>_test_YYYYMMDD_<8-character random suffix>`.
 * </test-provided>
 */
object TestingNamespaces {
    private val FORMATTER: DateTimeFormatter = DateTimeFormatter.ofPattern("yyyyMMdd")
    private const val SUFFIX_LENGTH = 5
    const val STANDARD_PREFIX: String = "test_"

    /**
     * Generates a namespace that matches our testing namespace convention.
     *
     * @param prefix prefix to use for the namespace
     * @return convention-compliant namespace
     */
    /**
     * Generates a namespace that matches our testing namespace convention.
     *
     * @return convention-compliant namespace
     */
    @JvmStatic
    @JvmOverloads
    fun generate(prefix: String? = null): String {
        val userDefinedPrefix = if (prefix != null) prefix + "_" else ""
        return userDefinedPrefix +
            STANDARD_PREFIX +
            FORMATTER.format(Instant.now().atZone(ZoneId.of("UTC"))) +
            "_" +
            generateSuffix()
    }

    fun generateFromOriginal(toOverwrite: String, oldPrefix: String, newPrefix: String): String {
        return toOverwrite.replace(oldPrefix, newPrefix)
    }

    /**
     * Checks if a namespace is older than 2 days.
     *
     * @param namespace to check
     * @return true if the namespace is older than 2 days, otherwise false
     */
    @JvmStatic
    fun isOlderThan2Days(namespace: String): Boolean {
        return isOlderThan(namespace, 2, ChronoUnit.DAYS)
    }

    private fun isOlderThan(namespace: String, timeMagnitude: Int, timeUnit: ChronoUnit): Boolean {
        return ifTestNamespaceGetDate(namespace)
            .map { namespaceInstant: Instant ->
                namespaceInstant.isBefore(Instant.now().minus(timeMagnitude.toLong(), timeUnit))
            }
            .orElse(false)
    }

    private fun ifTestNamespaceGetDate(namespace: String): Optional<Instant> {
        val parts = namespace.split("_".toRegex()).dropLastWhile { it.isEmpty() }.toTypedArray()

        if (parts.size < 3) {
            return Optional.empty()
        }

        // need to re-add the _ since it gets pruned out by the split.
        if (STANDARD_PREFIX != parts[parts.size - 3] + "_") {
            return Optional.empty()
        }

        return parseDateOrEmpty(parts[parts.size - 2])
    }

    private fun parseDateOrEmpty(dateCandidate: String): Optional<Instant> {
        return try {
            Optional.ofNullable(
                LocalDate.parse(dateCandidate, FORMATTER).atStartOfDay().toInstant(ZoneOffset.UTC)
            )
        } catch (e: DateTimeParseException) {
            Optional.empty()
        }
    }

    private fun generateSuffix(): String {
        return RandomStringUtils.randomAlphabetic(SUFFIX_LENGTH).lowercase(Locale.getDefault())
    }
}
