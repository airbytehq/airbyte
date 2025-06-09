/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.cdk.load.test.util.FakeConfigurationUpdater
import io.airbyte.cdk.load.write.BasicPerformanceTest
import io.airbyte.cdk.load.write.DataValidator
import io.airbyte.integrations.destination.mssql.v2.config.DataSourceFactory
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLConfiguration
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLConfigurationFactory
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLSpecification
import java.nio.file.Files
import java.nio.file.Path
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test

class MSSQLDataValidator(
    private val getConfiguration:
        (spec: ConfigurationSpecification, stream: DestinationStream) -> MSSQLConfiguration
) : DataValidator {
    override fun count(spec: ConfigurationSpecification, stream: DestinationStream): Long? {
        val config = getConfiguration(spec as MSSQLSpecification, stream)
        val sqlBuilder = MSSQLQueryBuilder(config.schema, stream)
        val dataSource = DataSourceFactory().dataSource(config)

        return dataSource.connection.use { connection ->
            COUNT_FROM.toQuery(sqlBuilder.outputSchema, sqlBuilder.tableName).executeQuery(
                connection
            ) { rs ->
                while (rs.next()) {
                    return@executeQuery rs.getLong(1)
                }
                return@executeQuery null
            }
        }
    }
}

abstract class MSSQLPerformanceTest(
    configContents: String,
    configUpdater: ConfigurationUpdater,
    getConfiguration:
        (spec: ConfigurationSpecification, stream: DestinationStream) -> MSSQLConfiguration,
) :
    BasicPerformanceTest(
        configContents = configContents,
        configSpecClass = MSSQLSpecification::class.java,
        configUpdater = configUpdater,
        dataValidator = MSSQLDataValidator(getConfiguration),
        defaultRecordsToInsert = 10000,
    ) {
    @Test
    override fun testInsertRecords() {
        testInsertRecords(recordsToInsert = 100000) {}
    }

    @Test
    override fun testRefreshingRecords() {
        testRefreshingRecords { perfSummary ->
            perfSummary.forEach { streamSummary ->
                assertEquals(streamSummary.expectedRecordCount, streamSummary.recordCount)
            }
        }
    }

    @Test
    override fun testInsertRecordsWithDedup() {
        testInsertRecordsWithDedup { perfSummary ->
            perfSummary.map { streamSummary ->
                assertEquals(streamSummary.expectedRecordCount, streamSummary.recordCount)
            }
        }
    }
}

class MSSQLStandardInsertPerformanceTest :
    MSSQLPerformanceTest(
        configContents = Files.readString(MSSQLTestConfigUtil.getConfigPath("check/valid.json")),
        configUpdater = MSSQLConfigUpdater(),
        getConfiguration = { spec, stream ->
            val configOverrides =
                mutableMapOf("host" to MSSQLContainerHelper.getHost()).apply {
                    MSSQLContainerHelper.getPort()?.let { port -> put("port", port.toString()) }
                    stream.descriptor.namespace?.let { schema -> put("schema", schema) }
                }
            MSSQLConfigurationFactory()
                .makeWithOverrides(spec = spec as MSSQLSpecification, overrides = configOverrides)
        },
    ) {

    companion object {
        @JvmStatic
        @BeforeAll
        fun beforeAll() {
            MSSQLContainerHelper.start()
        }
    }
}

class MSSQLBulkInsertPerformanceTest :
    MSSQLPerformanceTest(
        configContents = Files.readString(Path.of("secrets/bulk_upload_config.json")),
        configUpdater = FakeConfigurationUpdater,
        getConfiguration = { spec, _ ->
            MSSQLConfigurationFactory().makeWithOverrides(spec as MSSQLSpecification, emptyMap())
        },
    )
