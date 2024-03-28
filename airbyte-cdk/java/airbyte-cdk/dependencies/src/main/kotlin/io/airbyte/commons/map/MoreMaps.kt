/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.map

import com.google.common.base.Preconditions

object MoreMaps {
    @SafeVarargs
    @JvmStatic
    fun <K, V> merge(vararg maps: Map<K, V>): Map<K, V> {
        val outputMap: MutableMap<K, V> = HashMap()

        for (map in maps) {
            Preconditions.checkNotNull(map)
            outputMap.putAll(map)
        }

        return outputMap
    }
}
