/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base

import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class NameTransformerTest {
    @Test
    fun testStandardSQLNaming() {
        val namingResolver: NamingConventionTransformer = StandardNameTransformer()
        Assertions.assertEquals("identifier_name", namingResolver.getIdentifier("identifier_name"))
        Assertions.assertEquals("iDenTiFieR_name", namingResolver.getIdentifier("iDenTiFieR_name"))
        Assertions.assertEquals(
            "__identifier_name",
            namingResolver.getIdentifier("__identifier_name")
        )
        Assertions.assertEquals("IDENTIFIER_NAME", namingResolver.getIdentifier("IDENTIFIER_NAME"))
        Assertions.assertEquals(
            "123identifier_name",
            namingResolver.getIdentifier("123identifier_name")
        )
        Assertions.assertEquals(
            "i0d0e0n0t0i0f0i0e0r0n0a0m0e",
            namingResolver.getIdentifier("i0d0e0n0t0i0f0i0e0r0n0a0m0e")
        )
        Assertions.assertEquals(
            "_identifier_name",
            namingResolver.getIdentifier(",identifier+name")
        )
        Assertions.assertEquals("identifier_name", namingResolver.getIdentifier("identifiêr name"))
        Assertions.assertEquals(
            "a_unicode_name__",
            namingResolver.getIdentifier("a_unicode_name_文")
        )
        Assertions.assertEquals(
            "identifier__name__",
            namingResolver.getIdentifier("identifier__name__")
        )
        Assertions.assertEquals(
            "identifier_name_weee",
            namingResolver.getIdentifier("identifier-name.weee")
        )
        Assertions.assertEquals(
            "_identifier_name_",
            namingResolver.getIdentifier("\"identifier name\"")
        )
        Assertions.assertEquals("identifier_name", namingResolver.getIdentifier("identifier name"))
        Assertions.assertEquals("identifier_", namingResolver.getIdentifier("identifier%"))
        Assertions.assertEquals("_identifier_", namingResolver.getIdentifier("`identifier`"))

        Assertions.assertEquals(
            "_airbyte_raw_identifier_name",
            namingResolver.getRawTableName("identifier_name")
        )
    }

    // Temporarily disabling the behavior of the StandardNameTransformer, see (issue #1785)
    // @Test
    fun testExtendedSQLNaming() {
        val namingResolver: NamingConventionTransformer = StandardNameTransformer()
        Assertions.assertEquals("identifier_name", namingResolver.getIdentifier("identifier_name"))
        Assertions.assertEquals("iDenTiFieR_name", namingResolver.getIdentifier("iDenTiFieR_name"))
        Assertions.assertEquals(
            "__identifier_name",
            namingResolver.getIdentifier("__identifier_name")
        )
        Assertions.assertEquals("IDENTIFIER_NAME", namingResolver.getIdentifier("IDENTIFIER_NAME"))
        Assertions.assertEquals(
            "\"123identifier_name\"",
            namingResolver.getIdentifier("123identifier_name")
        )
        Assertions.assertEquals(
            "i0d0e0n0t0i0f0i0e0r0n0a0m0e",
            namingResolver.getIdentifier("i0d0e0n0t0i0f0i0e0r0n0a0m0e")
        )
        Assertions.assertEquals(
            "\",identifier+name\"",
            namingResolver.getIdentifier(",identifier+name")
        )
        Assertions.assertEquals(
            "\"identifiêr name\"",
            namingResolver.getIdentifier("identifiêr name")
        )
        Assertions.assertEquals(
            "\"a_unicode_name_文\"",
            namingResolver.getIdentifier("a_unicode_name_文")
        )
        Assertions.assertEquals(
            "identifier__name__",
            namingResolver.getIdentifier("identifier__name__")
        )
        Assertions.assertEquals(
            "\"identifier-name.weee\"",
            namingResolver.getIdentifier("identifier-name.weee")
        )
        Assertions.assertEquals(
            "\"\"identifier name\"\"",
            namingResolver.getIdentifier("\"identifier name\"")
        )
        Assertions.assertEquals(
            "\"identifier name\"",
            namingResolver.getIdentifier("identifier name")
        )
        Assertions.assertEquals("\"identifier%\"", namingResolver.getIdentifier("identifier%"))
        Assertions.assertEquals("\"`identifier`\"", namingResolver.getIdentifier("`identifier`"))

        Assertions.assertEquals(
            "_airbyte_raw_identifier_name",
            namingResolver.getRawTableName("identifier_name")
        )
        Assertions.assertEquals(
            "\"_airbyte_raw_identifiêr name\"",
            namingResolver.getRawTableName("identifiêr name")
        )
    }
}
