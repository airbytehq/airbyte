/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.config

import io.airbyte.validation.json.JsonSchemaValidator
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

@Factory
class ValidationFactory {

    @Singleton
    fun jsonSchemaValidator(): JsonSchemaValidator {
        return JsonSchemaValidator()
    }
}