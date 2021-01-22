/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.base;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.StandardNameTransformer;
import org.junit.jupiter.api.Test;

class NameTransformerTest {

  @Test
  void testStandardSQLNaming() {
    final NamingConventionTransformer namingResolver = new StandardNameTransformer();
    assertEquals("identifier_name", namingResolver.getIdentifier("identifier_name"));
    assertEquals("iDenTiFieR_name", namingResolver.getIdentifier("iDenTiFieR_name"));
    assertEquals("__identifier_name", namingResolver.getIdentifier("__identifier_name"));
    assertEquals("IDENTIFIER_NAME", namingResolver.getIdentifier("IDENTIFIER_NAME"));
    assertEquals("123identifier_name", namingResolver.getIdentifier("123identifier_name"));
    assertEquals("i0d0e0n0t0i0f0i0e0r0n0a0m0e", namingResolver.getIdentifier("i0d0e0n0t0i0f0i0e0r0n0a0m0e"));
    assertEquals("_identifier_name", namingResolver.getIdentifier(",identifier+name"));
    assertEquals("identifier_name", namingResolver.getIdentifier("identifiêr name"));
    assertEquals("a_unicode_name__", namingResolver.getIdentifier("a_unicode_name_文"));
    assertEquals("identifier__name__", namingResolver.getIdentifier("identifier__name__"));
    assertEquals("identifier_name_weee", namingResolver.getIdentifier("identifier-name.weee"));
    assertEquals("_identifier_name_", namingResolver.getIdentifier("\"identifier name\""));
    assertEquals("identifier_name", namingResolver.getIdentifier("identifier name"));
    assertEquals("identifier_", namingResolver.getIdentifier("identifier%"));
    assertEquals("_identifier_", namingResolver.getIdentifier("`identifier`"));

    assertEquals("_airbyte_raw_identifier_name", namingResolver.getRawTableName("identifier_name"));
  }

  // Temporarily disabling the behavior of the ExtendedNameTransformer, see (issue #1785)
  // @Test
  void testExtendedSQLNaming() {
    final NamingConventionTransformer namingResolver = new ExtendedNameTransformer();
    assertEquals("identifier_name", namingResolver.getIdentifier("identifier_name"));
    assertEquals("iDenTiFieR_name", namingResolver.getIdentifier("iDenTiFieR_name"));
    assertEquals("__identifier_name", namingResolver.getIdentifier("__identifier_name"));
    assertEquals("IDENTIFIER_NAME", namingResolver.getIdentifier("IDENTIFIER_NAME"));
    assertEquals("\"123identifier_name\"", namingResolver.getIdentifier("123identifier_name"));
    assertEquals("i0d0e0n0t0i0f0i0e0r0n0a0m0e", namingResolver.getIdentifier("i0d0e0n0t0i0f0i0e0r0n0a0m0e"));
    assertEquals("\",identifier+name\"", namingResolver.getIdentifier(",identifier+name"));
    assertEquals("\"identifiêr name\"", namingResolver.getIdentifier("identifiêr name"));
    assertEquals("\"a_unicode_name_文\"", namingResolver.getIdentifier("a_unicode_name_文"));
    assertEquals("identifier__name__", namingResolver.getIdentifier("identifier__name__"));
    assertEquals("\"identifier-name.weee\"", namingResolver.getIdentifier("identifier-name.weee"));
    assertEquals("\"\"identifier name\"\"", namingResolver.getIdentifier("\"identifier name\""));
    assertEquals("\"identifier name\"", namingResolver.getIdentifier("identifier name"));
    assertEquals("\"identifier%\"", namingResolver.getIdentifier("identifier%"));
    assertEquals("\"`identifier`\"", namingResolver.getIdentifier("`identifier`"));

    assertEquals("_airbyte_raw_identifier_name", namingResolver.getRawTableName("identifier_name"));
    assertEquals("\"_airbyte_raw_identifiêr name\"", namingResolver.getRawTableName("identifiêr name"));
  }

}
