/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.read

import io.airbyte.cdk.ConfigErrorException

/**
 * Persisted state that cannot be read fails the sync: starting over silently would replay the oplog
 * or re-emit a snapshot.
 */
object MongoDbStateMigration {
    fun failure(detail: String, cause: Throwable? = null): Nothing =
        throw ConfigErrorException(
            "Failed to migrate to the new connector version state protocol: $detail. " +
                "Reset the connection to start from a fresh snapshot.",
            cause,
        )

    inline fun require(condition: Boolean, detail: () -> String) {
        if (!condition) failure(detail())
    }
}
