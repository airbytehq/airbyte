/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.mysql

import io.airbyte.integrations.destination.mysql.MySQLNameTransformer.Companion.truncateName
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class MySQLNameTransformerTest {
    @Test
    fun testGetIdentifier() {
        Assertions.assertEquals(
            "very_very_very_long_n__mysql_identifier_size",
            NAME_TRANSFORMER.getIdentifier(LONG_NAME)
        )
    }

    @Test
    fun testGetTmpTableName() {
        val tmpTableName = NAME_TRANSFORMER.getTmpTableName(LONG_NAME)
        Assertions.assertEquals(
            MySQLNameTransformer.TRUNCATION_MAX_NAME_LENGTH,
            tmpTableName.length
        )
        // temp table name: _airbyte_tmp_xxx_very__mysql_identifier_size
        Assertions.assertTrue(tmpTableName.startsWith("_airbyte_tmp_"))
        Assertions.assertTrue(tmpTableName.endsWith("_very__mysql_identifier_size"))
    }

    @Test
    fun testGetRawTableName() {
        Assertions.assertEquals(
            "_airbyte_raw_very_ver__mysql_identifier_size",
            NAME_TRANSFORMER.getRawTableName(LONG_NAME)
        )
    }

    @get:Test
    val truncateName: Unit
        get() {
            Assertions.assertEquals("1234567890", truncateName("1234567890", 15))
            Assertions.assertEquals("123__890", truncateName("1234567890", 8))
        }

    companion object {
        private val NAME_TRANSFORMER = MySQLNameTransformer()
        private const val LONG_NAME =
            "very_very_very_long_name_that_exceeds_the_max_mysql_identifier_size"
    }
}
