/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.component

import io.airbyte.cdk.load.component.DefaultComponentTestCatalog
import io.airbyte.cdk.load.component.config.TestConfigLoader.loadTestConfig
import io.airbyte.integrations.destination.redshift_v2.spec.RedshiftV2Configuration
import io.airbyte.integrations.destination.redshift_v2.spec.RedshiftV2ConfigurationFactory
import io.airbyte.integrations.destination.redshift_v2.spec.RedshiftV2Specification
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Requires(env = ["component"])
@Factory
class RedshiftTestConfigFactory {
    @Singleton
    @Primary
    fun config(): RedshiftV2Configuration {
        return loadTestConfig(
            RedshiftV2Specification::class.java,
            RedshiftV2ConfigurationFactory::class.java,
            "config.json",
        )
    }

    @Singleton
    @Primary
    fun catalog(): ConfiguredAirbyteCatalog {
        return DefaultComponentTestCatalog.make()
    }
}
