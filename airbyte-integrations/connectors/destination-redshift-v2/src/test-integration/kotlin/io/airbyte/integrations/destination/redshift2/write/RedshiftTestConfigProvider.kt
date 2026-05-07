/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.write

import com.fasterxml.jackson.databind.DeserializationFeature
import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.integrations.destination.redshift2.client.RedshiftAirbyteClient
import io.airbyte.integrations.destination.redshift2.config.RedshiftConfiguration
import io.airbyte.integrations.destination.redshift2.config.RedshiftConfigurationFactory
import io.airbyte.integrations.destination.redshift2.config.RedshiftSpecification
import io.airbyte.integrations.destination.redshift2.connect.RedshiftConnect
import io.airbyte.integrations.destination.redshift2.sql.RedshiftSqlGenerator
import java.nio.file.Files
import java.nio.file.Path
import software.amazon.awssdk.regions.Region
import software.amazon.awssdk.services.s3.S3Client

/**
 * Centralized provider for test infrastructure objects. Eliminates duplicated config parsing,
 * DataSource creation, SqlGenerator instantiation, and AirbyteClient construction across test
 * files.
 */
object RedshiftTestConfigProvider {

    /** Shared, stateless SQL generator instance. */
    val sqlGenerator = RedshiftSqlGenerator()

    /** No-op S3 client stub for tests that don't need S3 (schema discovery, regression). */
    val noOpS3Client: S3Client by lazy { S3Client.builder().region(Region.US_EAST_1).build() }

    /** Parses a [ConfigurationSpecification] into a [RedshiftConfiguration]. */
    fun configFrom(spec: ConfigurationSpecification): RedshiftConfiguration =
        RedshiftConfigurationFactory().makeWithoutExceptionHandling(spec as RedshiftSpecification)

    /** Reads config from the secrets file and returns a [RedshiftConfiguration]. */
    fun configFromFile(): RedshiftConfiguration {
        val configJson = Files.readString(Path.of(CONFIG_PATH))
        val mapper =
            ObjectMapper().configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)
        val spec = mapper.readValue(configJson, RedshiftSpecification::class.java)
        return RedshiftConfigurationFactory().makeWithoutExceptionHandling(spec)
    }

    /**
     * Creates a [RedshiftAirbyteClient] from a [ConfigurationSpecification]. Uses a new DataSource
     * (not the shared pool) — suitable for short-lived test utilities like [RedshiftSchemaDumper]
     * and regression test ops clients.
     */
    fun airbyteClientFrom(spec: ConfigurationSpecification): RedshiftAirbyteClient {
        val config = configFrom(spec)
        val dataSource = RedshiftConnect(config).createDataSource()
        return RedshiftAirbyteClient(dataSource, sqlGenerator, noOpS3Client)
    }
}
