/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.command

import io.airbyte.cdk.ConfigErrorException

interface DestinationConfigurationFactory<
    I : ConfigurationSpecification, O : DestinationConfiguration> {
    fun makeWithoutExceptionHandling(pojo: I): O

    /** Wraps [makeWithoutExceptionHandling] exceptions in [ConfigErrorException]. */
    fun make(spec: I): O =
        try {
            makeWithoutExceptionHandling(spec)
        } catch (e: Exception) {
            // Wrap NPEs (mostly) in ConfigErrorException.
            throw ConfigErrorException("Failed to build ConnectorConfiguration.", e)
        }
}
