/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.avro

import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import java.util.Locale

/**
 *
 * * An Avro name starts with [A-Za-z_], followed by [A-Za-z0-9_].
 * * An Avro namespace is a dot-separated sequence of such names.
 * * Reference: https://avro.apache.org/docs/current/spec.html#names
 */
class AvroNameTransformer : StandardNameTransformer() {
    override fun applyDefaultCase(input: String): String {
        return super.convertStreamName(input).lowercase(Locale.getDefault())
    }

    override fun convertStreamName(input: String): String {
        val normalizedName = super.convertStreamName(input)
        return if (normalizedName.substring(0, 1).matches("[A-Za-z_]".toRegex())) {
            normalizedName
        } else {
            "_$normalizedName"
        }
    }

    override fun getNamespace(namespace: String): String {
        val tokens = namespace.split("\\.".toRegex()).dropLastWhile { it.isEmpty() }.toTypedArray()
        return tokens
            .map { name: String ->
                this.getIdentifier(
                    name,
                )
            }
            .joinToString(separator = ".")
    }
}
