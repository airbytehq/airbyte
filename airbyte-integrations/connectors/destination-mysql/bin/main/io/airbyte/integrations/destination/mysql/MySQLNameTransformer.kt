/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.mysql

import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import java.util.*

/**
 * Note that MySQL documentation discusses about identifiers case sensitivity using the
 * lower_case_table_names system variable. As one of their recommendation is: "It is best to adopt a
 * consistent convention, such as always creating and referring to databases and tables using
 * lowercase names. This convention is recommended for maximum portability and ease of use.
 *
 * Source: https://dev.mysql.com/doc/refman/8.0/en/identifier-case-sensitivity.html"
 *
 * As a result, we are here forcing all identifier (table, schema and columns) names to lowercase.
 */
class MySQLNameTransformer : StandardNameTransformer() {
    override fun getIdentifier(name: String): String {
        val identifier = applyDefaultCase(super.getIdentifier(name))
        return truncateName(identifier, TRUNCATION_MAX_NAME_LENGTH)
    }

    override fun getTmpTableName(streamName: String): String {
        val tmpTableName = applyDefaultCase(super.getTmpTableName(streamName))
        return truncateName(tmpTableName, TRUNCATION_MAX_NAME_LENGTH)
    }

    override fun getRawTableName(streamName: String): String {
        val rawTableName = applyDefaultCase(super.getRawTableName(streamName))
        return truncateName(rawTableName, TRUNCATION_MAX_NAME_LENGTH)
    }

    override fun applyDefaultCase(input: String): String {
        return input.lowercase(Locale.getDefault())
    }

    companion object {
        // These constants must match those in destination_name_transformer.py
        const val MAX_MYSQL_NAME_LENGTH: Int = 64

        // DBT appends a suffix to table names
        const val TRUNCATE_DBT_RESERVED_SIZE: Int = 12

        // 4 charachters for 1 underscore and 3 suffix (e.g. _ab1)
        // 4 charachters for 1 underscore and 3 schema hash
        const val TRUNCATE_RESERVED_SIZE: Int = 8
        const val TRUNCATION_MAX_NAME_LENGTH: Int =
            MAX_MYSQL_NAME_LENGTH - TRUNCATE_DBT_RESERVED_SIZE - TRUNCATE_RESERVED_SIZE

        @JvmStatic
        fun truncateName(name: String, maxLength: Int): String {
            if (name.length <= maxLength) {
                return name
            }

            val allowedLength = maxLength - 2
            val prefix = name.substring(0, allowedLength / 2)
            val suffix = name.substring(name.length - allowedLength / 2)
            return prefix + "__" + suffix
        }
    }
}
