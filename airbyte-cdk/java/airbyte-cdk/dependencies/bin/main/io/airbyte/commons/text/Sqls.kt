/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.text

import java.util.*

object Sqls {
    fun <T : Enum<T>> toSqlName(value: T): String {
        return value.name.lowercase(Locale.getDefault())
    }

    fun <T : Enum<T>> toSqlNames(values: Collection<T>): Set<String> {
        return values.map { toSqlName(it) }.toSet()
    }

    /**
     * Generate a string fragment that can be put in the IN clause of a SQL statement. eg. column IN
     * (value1, value2)
     *
     * @param values to encode
     * @param <T> enum type
     * @return "'value1', 'value2', 'value3'" </T>
     */
    fun <T : Enum<T>> toSqlInFragment(values: Iterable<T>): String {
        return values.map { toSqlName(it) }.joinToString(",", "(", ")") { Names.singleQuote(it) }
    }
}
