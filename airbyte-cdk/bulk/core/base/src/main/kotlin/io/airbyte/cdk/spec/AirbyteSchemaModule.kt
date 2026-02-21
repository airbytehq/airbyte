/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.spec

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.github.victools.jsonschema.generator.FieldScope
import com.github.victools.jsonschema.generator.MethodScope
import com.github.victools.jsonschema.generator.Module
import com.github.victools.jsonschema.generator.SchemaGeneratorConfigBuilder
import com.github.victools.jsonschema.generator.TypeScope
import io.airbyte.cdk.spec.annotations.JsonSchemaArrayWithUniqueItems
import io.airbyte.cdk.spec.annotations.JsonSchemaDefault
import io.airbyte.cdk.spec.annotations.JsonSchemaDescription
import io.airbyte.cdk.spec.annotations.JsonSchemaInject
import io.airbyte.cdk.spec.annotations.JsonSchemaTitle
import io.airbyte.cdk.util.Jsons

class AirbyteSchemaModule : Module {
    override fun applyToConfigBuilder(builder: SchemaGeneratorConfigBuilder) {
        builder.forFields().withTitleResolver(::resolveFieldTitle)
        builder.forFields().withDescriptionResolver(::resolveFieldDescription)
        builder.forFields().withDefaultResolver(::resolveFieldDefault)
        builder.forFields().withInstanceAttributeOverride(::overrideFieldAttributes)

        builder.forMethods().withTitleResolver(::resolveMethodTitle)
        builder.forMethods().withDescriptionResolver(::resolveMethodDescription)
        builder.forMethods().withDefaultResolver(::resolveMethodDefault)
        builder.forMethods().withInstanceAttributeOverride(::overrideMethodAttributes)

        builder.forTypesInGeneral().withTitleResolver(::resolveTypeTitle)
        builder.forTypesInGeneral().withDescriptionResolver(::resolveTypeDescription)
        builder.forTypesInGeneral().withTypeAttributeOverride(::overrideTypeAttributes)
    }

    private fun resolveFieldTitle(field: FieldScope): String? =
        field.getAnnotationConsideringFieldAndGetter(JsonSchemaTitle::class.java)?.value

    private fun resolveFieldDescription(field: FieldScope): String? =
        field.getAnnotationConsideringFieldAndGetter(JsonSchemaDescription::class.java)?.value

    private fun resolveFieldDefault(field: FieldScope): Any? {
        val defaultValue =
            field.getAnnotationConsideringFieldAndGetter(JsonSchemaDefault::class.java)?.value
                ?: return null
        return parseDefaultValue(defaultValue)
    }

    private fun resolveMethodTitle(method: MethodScope): String? =
        method.getAnnotation(JsonSchemaTitle::class.java)?.value

    private fun resolveMethodDescription(method: MethodScope): String? =
        method.getAnnotation(JsonSchemaDescription::class.java)?.value

    private fun resolveMethodDefault(method: MethodScope): Any? {
        val defaultValue =
            method.getAnnotation(JsonSchemaDefault::class.java)?.value ?: return null
        return parseDefaultValue(defaultValue)
    }

    private fun resolveTypeTitle(scope: TypeScope): String? =
        scope.type.erasedType.getAnnotation(JsonSchemaTitle::class.java)?.value

    private fun resolveTypeDescription(scope: TypeScope): String? =
        scope.type.erasedType.getAnnotation(JsonSchemaDescription::class.java)?.value

    private fun overrideFieldAttributes(
        node: ObjectNode,
        field: FieldScope,
        @Suppress("UNUSED_PARAMETER") context: com.github.victools.jsonschema.generator.SchemaGenerationContext,
    ) {
        applyInject(
            node,
            field.getAnnotationConsideringFieldAndGetter(JsonSchemaInject::class.java),
        )
        applyUniqueItems(
            node,
            field.getAnnotationConsideringFieldAndGetter(
                JsonSchemaArrayWithUniqueItems::class.java,
            ),
        )
    }

    private fun overrideMethodAttributes(
        node: ObjectNode,
        method: MethodScope,
        @Suppress("UNUSED_PARAMETER") context: com.github.victools.jsonschema.generator.SchemaGenerationContext,
    ) {
        applyInject(node, method.getAnnotation(JsonSchemaInject::class.java))
        applyUniqueItems(node, method.getAnnotation(JsonSchemaArrayWithUniqueItems::class.java))
    }

    private fun overrideTypeAttributes(
        node: ObjectNode,
        scope: TypeScope,
        @Suppress("UNUSED_PARAMETER") context: com.github.victools.jsonschema.generator.SchemaGenerationContext,
    ) {
        applyInject(
            node,
            scope.type.erasedType.getAnnotation(JsonSchemaInject::class.java),
        )
    }

    private fun applyInject(node: ObjectNode, annotation: JsonSchemaInject?) {
        if (annotation == null) return
        val injected: JsonNode = Jsons.readTree(annotation.json)
        if (injected is ObjectNode) {
            injected.fields().forEach { (key, value) ->
                node.set<JsonNode>(key, value)
            }
        }
    }

    private fun applyUniqueItems(node: ObjectNode, annotation: JsonSchemaArrayWithUniqueItems?) {
        if (annotation == null) return
        node.put("uniqueItems", true)
    }

    private fun parseDefaultValue(value: String): Any {
        return try {
            Jsons.readTree(value)
        } catch (_: Exception) {
            value
        }
    }
}
