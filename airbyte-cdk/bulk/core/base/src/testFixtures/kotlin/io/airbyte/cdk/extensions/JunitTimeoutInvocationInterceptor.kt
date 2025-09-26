/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.extensions

import java.lang.reflect.Method
import java.time.Duration
import java.time.format.DateTimeParseException
import java.util.Collections
import java.util.HashMap
import java.util.concurrent.TimeUnit
import java.util.regex.Pattern
import org.junit.jupiter.api.Assertions.assertTimeoutPreemptively
import org.junit.jupiter.api.extension.ExtensionContext
import org.junit.jupiter.api.extension.InvocationInterceptor
import org.junit.jupiter.api.extension.ReflectiveInvocationContext

class JunitTimeoutInvocationInterceptor : InvocationInterceptor {
    @Throws(Throwable::class)
    override fun interceptTestMethod(
        invocation: InvocationInterceptor.Invocation<Void>,
        context: ReflectiveInvocationContext<Method>,
        extensionContext: ExtensionContext
    ) {
        assertTimeoutPreemptively<Void>(
            getTimeout(),
        ) {
            invocation.proceed()
        }
    }

    companion object {
        private const val JUNIT_METHOD_EXECUTION_TIMEOUT_PROPERTY_NAME =
            "JunitMethodExecutionTimeout"

        private val PATTERN: Pattern =
            Pattern.compile(
                "([1-9]\\d*) *((?:[nμm]?s)|m|h|d)?",
                Pattern.CASE_INSENSITIVE or Pattern.UNICODE_CASE
            )
        private val UNITS_BY_ABBREVIATION: MutableMap<String, TimeUnit>

        init {
            val unitsByAbbreviation: MutableMap<String, TimeUnit> = HashMap()
            unitsByAbbreviation["ns"] = TimeUnit.NANOSECONDS
            unitsByAbbreviation["μs"] = TimeUnit.MICROSECONDS
            unitsByAbbreviation["ms"] = TimeUnit.MILLISECONDS
            unitsByAbbreviation["s"] = TimeUnit.SECONDS
            unitsByAbbreviation["m"] = TimeUnit.MINUTES
            unitsByAbbreviation["h"] = TimeUnit.HOURS
            unitsByAbbreviation["d"] = TimeUnit.DAYS
            UNITS_BY_ABBREVIATION = Collections.unmodifiableMap(unitsByAbbreviation)
        }

        @Throws(DateTimeParseException::class)
        fun parseDuration(text: String): Duration {
            val matcher = PATTERN.matcher(text.trim { it <= ' ' })
            if (matcher.matches()) {
                val value = matcher.group(1).toLong()
                val unitAbbreviation = matcher.group(2)
                val unit =
                    if (unitAbbreviation == null) TimeUnit.SECONDS
                    else UNITS_BY_ABBREVIATION.getValue(unitAbbreviation.lowercase())
                return Duration.ofSeconds(unit.toSeconds(value))
            }
            throw DateTimeParseException(
                "Timeout duration is not in the expected format (<number> [ns|μs|ms|s|m|h|d])",
                text,
                0
            )
        }

        private fun getTimeout(): Duration =
            parseDuration(System.getProperty(JUNIT_METHOD_EXECUTION_TIMEOUT_PROPERTY_NAME))
    }
}
