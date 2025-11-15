/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.enums

import com.google.common.base.Preconditions
import com.google.common.collect.Maps
import com.google.common.collect.Sets
import java.util.Locale
import java.util.Optional
import java.util.concurrent.ConcurrentMap

class Enums {
    companion object {
        @Suppress("UNUSED_PARAMETER")
        inline fun <T1 : Enum<T1>, reified T2 : Enum<T2>> convertTo(ie: T1?, oe: Class<T2>): T2? {
            if (ie == null) {
                return null
            }

            return enumValueOf<T2>(ie.name)
        }

        private fun normalizeName(name: String): String {
            return name.lowercase(Locale.getDefault()).replace("[^a-zA-Z0-9]".toRegex(), "")
        }

        @Suppress("UNCHECKED_CAST")
        fun <T : Enum<T>> toEnum(value: String, enumClass: Class<T>): Optional<T> {
            Preconditions.checkArgument(enumClass.isEnum)

            if (!NORMALIZED_ENUMS.containsKey(enumClass)) {
                val values = enumClass.enumConstants
                val mappings: MutableMap<String, T> = Maps.newHashMapWithExpectedSize(values.size)
                for (t in values) {
                    mappings[normalizeName(t!!.name)] = t
                }
                NORMALIZED_ENUMS[enumClass] = mappings
            }

            return Optional.ofNullable<T>(
                NORMALIZED_ENUMS.getValue(enumClass)[normalizeName(value)] as T?,
            )
        }

        private val NORMALIZED_ENUMS: ConcurrentMap<Class<*>, Map<String, *>> =
            Maps.newConcurrentMap()

        fun <T1 : Enum<T1>, T2 : Enum<T2>> isCompatible(c1: Class<T1>, c2: Class<T2>): Boolean {
            Preconditions.checkArgument(c1.isEnum)
            Preconditions.checkArgument(c2.isEnum)
            return (c1.enumConstants.size == c2.enumConstants.size &&
                Sets.difference(
                        c1.enumConstants.map { obj: T1 -> obj.name }.toSet(),
                        c2.enumConstants.map { obj: T2 -> obj.name }.toSet(),
                    )
                    .isEmpty())
        }

        inline fun <T1 : Enum<T1>, reified T2 : Enum<T2>> convertListTo(
            ies: List<T1>,
            oe: Class<T2>
        ): List<T2?> {
            return ies.map { convertTo(it, oe) }
        }
    }
}
