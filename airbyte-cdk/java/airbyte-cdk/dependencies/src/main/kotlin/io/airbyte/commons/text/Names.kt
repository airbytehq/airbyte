/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.text

import com.google.common.base.Preconditions
import java.text.Normalizer

object Names {
    const val NON_ALPHANUMERIC_AND_UNDERSCORE_PATTERN: String = "[^\\p{Alnum}_]"

    /**
     * Converts any UTF8 string to a string with only alphanumeric and _ characters without
     * preserving accent characters.
     *
     * @param s string to convert
     * @return cleaned string
     */
    @JvmStatic
    fun toAlphanumericAndUnderscore(s: String): String {
        return Normalizer.normalize(s, Normalizer.Form.NFKD)
            .replace(
                "\\p{M}".toRegex(),
                ""
            ) // P{M} matches a code point that is not a combining mark (unicode)
            .replace("\\s+".toRegex(), "_")
            .replace(NON_ALPHANUMERIC_AND_UNDERSCORE_PATTERN.toRegex(), "_")
    }

    fun doubleQuote(value: String): String {
        return internalQuote(value, '"')
    }

    fun singleQuote(value: String): String {
        return internalQuote(value, '\'')
    }

    private fun internalQuote(value: String, quoteChar: Char): String {
        Preconditions.checkNotNull(value)

        val startsWithChar = value[0] == quoteChar
        val endsWithChar = value[value.length - 1] == quoteChar

        Preconditions.checkState(startsWithChar == endsWithChar, "Invalid value: %s", value)

        return if (startsWithChar) {
            value
        } else {
            String.format("%c%s%c", quoteChar, value, quoteChar)
        }
    }
}
