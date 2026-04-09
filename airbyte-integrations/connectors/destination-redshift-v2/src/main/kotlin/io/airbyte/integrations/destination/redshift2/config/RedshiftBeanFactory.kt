/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.config

import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.Operation
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.integrations.destination.redshift2.connect.RedshiftConnect
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

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
}
