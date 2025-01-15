/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgresv2

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.MetadataQuerier

class PostgresV2MetadataQuerier(
    val base: JdbcMetadataQuerier,
) : MetadataQuerier by base {
    override fun fields(streamID: StreamIdentifier): List<Field> {
        TODO("Not yet implemented")
    }

    override fun primaryKey(streamID: StreamIdentifier): List<List<String>> {
        TODO("Not yet implemented")
    }
}
