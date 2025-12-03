/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.schema.model

import io.airbyte.cdk.load.table.TableSuffixes

data class TableName(val namespace: String, val name: String) {
    fun toPrettyString(quote: String = "", suffix: String = "") =
        "$quote$namespace$quote.$quote$name$suffix$quote"

    fun asOldStyleTempTable() = copy(name = name + TableSuffixes.TMP_TABLE_SUFFIX)
}
