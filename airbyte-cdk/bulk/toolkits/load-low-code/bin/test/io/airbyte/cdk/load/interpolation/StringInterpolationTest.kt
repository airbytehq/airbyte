/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.interpolation

import io.airbyte.cdk.util.Jsons
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

class StringInterpolationTest {

    @Test
    internal fun `test given string without interpolation when eval then return same string`() {
        val string = "this is a string"
        val interpolatedValue = StringInterpolator().interpolate(string, emptyMap())
        assertEquals(string, interpolatedValue)
    }

    @Test
    internal fun `test given if statement true when eval then return proper value`() {
        val interpolatedValue =
            StringInterpolator()
                .interpolate(
                    "{{ first == second ? 'true' : 'false' }}",
                    mapOf("first" to 1, "second" to 1)
                )
        assertEquals("true", interpolatedValue)
    }

    @Test
    internal fun `test given if statement false when eval then return proper value`() {
        val interpolatedValue =
            StringInterpolator()
                .interpolate(
                    "{{ 'true' if first == second else 'false' }}",
                    mapOf("first" to 1, "second" to 2)
                )
        assertEquals("false", interpolatedValue)
    }

    @Test
    internal fun `test given string interpolation when eval then insert variable into string`() {
        val interpolatedValue =
            StringInterpolator()
                .interpolate(
                    "{{protocol}}://login.salesforce.com/auth",
                    mapOf("protocol" to "https")
                )
        assertEquals("https://login.salesforce.com/auth", interpolatedValue)
    }

    @Test
    internal fun `test given string interpolation with condition true when eval then evaluate condition`() {
        val interpolatedValue =
            StringInterpolator()
                .interpolate(
                    "https://{{ 'sandbox' if isSandbox else 'login'}}.salesforce.com/auth",
                    mapOf("isSandbox" to true)
                )
        assertEquals("https://sandbox.salesforce.com/auth", interpolatedValue)
    }

    @Test
    internal fun `test given string interpolation with condition false when eval then evaluate condition`() {
        val interpolatedValue =
            StringInterpolator()
                .interpolate(
                    "https://{{ 'sandbox' if isSandbox else 'login'}}.salesforce.com/auth",
                    mapOf("isSandbox" to false)
                )
        assertEquals("https://login.salesforce.com/auth", interpolatedValue)
    }

    @Test
    internal fun `test given ObjectNode when eval then extract values from ObjectNode`() {
        val objectNode =
            Jsons.readTree("""{"modificationMetadata": {"readOnlyValue": "readonly"}}""")

        val interpolatedValue =
            StringInterpolator()
                .interpolate(
                    """{{ response.get("modificationMetadata").get("readOnlyValue") }}""",
                    mapOf("response" to objectNode.toInterpolationContext())
                )
        assertEquals("readonly", interpolatedValue)
    }

    @Test
    internal fun `test given ObjectNode with get accessor when eval then return value`() {
        val objectNode =
            Jsons.readTree("""{"modificationMetadata": {"readOnlyValue": "readonly"}}""")

        val interpolatedValue =
            StringInterpolator()
                .interpolate(
                    """{{ response["modificationMetadata"]["readOnlyValue"] }}""",
                    mapOf("response" to objectNode.toInterpolationContext())
                )
        assertEquals("readonly", interpolatedValue)
    }

    @Test
    internal fun `test given ObjectNode with condition when eval then compare the value of the node and not the node itself`() {
        val objectNode =
            Jsons.readTree("""{"modificationMetadata": {"readOnlyValue": "readonly"}}""")

        val interpolatedValue =
            StringInterpolator()
                .interpolate(
                    """{{ response["modificationMetadata"]["readOnlyValue"] == "readonly" }}""",
                    mapOf("response" to objectNode.toInterpolationContext())
                )
        assertEquals("true", interpolatedValue)
    }
}
