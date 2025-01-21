/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import io.airbyte.cdk.ConfigErrorException

/**
 * Each connector contains an implementation of this interface in a stateless class which maps the
 * configuration JSON object to a typed [Configuration] implementation which is more directly useful
 * to the rest of the connector.
 */
interface SourceConfigurationFactory<I : ConfigurationSpecification, O : SourceConfiguration> {
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
