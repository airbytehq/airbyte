/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.command

import io.airbyte.commons.exceptions.ConfigErrorException
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

/**
 * Each connector contains an implementation of this interface in a stateless class which maps the
 * configuration JSON object to a typed [Configuration] implementation which is more directly useful
 * to the rest of the connector.
 */
interface ConfigurationFactory<I : ConfigurationJsonObjectBase, O : Configuration> {

    fun makeWithoutExceptionHandling(pojo: I): O

    /** Wraps [makeWithoutExceptionHandling] exceptions in [ConfigErrorException]. */
    fun make(pojo: I): O =
        try {
            makeWithoutExceptionHandling(pojo)
        } catch (e: Exception) {
            // Wrap NPEs (mostly) in ConfigErrorException.
            throw ConfigErrorException("Failed to build ConnectorConfiguration.", e)
        }

    /**
     * Micronaut factory which glues [ConfigurationJsonObjectSupplier] and [ConfigurationFactory]
     * together to produce a [Configuration] singleton.
     */
    @Factory
    private class MicronautFactory {

        @Singleton
        fun <I : ConfigurationJsonObjectBase> sourceConfig(
            pojoSupplier: ConfigurationJsonObjectSupplier<I>,
            factory: ConfigurationFactory<I, out SourceConfiguration>
        ): SourceConfiguration = factory.make(pojoSupplier.get())
    }
}
