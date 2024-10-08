/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.util

import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import java.text.Normalizer
import java.util.regex.Pattern

open class S3NameTransformer : StandardNameTransformer() {

    companion object {
        // see https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-keys.html
        private const val S3_SAFE_CHARACTERS = "\\p{Alnum}/!_.*')("
        private const val S3_SPECIAL_CHARACTERS = "&$@=;:+,?-"
        private val S3_CHARACTER_PATTERN =
            "[^${S3_SAFE_CHARACTERS}${Pattern.quote(S3_SPECIAL_CHARACTERS)}]"
    }

    override fun convertStreamName(input: String): String {
        return Normalizer.normalize(input, Normalizer.Form.NFKD)
            .replace(
                "\\p{M}".toRegex(),
                "",
            ) // P{M} matches a code point that is not a combining mark (unicode)
            .replace(S3_CHARACTER_PATTERN.toRegex(), "_")
    }
}
