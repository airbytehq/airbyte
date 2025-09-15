/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc

import io.airbyte.integrations.base.destination.typing_deduping.ImportType
import java.time.Instant

/**
 * Write configuration POJO (plain old java object) for all destinations extending
 * [AbstractJdbcDestination].
 */
data class WriteConfig
@JvmOverloads
constructor(
    val streamName: String,
    /**
     * This is used in [JdbcBufferedConsumerFactory] to verify that record is from expected streams
     *
     * @return
     */
    val namespace: String?,
    val rawNamespace: String,
    val tmpTableName: String?,
    val rawTableName: String,
    val postImportAction: ImportType,
    val syncId: Long,
    val generationId: Long,
    val minimumGenerationId: Long,
    val rawTableSuffix: String,
    val writeDatetime: Instant = Instant.now(),
)
