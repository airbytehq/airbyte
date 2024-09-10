/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.command.ConfigurationJsonObjectSupplier
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.micronaut.context.env.Environment
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject

@MicronautTest(environments = [Environment.TEST], rebuildContext = true)
class MysqlSourceConfigurationTest {
    @Inject
    lateinit var pojoSupplier: ConfigurationJsonObjectSupplier<MysqlSourceConfigurationJsonObject>

    @Inject
    lateinit var factory:
        SourceConfigurationFactory<MysqlSourceConfigurationJsonObject, MysqlSourceConfiguration>

    // TODO: add tests to cover SSL config to Jdbc Property conversion.
}
