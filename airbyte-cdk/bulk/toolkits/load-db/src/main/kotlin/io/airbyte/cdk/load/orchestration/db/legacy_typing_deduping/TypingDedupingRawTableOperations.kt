/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping

import io.airbyte.cdk.load.orchestration.db.TableName

interface TypingDedupingRawTableOperations {
    /**
     * Prepare the raw table, including any associated blob storage. Similar to [createFinalTable],
     * accepts a [suffix] parameter, which should be used in conjunction with [overwriteRawTable].
     *
     * @param replace If true, then replace existing resources with empty e.g. tables. If false,
     * then leave existing resources untouched.
     */
    fun prepareRawTable(rawTableName: TableName, suffix: String, replace: Boolean = false)

    /**
     * Swap the "temporary" raw table into the "real" raw table. For example, `DROP TABLE IF NOT
     * EXISTS airbyte_internal.foo; ALTER TABLE airbyte_internal.foo_tmp RENAME TO foo`.
     */
    fun overwriteRawTable(rawTableName: TableName, suffix: String)

    /**
     * Copy all records from the temporary raw table into the real raw table, then drop the
     * temporary raw table. For example `INSERT INTO airbyte_internal.foo SELECT * FROM
     * airbyte_internal.foo_tmp; DROP TABLE airbyte_internal.foo_tmp`.
     */
    fun transferFromTempRawTable(rawTableName: TableName, suffix: String)

    /**
     * Get the generation of a single record in the raw table. Not necessarily the min or max
     * generation, just _any_ record.
     *
     * [TypingDedupingStreamLoader] is responsible for orchestrating the raw tables so that the temp
     * raw table always contains exactly one generation.
     *
     * @return The generation ID of a record in the raw table, or `null` if the raw table is empty.
     */
    fun getRawTableGeneration(rawTableName: TableName, suffix: String): Long?
}
