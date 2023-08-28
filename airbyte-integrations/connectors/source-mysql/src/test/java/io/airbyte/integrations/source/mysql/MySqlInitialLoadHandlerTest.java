/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.integrations.source.mysql.MySqlQueryUtils.TableSizeInfo;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialLoadHandler;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import org.junit.jupiter.api.Test;

public class MySqlInitialLoadHandlerTest {

  private static final long ONE_GB = 1_073_741_824;
  private static final long ONE_MB = 1_048_576;

  @Test
  void testInvalidOrNullTableSizeInfo() {
    final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair("table_name", "schema_name");
    assertEquals(MySqlInitialLoadHandler.calculateChunkSize(null, pair), 1_000_000L);
    final TableSizeInfo invalidRowLengthInfo = new TableSizeInfo(ONE_GB, 0L);
    assertEquals(MySqlInitialLoadHandler.calculateChunkSize(invalidRowLengthInfo, pair), 1_000_000L);
    final TableSizeInfo invalidTableSizeInfo = new TableSizeInfo(0L, 0L);
    assertEquals(MySqlInitialLoadHandler.calculateChunkSize(invalidTableSizeInfo, pair), 1_000_000L);
  }

  @Test
  void testTableSizeInfo() {
    final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair("table_name", "schema_name");
    assertEquals(MySqlInitialLoadHandler.calculateChunkSize(new TableSizeInfo(ONE_GB, 2 * ONE_MB), pair), 512L);
    assertEquals(MySqlInitialLoadHandler.calculateChunkSize(new TableSizeInfo(ONE_GB, 200L), pair), 5368709L);
  }

}
