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

package io.airbyte.integrations.destination.mysql;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class MySQLNameTransformerTest {

  private static final MySQLNameTransformer NAME_TRANSFORMER = new MySQLNameTransformer();
  private static final String LONG_NAME = "very_very_very_long_name_that_exceeds_the_max_mysql_identifier_size";

  @Test
  public void testGetIdentifier() {
    assertEquals(
        "very_very_very_long_n__mysql_identifier_size",
        NAME_TRANSFORMER.getIdentifier(LONG_NAME));
  }

  @Test
  public void testGetTmpTableName() {
    String tmpTableName = NAME_TRANSFORMER.getTmpTableName(LONG_NAME);
    assertEquals(MySQLNameTransformer.TRUNCATION_MAX_NAME_LENGTH, tmpTableName.length());
    // temp table name: _airbyte_tmp_xxx_very__mysql_identifier_size
    assertTrue(tmpTableName.startsWith("_airbyte_tmp_"));
    assertTrue(tmpTableName.endsWith("_very__mysql_identifier_size"));
  }

  @Test
  public void testGetRawTableName() {
    assertEquals(
        "_airbyte_raw_very_ver__mysql_identifier_size",
        NAME_TRANSFORMER.getRawTableName(LONG_NAME));
  }

  @Test
  public void getTruncateName() {
    assertEquals("1234567890", MySQLNameTransformer.truncateName("1234567890", 15));
    assertEquals("123__890", MySQLNameTransformer.truncateName("1234567890", 8));
  }

}
