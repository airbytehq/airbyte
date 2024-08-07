/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.normalization

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.configoss.OperatorDbt
import io.airbyte.configoss.ResourceRequirements
import io.airbyte.protocol.models.AirbyteTraceMessage
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog
import java.nio.file.Path
import java.util.stream.Stream

interface NormalizationRunner : AutoCloseable {
    /**
     * After this method is called, the caller must call close. Previous to this method being called
     * a NormalizationRunner can be instantiated and not worry about close being called.
     *
     * @throws Exception
     * - any exception thrown from normalization will be handled gracefully by the caller.
     */
    @Throws(Exception::class)
    fun start() {
        // no-op.
    }

    /**
     * Prepare a configured folder to run dbt commands from (similar to what is required by
     * normalization models) However, this does not run the normalization file generation process or
     * dbt at all. This is pulling files from a distant git repository instead of the
     * dbt-project-template.
     *
     * @return true if configuration succeeded. otherwise false.
     * @throws Exception
     * - any exception thrown from configuration will be handled gracefully by the caller.
     */
    @Throws(Exception::class)
    fun configureDbt(
        jobId: String,
        attempt: Int,
        jobRoot: Path,
        config: JsonNode?,
        resourceRequirements: ResourceRequirements?,
        dbtConfig: OperatorDbt
    ): Boolean

    /**
     * Executes normalization of the data in the destination.
     *
     * @param jobId
     * - id of the job that launched normalization
     * @param attempt
     * - current attempt
     * @param jobRoot
     * - root dir available for the runner to use.
     * @param config
     * - configuration for connecting to the destination
     * @param catalog
     * - the schema of the json blob in the destination. it is used normalize the blob into typed
     * columns.
     * @param resourceRequirements
     * @return true of normalization succeeded. otherwise false.
     * @throws Exception
     * - any exception thrown from normalization will be handled gracefully by the caller.
     */
    @Throws(Exception::class)
    fun normalize(
        jobId: String,
        attempt: Int,
        jobRoot: Path,
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        resourceRequirements: ResourceRequirements?
    ): Boolean

    val traceMessages: Stream<AirbyteTraceMessage>
}
