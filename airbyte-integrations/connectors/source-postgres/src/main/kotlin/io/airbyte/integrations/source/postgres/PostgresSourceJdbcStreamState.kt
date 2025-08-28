/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.DefaultJdbcSharedState
import io.airbyte.cdk.read.DefaultJdbcStreamState
import io.airbyte.cdk.read.JdbcPartition
import io.airbyte.cdk.read.JdbcStreamState
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.postgres.ctid.Ctid

typealias Filenode = Long

/** Delegates to [DefaultJdbcStreamState] except for [maybeFilenode]. */
class PostgresSourceJdbcStreamState(val base: DefaultJdbcStreamState) :
    JdbcStreamState<DefaultJdbcSharedState> by base {

    val stateValue: PostgresSourceJdbcStreamStateValue?
        get() =
            streamFeedBootstrap.currentState?.let {
                Jsons.treeToValue(it, PostgresSourceJdbcStreamStateValue::class.java)
            }

    val maybeFilenode: Filenode?
        get() = stateValue?.let { sv -> sv.filenode }
    val maybeCtid: Ctid?
        get() = stateValue?.let { sv -> sv.ctid?.let { Ctid(it) } }

    override fun validatePartition(
        partition: JdbcPartition<*>,
        jdbcConnectionFactory: JdbcConnectionFactory
    ) {
        val filenode: Filenode? = when (partition) {
            is PostgresSourceJdbcSplittableSnapshotPartition -> partition.filenode
            is PostgresSourceJdbcSplittableSnapshotWithCursorPartition -> partition.filenode
            else -> null
        }
        val currentFilenode: Filenode? = PostgresSourceJdbcPartitionFactory.getStreamFilenode(
            partition.streamState,
            jdbcConnectionFactory
        )

        if (currentFilenode != filenode) {
            throw TransientErrorException(
                "Full vacuum on table ${partition.streamState.stream.id} detected. Filenode changed from ${filenode} to $currentFilenode"
            )
        }
    }
}

