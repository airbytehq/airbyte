/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.config

import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.Operation
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.load.dataflow.config.model.AggregatePublishingConfig
import io.airbyte.cdk.load.table.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.integrations.destination.redshift.connect.RedshiftConnect
import io.airbyte.integrations.destination.redshift.connect.S3Connect
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import software.amazon.awssdk.services.s3.S3Client

/** Micronaut Factory for creating and wiring Redshift destination beans. */
@Factory
class RedshiftBeanFactory {

    @Singleton
    fun redshiftConfiguration(
        configFactory: RedshiftConfigurationFactory,
        specFactory: ConfigurationSpecificationSupplier<RedshiftSpecification>
    ): RedshiftConfiguration {
        val spec = specFactory.get()
        return configFactory.makeWithoutExceptionHandling(spec)
    }

    /** Creates the HikariCP DataSource for Redshift connections */
    @Singleton
    @Requires(property = Operation.PROPERTY, notEquals = "spec")
    fun redshiftDataSource(redshiftConnect: RedshiftConnect): HikariDataSource {
        return redshiftConnect.createDataSource()
    }

    /** Creates the S3 client for staging operations */
    @Singleton
    @Requires(property = Operation.PROPERTY, notEquals = "spec")
    fun s3Client(s3Connect: S3Connect): S3Client {
        return s3Connect.createS3Client()
    }

    /** Generates deterministic temp table names for staging during dedup/truncate syncs. */
    @Singleton
    fun tempTableNameGenerator(): TempTableNameGenerator = DefaultTempTableNameGenerator()

    /**
     * Configures aggregate publishing thresholds for the CDK dataflow pipeline.
     *
     * Redshift loads data via S3 staging + COPY, which has fixed per-invocation overhead. Larger
     * batches amortize this cost better. 200 MB per aggregate with 1 GB total across all streams
     * balances throughput against memory usage.
     *
     * maxRecordsPerAgg is very high so that we always hit the flush limits based on Bytes metric
     */
    @Singleton
    fun aggregatePublishingConfig(): AggregatePublishingConfig =
        AggregatePublishingConfig(
            maxRecordsPerAgg = 10_000_000_000_000L,
            maxEstBytesPerAgg = 150_000_000L,
            maxEstBytesAllAggregates = 1_500_000_000L,
            maxBufferedAggregates = 10,
        )
}
