/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.jdbc.streaming

import java.sql.ResultSet
import java.sql.SQLException
import joptsimple.internal.Strings
import org.junit.jupiter.api.Test
import org.mockito.ArgumentMatchers
import org.mockito.Mockito

internal class AdaptiveStreamingQueryConfigTest {
    @Test
    @Throws(SQLException::class)
    fun testFetchSizeUpdate() {
        val queryConfig = AdaptiveStreamingQueryConfig()
        val resultSet = Mockito.mock(ResultSet::class.java)
        for (i in 0 until FetchSizeConstants.INITIAL_SAMPLE_SIZE - 1) {
            queryConfig.accept(resultSet, Strings.repeat(Character.forDigit(i, 10), i + 1))
            Mockito.verify(resultSet, Mockito.never()).fetchSize = ArgumentMatchers.anyInt()
        }
        queryConfig.accept(resultSet, "final sampling in the initial stage")
        Mockito.verify(resultSet, Mockito.times(1)).fetchSize = ArgumentMatchers.anyInt()
        queryConfig.accept(resultSet, "abcd")
    }
}
