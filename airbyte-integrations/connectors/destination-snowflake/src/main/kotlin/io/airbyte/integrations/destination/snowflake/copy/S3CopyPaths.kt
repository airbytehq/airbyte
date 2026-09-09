package io.airbyte.integrations.destination.snowflake.copy

import java.util.UUID

/** A run owns its schema, cutoff directive, and all batch objects. */
internal object S3CopyPaths {
    fun run(config: S3CopyConfiguration, streamName: String, runId: UUID): String =
        "${config.prefix}/workspaces/${config.workspaceId}/sources/${config.sourceId}/connections/${config.connectionId}/streams/${escape(streamName)}/runs/$runId"

    // Encode the actual key component; the SDK separately handles HTTP URL encoding.
    fun escape(name: String): String {
        require(name.isNotEmpty()) { "Archive stream name must not be empty" }
        return name.toByteArray(Charsets.UTF_8).joinToString("") { byte ->
            val value = byte.toInt() and 0xff
            val char = value.toChar()
            if (char in 'a'..'z' || char in 'A'..'Z' || char in '0'..'9' ||
                char in "-_~" || (char == '.' && name != "." && name != "..")) {
                char.toString()
            } else {
                "%%%02X".format(value)
            }
        }
    }
}
