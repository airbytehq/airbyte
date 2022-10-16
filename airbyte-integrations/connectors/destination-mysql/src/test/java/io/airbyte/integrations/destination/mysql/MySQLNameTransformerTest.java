/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
    final String tmpTableName = NAME_TRANSFORMER.getTmpTableName(LONG_NAME);
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
