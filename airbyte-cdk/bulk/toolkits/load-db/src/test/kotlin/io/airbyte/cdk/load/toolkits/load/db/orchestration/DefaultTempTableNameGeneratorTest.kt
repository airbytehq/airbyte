/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.load.db.orchestration

import io.airbyte.cdk.load.orchestration.db.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TableName
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class DefaultTempTableNameGeneratorTest {
    @Test
    fun testGenerateWithLongName() {
        val generator = DefaultTempTableNameGenerator(internalNamespace = "airbyte_internal")
        val tempTableName =
            generator.generate(
                TableName(
                    namespace = "averylongnamespacewithmanycharacters",
                    name = "similarlylongstreamnamewithlotsoftest",
                )
            )
        // namespace affixes are averylon and aracters
        // name affixes are similarl and tsoftest
        // sha256(averylongnamespacewithmanycharacters_raw__stream_similarlylongstreamnamewithlotsoftest_airbyte_tmp)
        // is 81e041292e119a43ceaa439325d86a24c12dfdcc1c41bb3973a46079cdbe6bb4,
        //   of which we take the first 32 chars (81e041292e119a43ceaa439325d86a24)
        assertEquals(
            TableName(
                "airbyte_internal",
                "averylonaracterssimilarltsoftest81e041292e119a43ceaa439325d86a24"
            ),
            tempTableName,
        )
    }

    @Test
    fun testGenerateWithShortName() {
        val generator = DefaultTempTableNameGenerator(internalNamespace = "airbyte_internal")
        val tempTableName =
            generator.generate(
                TableName(
                    namespace = "a",
                    name = "1",
                )
            )
        // name and namespace are unchanged
        // sha256(a_raw__stream_1_airbyte_tmp) is
        //   b0b9f815c588c797c6616a082f6f2c5862bea54fff8b8c914e3310f4bba57052,
        //   of which we take the first 32 chars (b0b9f815c588c797c6616a082f6f2c58)
        assertEquals(
            TableName("airbyte_internal", "a1b0b9f815c588c797c6616a082f6f2c58"),
            tempTableName,
        )
    }
}
