/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import javax.inject.Singleton

class BigqueryConfiguration(val option: String) : DestinationConfiguration()

private val logger = KotlinLogging.logger {}

@Singleton
class BigqueryConfigurationFactory :
    DestinationConfigurationFactory<BigquerySpecification, BigqueryConfiguration> {
    override fun makeWithoutExceptionHandling(pojo: BigquerySpecification): BigqueryConfiguration {
        logger.info { "EDGAO DEBUG got pojo $pojo" }
        return BigqueryConfiguration(option = pojo.option)
    }
}
