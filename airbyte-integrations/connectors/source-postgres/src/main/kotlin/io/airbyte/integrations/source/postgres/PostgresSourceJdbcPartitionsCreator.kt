/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.read.JdbcConcurrentPartitionsCreator
import io.airbyte.cdk.read.JdbcNonResumablePartitionReader
import io.airbyte.cdk.read.JdbcPartition
import io.airbyte.cdk.read.JdbcPartitionFactory
import io.airbyte.cdk.read.JdbcPartitionsCreator
import io.airbyte.cdk.read.JdbcPartitionsCreatorFactory
import io.airbyte.cdk.read.JdbcSharedState
import io.airbyte.cdk.read.JdbcStreamState
import io.airbyte.cdk.read.MODE_PROPERTY
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.Sample
import io.airbyte.cdk.read.SelectQuerier
import io.airbyte.cdk.read.SelectQuery
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Primary
@Requires(property = MODE_PROPERTY, value = "concurrent")
class PostgresSourceConcurrentJdbcPartitionsCreatorFactory<
    A : JdbcSharedState,
    S : JdbcStreamState<A>,
    P : JdbcPartition<S>,
>(
    partitionFactory: JdbcPartitionFactory<A, S, P>,
) : JdbcPartitionsCreatorFactory<A, S, P>(partitionFactory) {
    override fun partitionsCreator(partition: P): JdbcPartitionsCreator<A, S, P> =
        PostgresSourceJdbcConcurrentPartitionsCreator(partition, partitionFactory)
}

class PostgresSourceJdbcConcurrentPartitionsCreator<
    A : JdbcSharedState, S : JdbcStreamState<A>, P : JdbcPartition<S>>(
    partition: P,
    partitionFactory: JdbcPartitionFactory<A, S, P>,
) : JdbcConcurrentPartitionsCreator<A, S, P>(partition, partitionFactory) {
    private val log = KotlinLogging.logger {}

    override fun <T> collectSample(
        recordMapper: (SelectQuerier.ResultRow) -> T,
    ): Sample<T> {
        val values = mutableListOf<T>()
        var previousWeight = 0L
        for (sampleRateInvPow2 in listOf(20, 16, 8, 0)) {
            val sampleRateInv: Long = 1L shl sampleRateInvPow2
            log.info { "Sampling stream '${stream.label}' at rate 1 / $sampleRateInv." }
            // First, try sampling the table at a rate of one every 2^20 = 1,048,576 rows.
            // If that's not enough to produce the desired number of sampled rows (1024 by default)
            // then try sampling at a higher rate of one every 2^16 = 65,536 rows.
            // them 2^8 and if that's still not enough, don't sample at all.
            values.clear()
            val samplingQuery: SelectQuery = partition.samplingQuery(sampleRateInvPow2)
            selectQuerier.executeQuery(samplingQuery).use {
                for (row in it) {
                    values.add(recordMapper(row))
                }
            }
            if (values.size < sharedState.maxSampleSize) {
                previousWeight = sampleRateInv * values.size / sharedState.maxSampleSize
                continue
            }
            val kind: Sample.Kind =
                when (sampleRateInvPow2) {
                    20,
                    16 -> Sample.Kind.LARGE
                    8 -> Sample.Kind.MEDIUM
                    else -> Sample.Kind.SMALL
                }
            log.info { "Sampled ${values.size} rows in ${kind.name} stream '${stream.label}'." }
            return Sample(values, kind, previousWeight.coerceAtLeast(sampleRateInv))
        }
        val kind: Sample.Kind = if (values.isEmpty()) Sample.Kind.EMPTY else Sample.Kind.TINY
        log.info { "Sampled ${values.size} rows in ${kind.name} stream '${stream.label}'." }
        return Sample(values, kind, if (values.isEmpty()) 0L else 1L)
    }

    override suspend fun run(): List<PartitionReader> {
        return super.run().takeUnless { it.isEmpty() }
            ?: listOf(JdbcNonResumablePartitionReader(partition))
    }
}
