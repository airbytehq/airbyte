/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.config

import com.fasterxml.jackson.annotation.JsonProperty
import com.github.victools.jsonschema.generator.*
import io.airbyte.validation.json.JsonSchemaValidator
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton


@Factory
class ValidationFactory {
    @Singleton
    fun jsonSchemaValidator(): JsonSchemaValidator {
        return JsonSchemaValidator()
    }

    @Singleton
    fun specGenerator(instanceAttributeOverride: AirbytePropertyInfoOverrideProvider): SchemaGenerator {
        val configBuilder = SchemaGeneratorConfigBuilder(SchemaVersion.DRAFT_2019_09, OptionPreset.PLAIN_JSON)
        configBuilder.forFields()
            .withRequiredCheck { field ->
                field.getAnnotationConsideringFieldAndGetter(JsonProperty::class.java)?.required ?: false
            }
            .withPropertyNameOverrideResolver { field ->
                field.getAnnotationConsideringFieldAndGetter(JsonProperty::class.java)?.value ?: field.name
            }
            .withDefaultResolver { field ->
                field.getAnnotationConsideringFieldAndGetter(JsonProperty::class.java)?.defaultValue ?: null
            }
            .withInstanceAttributeOverride(instanceAttributeOverride)


        val config = configBuilder.build()
        return SchemaGenerator(config)
    }
}
