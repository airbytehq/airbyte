/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.spec.annotations

@Target(
    AnnotationTarget.CLASS,
    AnnotationTarget.FIELD,
    AnnotationTarget.PROPERTY,
    AnnotationTarget.PROPERTY_GETTER,
    AnnotationTarget.FUNCTION,
    AnnotationTarget.VALUE_PARAMETER,
)
@Retention(AnnotationRetention.RUNTIME)
annotation class JsonSchemaInject(val json: String)
