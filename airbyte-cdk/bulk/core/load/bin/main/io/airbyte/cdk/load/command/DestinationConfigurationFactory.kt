/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.ConnectorErrorException
import io.airbyte.cdk.command.ConfigurationSpecification

interface DestinationConfigurationFactory<
    I : ConfigurationSpecification, O : DestinationConfiguration> {
    fun makeWithoutExceptionHandling(pojo: I): O

    /** Wraps [makeWithoutExceptionHandling] exceptions in [ConfigErrorException]. */
    fun make(spec: I): O =
        try {
            makeWithoutExceptionHandling(spec)
        } catch (e: ConnectorErrorException) {
            throw e
        } catch (e: Exception) {
            // Wrap NPEs (mostly) in ConfigErrorException.
            throw ConfigErrorException("Failed to build ConnectorConfiguration.", e)
        }
}
