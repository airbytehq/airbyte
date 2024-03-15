/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base

import java.util.*

object TypingAndDedupingFlag {
    @JvmStatic
    val isDestinationV2: Boolean
        get() = (DestinationConfig.Companion.getInstance().getIsV2Destination()
                || DestinationConfig.Companion.getInstance().getBooleanValue("use_1s1t_format"))

    @JvmStatic
    fun getRawNamespaceOverride(option: String?): Optional<String> {
        val rawOverride: String = DestinationConfig.Companion.getInstance().getTextValue(option)
        return if (rawOverride == null || rawOverride.isEmpty()) {
            Optional.empty()
        } else {
            Optional.of(rawOverride)
        }
    }
}
