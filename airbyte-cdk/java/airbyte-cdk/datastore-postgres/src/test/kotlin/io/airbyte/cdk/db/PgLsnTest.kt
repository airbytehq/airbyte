/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db

import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.db.PgLsn.Companion.fromLong
import io.airbyte.cdk.db.PgLsn.Companion.longToLsn
import io.airbyte.cdk.db.PgLsn.Companion.lsnToLong
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class PgLsnTest {
    @Test
    fun testLsnToLong() {
        TEST_LSNS.forEach { (key: String?, value: Long?) ->
            Assertions.assertEquals(
                value,
                lsnToLong(key),
                String.format("Conversion failed. lsn: %s long value: %s", key, value)
            )
        }
    }

    @Test
    fun testLongToLsn() {
        TEST_LSNS.forEach { (key: String?, value: Long?) ->
            Assertions.assertEquals(
                key,
                longToLsn(value),
                String.format("Conversion failed. lsn: %s long value: %s", key, value)
            )
        }
    }

    // Added Test Case to test .toString() method in PgLsn.java
    @Test
    fun testLsnToString() {
        EXPECTED_TEST_LSNS.forEach { (key: String?, value: Long?) ->
            Assertions.assertEquals(
                key,
                fromLong(value).toString(),
                String.format("Conversion failed. string: %s lsn: %s", key, value)
            )
        }
    }

    companion object {
        private val TEST_LSNS: Map<String, Long> =
            ImmutableMap.builder<String, Long>()
                .put("0/15E7A10", 22968848L)
                .put("0/15E7B08", 22969096L)
                .put("16/15E7B08", 94512249608L)
                .put("16/FFFFFFFF", 98784247807L)
                .put("7FFFFFFF/FFFFFFFF", Long.MAX_VALUE)
                .put("0/0", 0L)
                .build()

        // Example Map used to run test case.
        private val EXPECTED_TEST_LSNS: Map<String, Long> =
            ImmutableMap.builder<String, Long>()
                .put("PgLsn{lsn=22968848}", 22968848L)
                .put("PgLsn{lsn=22969096}", 22969096L)
                .put("PgLsn{lsn=94512249608}", 94512249608L)
                .put("PgLsn{lsn=98784247807}", 98784247807L)
                .put("PgLsn{lsn=9223372036854775807}", Long.MAX_VALUE)
                .put("PgLsn{lsn=0}", 0L)
                .build()
    }
}
