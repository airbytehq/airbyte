package io.airbyte.cdk.core.config

import com.fasterxml.jackson.databind.node.ObjectNode
import com.github.victools.jsonschema.generator.FieldScope
import com.github.victools.jsonschema.generator.InstanceAttributeOverrideV2
import com.github.victools.jsonschema.generator.SchemaGenerationContext
import io.airbyte.cdk.core.config.annotation.AirbyteDisplayHint
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

private val logger = KotlinLogging.logger {}

@Singleton
class AirbytePropertyInfoOverrideProvider:InstanceAttributeOverrideV2<FieldScope> {
    override fun overrideInstanceAttributes(fieldSchema: ObjectNode, member: FieldScope, context: SchemaGenerationContext) {
        val airbyteDisplayHint: AirbyteDisplayHint? = member.getAnnotationConsideringFieldAndGetter(AirbyteDisplayHint::class.java)
        airbyteDisplayHint?.let {
            fieldSchema.put("description", it.description)
            fieldSchema.put("title", it.title)
            fieldSchema.put("airbyte_secret", it.secret)
            fieldSchema.put("always_show", it.alwaysShow)

            // TODO create resolver beans that can be referenced by the AirbyteDisplayHint annotation
            //      and used here to retrieve the values of the enum.  Potentially support both setting
            //      the enum values directly on the configuration or using an enum-ref, which is the name
            //      of the SpeEnumResolver bean to use to fetch those values

            if (it.enum.isNotEmpty()) {
                it.enum.forEach { value -> fieldSchema.putArray("enum").add(value) }
            }
            if (it.examples.isNotEmpty()) {
                it.examples.forEach { value -> fieldSchema.putArray("examples").add(value) }
            }
            fieldSchema.put("order", it.order)
        }
    }
}