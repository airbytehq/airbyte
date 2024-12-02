/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.output

import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Requires
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton

/**
 * [CatalogValidationFailureHandler] implementation for unit tests. Collects everything into a
 * thread-safe buffer.
 */
@Singleton
@Requires(notEnv = [Environment.CLI])
@Replaces(CatalogValidationFailureHandler::class)
class BufferingCatalogValidationFailureHandler : CatalogValidationFailureHandler {
    private val failures = mutableListOf<CatalogValidationFailure>()

    fun get(): List<CatalogValidationFailure> =
        synchronized(this) { listOf(*failures.toTypedArray()) }

    override fun accept(f: CatalogValidationFailure) {
        synchronized(this) { failures.add(f) }
    }
}
