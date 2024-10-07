/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.testcontainers

object LoggingHelper {
    const val LOG_SOURCE_MDC_KEY: String = "log_source"
    const val PREPARE_COLOR_CHAR: String = "\u001b[m"
    const val RESET: String = "\u001B[0m"

    fun applyColor(
        color: Color,
        msg: String,
    ): String = PREPARE_COLOR_CHAR + color.code + msg + PREPARE_COLOR_CHAR + RESET

    fun logPrefixMdc(
        logPrefix: String,
        color: Color? = null,
    ): Pair<String, String> =
        LOG_SOURCE_MDC_KEY to
            when (color) {
                null -> logPrefix
                else -> applyColor(color, logPrefix)
            }

    enum class Color(
        val code: String,
    ) {
        BLACK("\u001b[30m"),
        RED("\u001b[31m"),
        GREEN("\u001b[32m"),
        YELLOW("\u001b[33m"),
        BLUE("\u001b[34m"),
        MAGENTA("\u001b[35m"),
        CYAN("\u001b[36m"),
        WHITE("\u001b[37m"),
        BLUE_BACKGROUND("\u001b[44m"), // source
        YELLOW_BACKGROUND("\u001b[43m"), // destination
        GREEN_BACKGROUND("\u001b[42m"), // normalization
        CYAN_BACKGROUND("\u001b[46m"), // container runner
        RED_BACKGROUND("\u001b[41m"), // testcontainers
        PURPLE_BACKGROUND("\u001b[45m"), // dbt
    }
}
