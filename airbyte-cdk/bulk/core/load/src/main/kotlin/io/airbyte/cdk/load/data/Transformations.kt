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

        fun toS3SafeCharacters(input: String): String {
            return Normalizer.normalize(input, Normalizer.Form.NFKD)
                .replace(
                    "\\p{M}".toRegex(),
                    "",
                ) // P{M} matches a code point that is not a combining mark (unicode)
                .replace(S3_CHARACTER_PATTERN.toRegex(), "_")
        }
    }
}
