/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

fun interface NameMapper {
    /**
     * Some destinations only need to mangle the top-level names (e.g. Snowflake, where we write
     * nested data to a VARIANT column which preserves the nested field names), whereas other
     * destinations need to mangle the entire path (e.g. Avro files).
     *
     * So we need to accept the entire path here, instead of just accepting individual path
     * elements.
     */
    fun mapFieldName(path: List<String>): List<String>
}

object NoopNameMapper : NameMapper {
    override fun mapFieldName(path: List<String>): List<String> = path
}
