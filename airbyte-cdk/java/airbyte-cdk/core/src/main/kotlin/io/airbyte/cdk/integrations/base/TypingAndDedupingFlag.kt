/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base

import java.util.*

object TypingAndDedupingFlag {
    @JvmStatic
    val isDestinationV2: Boolean
        get() =
            (DestinationConfig.Companion.instance!!.isV2Destination ||
                DestinationConfig.Companion.instance!!.getBooleanValue("use_1s1t_format"))

    @JvmStatic
    fun getRawNamespaceOverride(option: String?): Optional<String> {
        val rawOverride: String = DestinationConfig.Companion.instance!!.getTextValue(option)
        return if (rawOverride.isEmpty()) {
            Optional.empty()
        } else {
            Optional.ofNullable(rawOverride)
        }
    }
}
