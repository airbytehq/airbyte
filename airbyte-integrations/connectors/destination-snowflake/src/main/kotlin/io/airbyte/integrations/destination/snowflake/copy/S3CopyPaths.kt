/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.copy

import java.util.UUID

/** A run owns its schema, completion marker, and all batch objects. */
internal object S3CopyPaths {
    fun run(
        config: S3CopyConfiguration,
        streamName: String,
        runId: UUID,
        epochSeconds: Long
    ): String {
        val path =
            "${config.prefix}/organizations/${config.organizationId}/workspaces/${config.workspaceId}/sources/${config.sourceId}/connections/${config.connectionId}/destinations/${config.destinationId}/syncs/streams/${escape(streamName)}/runs/$epochSeconds/$runId/"
        // Reserve the longest object suffix, including a full batch UUID, before any uploads.
        val longestKey = "${path}batches/${UUID(0, 0)}.csv.gz"
        require(longestKey.toByteArray(Charsets.UTF_8).size <= 1024) {
            "Archive object key exceeds the S3 limit of 1024 UTF-8 bytes"
        }
        return path
    }

    // Encode the actual key component; the SDK separately handles HTTP URL encoding.
    fun escape(name: String): String {
        require(name.isNotEmpty()) { "Archive stream name must not be empty" }
        return name.toByteArray(Charsets.UTF_8).joinToString("") { byte ->
            val value = byte.toInt() and 0xff
            val char = value.toChar()
            if (
                char in 'a'..'z' ||
                    char in 'A'..'Z' ||
                    char in '0'..'9' ||
                    char in "-_~" ||
                    (char == '.' && name != "." && name != "..")
            ) {
                char.toString()
            } else {
                "%%%02X".format(value)
            }
        }
    }
}
