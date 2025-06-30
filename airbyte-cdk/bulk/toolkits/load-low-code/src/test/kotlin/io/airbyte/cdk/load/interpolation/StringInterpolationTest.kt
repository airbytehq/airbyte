/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.interpolation

import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

class StringInterpolationTest {

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
                    "{{ first == second ? 'true' : 'false' }}",
                    mapOf("first" to 1, "second" to 2)
                )
        assertEquals("false", interpolatedValue)
    }

    @Test
    internal fun `test given string interpolation when eval then insert variable into string`() {
        val interpolatedValue =
            StringInterpolator()
                .interpolate(
                    "{{ \"#{protocol}://login.salesforce.com/auth\" }}",
                    mapOf("protocol" to "https")
                )
        assertEquals("https://login.salesforce.com/auth", interpolatedValue)
    }

    @Test
    internal fun `test given string interpolation with condition true when eval then evaluate condition`() {
        val interpolatedValue =
            StringInterpolator()
                .interpolate(
                    "{{ \"https://#{isSandbox ? 'sandbox' : 'login'}.salesforce.com/auth\" }}",
                    mapOf("isSandbox" to true)
                )
        assertEquals("https://sandbox.salesforce.com/auth", interpolatedValue)
    }

    @Test
    internal fun `test given string interpolation with condition false when eval then evaluate condition`() {
        val interpolatedValue =
            StringInterpolator()
                .interpolate(
                    "{{ \"https://#{isSandbox ? 'sandbox' : 'login'}.salesforce.com/auth\" }}",
                    mapOf("isSandbox" to false)
                )
        assertEquals("https://login.salesforce.com/auth", interpolatedValue)
    }
}
