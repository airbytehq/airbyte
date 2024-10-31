/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc.copy

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import io.airbyte.cdk.integrations.destination.jdbc.SqlOperations
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream

interface StreamCopierFactory<T> {
    fun create(
        configuredSchema: String?,
        config: T,
        stagingFolder: String?,
        configuredStream: ConfiguredAirbyteStream?,
        nameTransformer: StandardNameTransformer?,
        db: JdbcDatabase?,
        sqlOperations: SqlOperations?
    ): StreamCopier

    companion object {
        @JvmStatic
        fun getSchema(
            namespace: String?,
            configuredSchema: String,
            nameTransformer: StandardNameTransformer
        ): String {
            return if (namespace != null) {
                nameTransformer.convertStreamName(namespace)
            } else {
                nameTransformer.convertStreamName(configuredSchema)
            }
        }
    }
}
