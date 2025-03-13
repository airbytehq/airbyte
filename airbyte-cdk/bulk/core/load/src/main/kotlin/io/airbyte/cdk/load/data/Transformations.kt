/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import java.text.Normalizer
import java.util.regex.Pattern

class Transformations {
    companion object {
        private const val S3_SAFE_CHARACTERS = "\\p{Alnum}/!_.*')("
        private const val S3_SPECIAL_CHARACTERS = "&$@=;:+,?-"
        private val S3_CHARACTER_PATTERN =
            "[^${S3_SAFE_CHARACTERS}${Pattern.quote(S3_SPECIAL_CHARACTERS)}]"
        const val NON_ALPHANUMERIC_AND_UNDERSCORE_PATTERN: String = "[^\\p{Alnum}_]"

        fun toS3SafeCharacters(input: String): String {
            return Normalizer.normalize(input, Normalizer.Form.NFKD)
                .replace(
                    "\\p{M}".toRegex(),
                    "",
                ) // P{M} matches a code point that is not a combining mark (unicode)
                .replace(S3_CHARACTER_PATTERN.toRegex(), "_")
        }

        fun toAlphanumericAndUnderscore(s: String): String {
            return Normalizer.normalize(s, Normalizer.Form.NFKD)
                .replace(
                    "\\p{M}".toRegex(),
                    ""
                ) // P{M} matches a code point that is not a combining mark (unicode)
                .replace("\\s+".toRegex(), "_")
                .replace(NON_ALPHANUMERIC_AND_UNDERSCORE_PATTERN.toRegex(), "_")
        }

        fun toAvroSafeNamespace(namespace: String): String {
            val tokens =
                namespace.split("\\.".toRegex()).dropLastWhile { it.isEmpty() }.toTypedArray()
            return tokens
                .map { name: String -> toAlphanumericAndUnderscore(name) }
                .joinToString(separator = ".")
        }

        fun toAvroSafeName(name: String): String {
            val stripped = toAlphanumericAndUnderscore(name)
            return if (stripped.substring(0, 1).matches("[A-Za-z_]".toRegex())) {
                stripped
            } else {
                "_$stripped"
            }
        }
    }
}
