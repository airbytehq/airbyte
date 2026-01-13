/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.table

object TableSuffixes {
    const val NO_SUFFIX = ""
    // TODO comment explaining this
    const val TMP_TABLE_SUFFIX = "_airbyte_tmp"
    const val SOFT_RESET_SUFFIX = "_ab_soft_reset"
}
