/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc

import io.airbyte.protocol.models.v0.DestinationSyncMode
import java.time.Instant

/**
 * Write configuration POJO (plain old java object) for all destinations extending
 * [AbstractJdbcDestination].
 */
class WriteConfig
@JvmOverloads
constructor(
    val streamName: String,
    /**
     * This is used in [JdbcBufferedConsumerFactory] to verify that record is from expected streams
     *
     * @return
     */
    val namespace: String?,
    val outputSchemaName: String,
    val tmpTableName: String?,
    val outputTableName: String?,
    val syncMode: DestinationSyncMode,
    val writeDatetime: Instant = Instant.now()
) {
    override fun toString(): String {
        return "WriteConfig{" +
            "streamName=" +
            streamName +
            ", namespace=" +
            namespace +
            ", outputSchemaName=" +
            outputSchemaName +
            ", tmpTableName=" +
            tmpTableName +
            ", outputTableName=" +
            outputTableName +
            ", syncMode=" +
            syncMode +
            '}'
    }
}
