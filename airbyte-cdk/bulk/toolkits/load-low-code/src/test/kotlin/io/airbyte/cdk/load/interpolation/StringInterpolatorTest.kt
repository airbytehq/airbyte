/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.interpolation

import io.airbyte.cdk.util.Jsons
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

class StringInterpolatorTest {

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

    @Test
    internal fun `test given bracket accessor on record when extract record keys then return key`() {
        val template = """{{ record["a_key"] }}"""
        val extractedKeys = StringInterpolator().extractAccessedRecordKeys(template)
        assertEquals(setOf("a_key"), extractedKeys)
    }

    @Test
    internal fun `test given get accessor on record when extract record keys then return key`() {
        val template = """{{ record.get("a_key") }}"""
        val extractedKeys = StringInterpolator().extractAccessedRecordKeys(template)
        assertEquals(setOf("a_key"), extractedKeys)
    }

    @Test
    internal fun `test given object name ends with record when extract record keys then return key`() {
        // This behavior is tested to show the potential problems with the solutions. See comment on
        // bracketAccessorRegex to understand why this is acceptable.
        val template = """{{ not_a_record.get("a_key") }}"""
        val extractedKeys = StringInterpolator().extractAccessedRecordKeys(template)
        assertEquals(setOf("a_key"), extractedKeys)
    }

    @Test
    internal fun `test given accessor on other object than record when extract record keys then return empty set`() {
        val template = """{{ response["a_key"] }}"""
        val extractedKeys = StringInterpolator().extractAccessedRecordKeys(template)
        assertEquals(setOf(), extractedKeys)
    }

    @Test
    internal fun `test given record key with text around it when extract record keys then return all the keys`() {
        val template = """This is some text {{ record["a_key"] }} there is even text after"""
        val extractedKeys = StringInterpolator().extractAccessedRecordKeys(template)
        assertEquals(setOf("a_key"), extractedKeys)
    }

    @Test
    internal fun `test given multiple keys in different nodes when extract record keys then return all the keys`() {
        val template = """{{ record["prefix"] }} I'm a potato: {{ record["suffix"] }}"""
        val extractedKeys = StringInterpolator().extractAccessedRecordKeys(template)
        assertEquals(setOf("prefix", "suffix"), extractedKeys)
    }

    @Test
    internal fun `test given multiple keys in the same node when extract record keys then return all the keys`() {
        val template = """{{ record["prefix"] + " I'm a potato: " + {{ record["suffix"] }}"""
        val extractedKeys = StringInterpolator().extractAccessedRecordKeys(template)
        assertEquals(setOf("prefix", "suffix"), extractedKeys)
    }

    @Test
    internal fun `test given invalid string interpolation when extract record keys then return empty set`() {
        // This happens because Jinja does not identify this string as an expression and therefore
        // it is filtered out
        val template = """{{ record["prefix"] other text "] }}"""
        val extractedKeys = StringInterpolator().extractAccessedRecordKeys(template)
        assertEquals(emptySet(), extractedKeys)
    }

}
