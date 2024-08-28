/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.output

import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
import io.micronaut.core.order.Ordered

interface ExceptionClassifier : Ordered {

    /** Classifies [e] into a [ConnectorError] if possible, null otherwise. */
    fun classify(e: Throwable): ConnectorError?

    /** Convenience val for [getOrder]. */
    val orderValue: Int

    override fun getOrder(): Int = orderValue
}

/** Each [ConnectorError] subtype corresponds to a [AirbyteErrorTraceMessage.FailureType]. */
sealed interface ConnectorError

/**
 * A [ConfigError] means there is something wrong with the user's connector configuration or any
 * other error for which the connector informs the platform that the error is not transient in
 * nature and thus to not bother retrying.
 */
data class ConfigError(val displayMessage: String) : ConnectorError

/**
 * A [TransientError] means there is something wrong with the user's source or any other error for
 * which the connector informs the platform that the error is transient in nature.
 */
data class TransientError(val displayMessage: String) : ConnectorError

/**
 * A [SystemError] means there is something wrong with the connector.
 *
 * In practice these are also ll errors that are neither [ConfigError] or [TransientError]. This is
 * whatever falls through the cracks of the [ExceptionClassifier], as such there is a standing goal
 * to minimize occurrences of these instances.
 */
data class SystemError(val displayMessage: String?) : ConnectorError

/** Common Micronaut property prefix for all exception classifiers. */
const val EXCEPTION_CLASSIFIER_PREFIX = "airbyte.connector.exception-classifiers"

/** Convenience interface for rules-based [ExceptionClassifier] implementations. */
interface RuleBasedExceptionClassifier<T : RuleBasedExceptionClassifier.Rule> :
    ExceptionClassifier {

    /** List of rules to match for. */
    val rules: List<T>

    override fun classify(e: Throwable): ConnectorError? {
        for (rule in rules) {
            if (!rule.matches(e)) {
                continue
            }
            val message: String = rule.output ?: e.message ?: e.toString()
            val firstLine: String = if (rule.group == null) message else "${rule.group}: $message"
            val lines: List<String> = listOf(firstLine) + rule.referenceLinks
            val displayMessage: String = lines.joinToString(separator = "\n")
            return when (rule.error) {
                ErrorKind.CONFIG -> ConfigError(displayMessage)
                ErrorKind.TRANSIENT -> TransientError(displayMessage)
                ErrorKind.SYSTEM -> SystemError(displayMessage)
            }
        }
        return null
    }

    interface Rule : Ordered {

        /** Rule ordinal in the rule set. */
        val ordinal: Int

        /** If the rule matches, the kind of [ConnectorError] to produce. */
        val error: ErrorKind

        /** Optional display message prefix. */
        val group: String?

        /** Optional display message. */
        val output: String?

        /** Optional list of reference links to display. */
        val referenceLinks: List<String>

        /** Rule predicate. */
        fun matches(e: Throwable): Boolean

        override fun getOrder(): Int = ordinal

        /** Validates rule definition correctness. */
        fun validate()
    }

    enum class ErrorKind {
        CONFIG,
        TRANSIENT,
        SYSTEM,
    }
}
