/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.string

import java.util.*
import org.apache.commons.lang3.RandomStringUtils

object Strings {
    @JvmStatic
    fun join(iterable: Iterable<Any>, separator: CharSequence): String {
        return iterable.joinToString(separator) { it.toString() }
    }

    @JvmStatic
    fun addRandomSuffix(base: String, separator: String, suffixLength: Int): String {
        return base +
            separator +
            RandomStringUtils.insecure()
                .nextAlphanumeric(suffixLength)
                .lowercase(Locale.getDefault())
    }

    @JvmStatic
    fun safeTrim(string: String?): String? {
        return string?.trim { it <= ' ' }
    }
}
