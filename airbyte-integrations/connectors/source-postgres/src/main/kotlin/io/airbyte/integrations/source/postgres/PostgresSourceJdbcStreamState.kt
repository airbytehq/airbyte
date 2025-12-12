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
import io.github.oshai.kotlinlogging.KotlinLogging

typealias Filenode = Long

/** Delegates to [DefaultJdbcStreamState] except for [maybeFilenode]. */
class PostgresSourceJdbcStreamState(val base: DefaultJdbcStreamState) :
    JdbcStreamState<DefaultJdbcSharedState> by base {
    private val log = KotlinLogging.logger {}
    val stateValue: PostgresSourceJdbcStreamStateValue?
        get() =
            streamFeedBootstrap.currentState?.let {
                val ver =
                    Jsons.treeToValue(
                        it,
                        PostgresSourceJdbcV2VersionOnlyStreamStateValue::class.java
                    )
                when (ver?.version) {
                    2 ->
                        PostgresSourceJdbcV2CompatibilityStreamStateValue.toV3StateValue(
                            Jsons.treeToValue(
                                it,
                                PostgresSourceJdbcV2CompatibilityStreamStateValue::class.java
                            ),
                            streamFeedBootstrap.feed
                        )
                    3 -> Jsons.treeToValue(it, PostgresSourceJdbcStreamStateValue::class.java)
                    else -> {
                        log.warn { "State version not specified. Defaulting to V3" }
                        Jsons.treeToValue(it, PostgresSourceJdbcStreamStateValue::class.java)
                    }
                }
            }

    val maybeFilenode: Filenode?
        get() = stateValue?.filenode
    val maybeCtid: Ctid?
        get() = stateValue?.let { sv -> sv.ctid?.let { Ctid.of(it) } }

    override fun validatePartition(
        partition: JdbcPartition<*>,
        jdbcConnectionFactory: JdbcConnectionFactory
    ) {
        val savedFilenode: Filenode? =
            when (partition) {
                is PostgresSourceJdbcSplittableSnapshotPartition -> partition.filenode
                is PostgresSourceJdbcSplittableSnapshotWithCursorPartition -> partition.filenode
                else -> return
            }
        val currentFilenode: Filenode? =
            PostgresSourceJdbcPartitionFactory.getStreamFilenode(
                partition.streamState,
                jdbcConnectionFactory
            )

        if (currentFilenode != savedFilenode) {
            throw TransientErrorException(
                "Full vacuum on table ${partition.streamState.stream.id} detected. Filenode changed from ${savedFilenode} to $currentFilenode"
            )
        }
    }
}
