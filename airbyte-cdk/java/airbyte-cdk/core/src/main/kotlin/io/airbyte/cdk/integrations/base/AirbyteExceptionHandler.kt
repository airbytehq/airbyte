/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.annotations.VisibleForTesting
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*
import java.util.regex.Pattern
import javax.validation.constraints.NotNull
import org.apache.commons.lang3.exception.ExceptionUtils

private val LOGGER = KotlinLogging.logger {}

class AirbyteExceptionHandler : Thread.UncaughtExceptionHandler {
    override fun uncaughtException(thread: Thread, throwable: Throwable) {
        // This is a naive AirbyteTraceMessage emission in order to emit one when any error occurs
        // in a
        // connector.
        // If a connector implements AirbyteTraceMessage emission itself, this code will result in
        // an
        // additional one being emitted.
        // this is fine tho because:
        // "The earliest AirbyteTraceMessage where type=error will be used to populate the
        // FailureReason for
        // the sync."
        // from the spec:
        // https://docs.google.com/document/d/1ctrj3Yh_GjtQ93aND-WH3ocqGxsmxyC3jfiarrF6NY0/edit#
        try {
            LOGGER.error(throwable) { logMessage }
            // Attempt to deinterpolate the error message before emitting a trace message
            val mangledMessage: String?
            // If any exception in the chain is of a deinterpolatable type, find it and
            // deinterpolate
            // its
            // message.
            // This assumes that any wrapping exceptions are just noise (e.g. runtime exception).
            val deinterpolatableException =
                ExceptionUtils.getThrowableList(throwable)
                    .stream()
                    .filter { t: Throwable ->
                        THROWABLES_TO_DEINTERPOLATE.stream().anyMatch {
                            deinterpolatableClass: Class<out Throwable> ->
                            deinterpolatableClass.isAssignableFrom(t.javaClass)
                        }
                    }
                    .findFirst()
            val messageWasMangled: Boolean
            if (deinterpolatableException.isPresent) {
                val originalMessage = deinterpolatableException.get().message
                mangledMessage =
                    STRINGS_TO_DEINTERPOLATE
                        .stream() // Sort the strings longest to shortest, in case any target string
                        // is
                        // a substring of another
                        // e.g. "airbyte_internal" should be swapped out before "airbyte"
                        .sorted(Comparator.comparing { obj: String -> obj.length }.reversed())
                        .reduce(originalMessage) { message: String?, targetString: String? ->
                            deinterpolate(message, targetString)
                        }
                messageWasMangled = mangledMessage != originalMessage
            } else {
                mangledMessage = throwable.message
                messageWasMangled = false
            }

            if (!messageWasMangled) {
                // If we did not modify the message (either not a deinterpolatable class, or we
                // tried to
                // deinterpolate but made no changes) then emit our default trace message
                AirbyteTraceMessageUtility.emitSystemErrorTrace(throwable, logMessage)
            } else {
                // If we did modify the message, then emit a custom trace message
                AirbyteTraceMessageUtility.emitCustomErrorTrace(throwable.message, mangledMessage)
            }
        } catch (t: Throwable) {
            LOGGER.error(t) { "exception in the exception handler" }
        } finally {
            terminate()
        }
    }

    // by doing this in a separate method we can mock it to avoid closing the jvm and therefore test
    // properly
    fun terminate() {
        System.exit(1)
    }

    companion object {

        const val logMessage: String =
            "Something went wrong in the connector. See the logs for more details."

        // Basic deinterpolation helpers to avoid doing _really_ dumb deinterpolation.
        // E.g. if "id" is in the list of strings to remove, we don't want to modify the message
        // "Invalid
        // identifier".
        private const val REGEX_PREFIX = "(^|[^A-Za-z0-9])"
        private const val REGEX_SUFFIX = "($|[^A-Za-z0-9])"

        /**
         * If this list is populated, then the exception handler will attempt to deinterpolate the
         * error message before emitting a trace message. This is useful for connectors which (a)
         * emit a single exception class, and (b) rely on that exception's message to distinguish
         * between error types.
         *
         * If this is active, then the trace message will:
         *
         * 1. Not contain the stacktrace at all. This causes Sentry to use its fallback grouping
         * (using exception class and message)
         * 1. Contain the original exception message as the external message, and a mangled message
         * as the internal message.
         */
        @VisibleForTesting val STRINGS_TO_DEINTERPOLATE: MutableSet<String> = HashSet()

        init {
            addCommonStringsToDeinterpolate()
        }

        @VisibleForTesting
        val THROWABLES_TO_DEINTERPOLATE: MutableSet<Class<out Throwable>> = HashSet()

        private fun deinterpolate(message: String?, targetString: String?): @NotNull String? {
            // (?i) makes the pattern case-insensitive
            val quotedTarget = '('.toString() + "(?i)" + Pattern.quote(targetString) + ')'
            val targetRegex = REGEX_PREFIX + quotedTarget + REGEX_SUFFIX
            val pattern = Pattern.compile(targetRegex)
            val matcher = pattern.matcher(message)

            // The pattern has three capturing groups:
            // 1. The character before the target string (or an empty string, if it matched
            // start-of-string)
            // 2. The target string
            // 3. The character after the target string (or empty string for end-of-string)
            // We want to preserve the characters before and after the target string, so we use $1
            // and $3 to
            // reinsert them
            // but the target string is replaced with just '?'
            return matcher.replaceAll("$1?$3")
        }

        @JvmStatic
        fun addThrowableForDeinterpolation(klass: Class<out Throwable>) {
            THROWABLES_TO_DEINTERPOLATE.add(klass)
        }

        @JvmStatic
        fun addStringForDeinterpolation(string: String?) {
            if (string != null) {
                STRINGS_TO_DEINTERPOLATE.add(string.lowercase(Locale.getDefault()))
            }
        }

        @JvmStatic
        fun addAllStringsInConfigForDeinterpolation(node: JsonNode) {
            if (node.isTextual) {
                addStringForDeinterpolation(node.asText())
            } else if (node.isContainerNode) {
                for (subNode in node) {
                    addAllStringsInConfigForDeinterpolation(subNode)
                }
            }
        }

        internal fun addCommonStringsToDeinterpolate() {
            // Add some common strings to deinterpolate, regardless of what the connector is doing
            addStringForDeinterpolation("airbyte")
            addStringForDeinterpolation("config")
            addStringForDeinterpolation("configuration")
            addStringForDeinterpolation("description")
            addStringForDeinterpolation("email")
            addStringForDeinterpolation("id")
            addStringForDeinterpolation("location")
            addStringForDeinterpolation("message")
            addStringForDeinterpolation("name")
            addStringForDeinterpolation("state")
            addStringForDeinterpolation("status")
            addStringForDeinterpolation("type")
            addStringForDeinterpolation("userEmail")
        }
    }
}
