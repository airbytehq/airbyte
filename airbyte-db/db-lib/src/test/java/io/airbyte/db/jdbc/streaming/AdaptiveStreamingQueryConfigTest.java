/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc.streaming;

import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

import java.sql.ResultSet;
import java.sql.SQLException;
import joptsimple.internal.Strings;
import org.junit.jupiter.api.Test;

class AdaptiveStreamingQueryConfigTest {

  @Test
  void testFetchSizeUpdate() throws SQLException {
    final AdaptiveStreamingQueryConfig queryConfig = new AdaptiveStreamingQueryConfig();
    final ResultSet resultSet = mock(ResultSet.class);
    for (int i = 0; i < FetchSizeConstants.INITIAL_SAMPLE_SIZE - 1; ++i) {
      queryConfig.accept(resultSet, Strings.repeat(Character.forDigit(i, 10), i + 1));
      verify(resultSet, never()).setFetchSize(anyInt());
    }
    queryConfig.accept(resultSet, "final sampling in the initial stage");
    verify(resultSet, times(1)).setFetchSize(anyInt());
    queryConfig.accept(resultSet, "abcd");
  }

}
