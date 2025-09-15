/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.operation

import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import java.time.Instant
import java.util.Optional

interface StorageOperation<Data> {
    /*
     *  ==================== Staging or Raw table Operations ================================
     */

    /**
     * Prepare staging area which cloud be creating any object storage, temp tables or file storage.
     * Similar to [createFinalTable], accepts a [suffix] parameter, which should be used in
     * conjunction with [overwriteStage].
     *
     * @param replace If true, then replace existing resources with empty e.g. tables. If false,
     * then leave existing resources untouched.
     */
    fun prepareStage(streamId: StreamId, suffix: String, replace: Boolean = false)

    /**
     * Swap the "temporary" stage into the "real" stage. For example, `DROP TABLE IF NOT EXISTS
     * airbyte_internal.foo; ALTER TABLE airbyte_internal.foo_tmp RENAME TO foo`.
     */
    fun overwriteStage(streamId: StreamId, suffix: String)

    /**
     * Copy all records from the temporary stage into the real stage, then drop the temporary stage.
     * For example `INSERT INTO airbyte_internal.foo SELECT * FROM airbyte_internal.foo_tmp; DROP
     * TABLE airbyte_internal.foo_tmp`.
     */
    fun transferFromTempStage(streamId: StreamId, suffix: String)

    /**
     * Get the generation of a single record in the stage. Not necessarily the min or max
     * generation, just _any_ record.
     *
     * [AbstractStreamOperation] is responsible for orchestrating the stages so that the temp stage
     * always contains exactly one generation.
     *
     * @return The generation ID of a record in the stage, or `null` if the stage is empty.
     */
    fun getStageGeneration(streamId: StreamId, suffix: String): Long?

    /** Delete previously staged data, using deterministic information from streamId. */
    fun cleanupStage(streamId: StreamId)

    /** Write data to stage. */
    fun writeToStage(streamConfig: StreamConfig, suffix: String, data: Data)

    /*
     *  ==================== Final Table Operations ================================
     */

    /** Create final table extracted from [StreamId] */
    fun createFinalTable(streamConfig: StreamConfig, suffix: String, replace: Boolean)

    /** Reset the final table using a temp table or ALTER existing table's columns. */
    fun softResetFinalTable(streamConfig: StreamConfig)

    /**
     * Attempt to atomically swap the final table (name and namespace extracted from [StreamId]).
     * This could be destination specific, INSERT INTO..SELECT * and DROP TABLE OR CREATE OR REPLACE
     * ... SELECT *, DROP TABLE
     */
    fun overwriteFinalTable(streamConfig: StreamConfig, tmpTableSuffix: String)

    /**
     */
    fun typeAndDedupe(
        streamConfig: StreamConfig,
        maxProcessedTimestamp: Optional<Instant>,
        finalTableSuffix: String
    )
}
