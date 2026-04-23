/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import com.fasterxml.jackson.annotation.JsonAnyGetter
import com.fasterxml.jackson.annotation.JsonAnySetter
import com.fasterxml.jackson.annotation.JsonIgnore
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class ValidatedJsonUtilsTest {

    /**
     * Regression test for airbytehq/oncall#12062 / airbytehq/airbyte#76942.
     *
     * The mbknor-jackson-jsonschema generator does not understand Jackson's `@JsonAnyGetter`
     * semantics. When a class exposes an any-getter returning `Map<String, Any>`, the generator
     * incorrectly emits it as a regular bean property called `"additionalProperties"` and — because
     * the Kotlin return type is non-nullable — also lists it in `required`. The fix in
     * `ValidatedJsonUtils.generateAirbyteJsonSchema` strips this spurious field from the generated
     * schema.
     */
    @Test
    fun testAnyGetterDoesNotLeakIntoGeneratedSchema() {
        val schema =
            ValidatedJsonUtils.generateAirbyteJsonSchema(SpecWithAnyGetter::class.java)
                as ObjectNode

        val properties = schema["properties"] as ObjectNode
        Assertions.assertTrue(
            properties.has("host"),
            "expected legitimate property 'host' to remain; schema=$schema",
        )
        Assertions.assertFalse(
            properties.has("additionalProperties"),
            "expected spurious 'additionalProperties' property to be stripped; schema=$schema",
        )

        val required = schema["required"] as ArrayNode
        val requiredValues = required.elements().asSequence().map { it.asText() }.toList()
        Assertions.assertTrue(
            "host" in requiredValues,
            "expected legitimate required entry 'host' to remain; required=$requiredValues",
        )
        Assertions.assertFalse(
            "additionalProperties" in requiredValues,
            "expected 'additionalProperties' to be absent from required; required=$requiredValues",
        )
    }

    @Test
    fun testSchemaWithoutAnyGetterIsUnchanged() {
        val schema =
            ValidatedJsonUtils.generateAirbyteJsonSchema(SpecWithoutAnyGetter::class.java)
                as ObjectNode
        val properties = schema["properties"] as ObjectNode
        Assertions.assertTrue(properties.has("host"))
        Assertions.assertFalse(properties.has("additionalProperties"))
    }

    @JsonSchemaTitle("Spec With Any Getter")
    class SpecWithAnyGetter : ConfigurationSpecification() {
        @JsonProperty("host") lateinit var host: String

        @JsonIgnore var additionalPropertiesMap = mutableMapOf<String, Any>()

        @JsonAnyGetter fun getAdditionalProperties(): Map<String, Any> = additionalPropertiesMap

        @JsonAnySetter
        fun setAdditionalProperty(
            name: String,
            value: Any,
        ) {
            additionalPropertiesMap[name] = value
        }
    }

    @JsonSchemaTitle("Spec Without Any Getter")
    class SpecWithoutAnyGetter : ConfigurationSpecification() {
        @JsonProperty("host") lateinit var host: String
    }
}
