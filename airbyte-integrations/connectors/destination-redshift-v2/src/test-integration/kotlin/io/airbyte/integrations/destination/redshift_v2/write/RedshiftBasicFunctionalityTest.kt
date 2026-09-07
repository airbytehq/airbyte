/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.write

import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.UnknownTypesBehavior
import io.airbyte.integrations.destination.redshift_v2.spec.RedshiftV2Configuration
import io.airbyte.integrations.destination.redshift_v2.spec.RedshiftV2ConfigurationFactory
import io.airbyte.integrations.destination.redshift_v2.spec.RedshiftV2Specification
import java.nio.file.Files
import java.nio.file.Path
import javax.sql.DataSource
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode
import org.junit.jupiter.api.parallel.ResourceLock

/** Prevent concurrent execution with other Redshift test classes to avoid cluster contention. */
@Execution(ExecutionMode.SAME_THREAD)
@ResourceLock("redshift-cluster")
class RedshiftBasicFunctionalityTest :
    BasicFunctionalityIntegrationTest(
        configContents = Files.readString(Path.of("secrets/config.json")),
        configSpecClass = RedshiftV2Specification::class.java,
        dataDumper =
            RedshiftDataDumper(
                configProvider = { spec ->
                    RedshiftV2ConfigurationFactory()
                        .makeWithoutExceptionHandling(spec as RedshiftV2Specification)
                },
                dataSourceProvider = { config -> createDataSource(config) }
            ),
        destinationCleaner = RedshiftDataCleaner,
        // Redshift normalizes TIMESTAMPTZ to UTC, so we need to normalize expected values too
        recordMangler = RedshiftExpectedRecordMapper,

        // Schema behavior
        isStreamSchemaRetroactive = true,

        // CDC deletion mode - Redshift supports hard delete
        dedupBehavior = DedupBehavior(DedupBehavior.CdcDeletionMode.HARD_DELETE),

        // Type handling - Redshift has SUPER type for JSON
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        stringifyUnionObjects = false,

        // Feature support
        supportFileTransfer = false,
        commitDataIncrementally = false,
        commitDataIncrementallyOnAppend = false,
        commitDataIncrementallyToEmptyDestinationOnAppend = true,
        commitDataIncrementallyToEmptyDestinationOnDedupe = false,

        // Type system behavior - Redshift has BIGINT (64-bit) and DOUBLE PRECISION
        allTypesBehavior =
            StronglyTyped(
                integerCanBeLarge = false, // BIGINT has 64-bit limits
                numberCanBeLarge = true, // DOUBLE PRECISION can handle 1e39 (IEEE 754)
                nestedFloatLosesPrecision = false, // SUPER preserves JSON precision
            ),
        unknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
        nullEqualsUnset = true,

        // Dataflow CDK architecture - REQUIRED
        useDataFlowPipeline = true,
    ) {

    companion object {
        @JvmStatic
        @BeforeAll
        fun beforeAll() {
            // Configure cleaner with test namespaces
            val config = Files.readString(Path.of("secrets/config.json"))
            val spec =
                io.airbyte.cdk.command.ValidatedJsonUtils.parseUnvalidated(
                    config,
                    RedshiftV2Specification::class.java
                )
            val redshiftConfig = RedshiftV2ConfigurationFactory().makeWithoutExceptionHandling(spec)

            RedshiftDataCleaner.configure(
                dataSourceProvider = { createDataSource(redshiftConfig) },
                testNamespaces =
                    listOf("test", redshiftConfig.schema, redshiftConfig.internalSchema)
            )
        }

        private fun createDataSource(config: RedshiftV2Configuration): DataSource {
            val hikariConfig =
                HikariConfig().apply {
                    jdbcUrl = config.jdbcUrl
                    username = config.username
                    password = config.password
                    driverClassName = "com.amazon.redshift.jdbc42.Driver"
                    maximumPoolSize = 5
                    minimumIdle = 1
                    connectionTimeout = 30000
                    idleTimeout = 600000
                }
            return HikariDataSource(hikariConfig)
        }
    }

    @Test
    override fun testAppend() {
        super.testAppend()
    }

    @Test
    override fun testAppendSchemaEvolution() {
        super.testAppendSchemaEvolution()
    }

    @Test
    override fun testDedup() {
        super.testDedup()
    }

    @Test
    override fun testTruncateRefresh() {
        super.testTruncateRefresh()
    }
}
