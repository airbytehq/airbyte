/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.check

import com.fasterxml.jackson.databind.DeserializationFeature
import com.fasterxml.jackson.databind.ObjectMapper
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.integrations.destination.redshift2.client.RedshiftSqlGenerator
import io.airbyte.integrations.destination.redshift2.config.RedshiftConfiguration
import io.airbyte.integrations.destination.redshift2.config.RedshiftConfigurationFactory
import io.airbyte.integrations.destination.redshift2.config.RedshiftConnect
import io.airbyte.integrations.destination.redshift2.config.RedshiftSpecification
import java.nio.file.Files
import java.nio.file.Path
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestInstance

/**
 * Standalone integration test for [RedshiftChecker].
 *
 * Manually constructs all dependencies from secrets/config_staging.json
 * (no CDK integration test hierarchy). Exercises the full 7-step checker pipeline:
 * Redshift connect -> S3 write -> CREATE TABLE -> COPY -> count -> delete -> cleanup.
 *
 * Requires a valid secrets/config_staging.json with Redshift + S3 credentials.
 * Will fail hard if the file is absent.
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class RedshiftCheckerTest {

    private val mapper =
        ObjectMapper()
            .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)

    private val config = mapper.readTree(Files.readString(Path.of("secrets/config.json")))

    private lateinit var configuration: RedshiftConfiguration
    private lateinit var redshiftConnect: RedshiftConnect
    private lateinit var dataSource: HikariDataSource
    private lateinit var sqlGenerator: RedshiftSqlGenerator
    private lateinit var checker: RedshiftChecker

    @BeforeAll
    fun setup() {
        val spec = mapper.treeToValue(config, RedshiftSpecification::class.java)
        configuration = RedshiftConfigurationFactory().makeWithoutExceptionHandling(spec)
        redshiftConnect = RedshiftConnect(configuration)
        dataSource = redshiftConnect.createDataSource()
        sqlGenerator = RedshiftSqlGenerator()
        checker = RedshiftChecker(dataSource, configuration, redshiftConnect, sqlGenerator)
    }

    @AfterAll
    fun teardown() {
        if (::dataSource.isInitialized) {
            dataSource.close()
        }
    }

    @Test
    fun testCheckSucceeds() {
        checker.check()
    }
}
