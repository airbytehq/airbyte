/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.integrations.source.mssql.MssqlQueryUtils.TableSizeInfo;
import io.airbyte.integrations.source.mssql.initialsync.MssqlInitialLoadHandler;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import org.junit.jupiter.api.Test;

public class MssqlInitialLoadHandlerTest {

  private static final long ONE_GB = 1_073_741_824;
  private static final long ONE_MB = 1_048_576;

  @Test
  void testInvalidOrNullTableSizeInfo() {
    final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair("table_name", "schema_name");
    assertEquals(MssqlInitialLoadHandler.calculateChunkSize(null, pair), 1_000_000L);
    final TableSizeInfo invalidRowLengthInfo = new TableSizeInfo(ONE_GB, 0L);
    assertEquals(MssqlInitialLoadHandler.calculateChunkSize(invalidRowLengthInfo, pair), 1_000_000L);
    final TableSizeInfo invalidTableSizeInfo = new TableSizeInfo(0L, 0L);
    assertEquals(MssqlInitialLoadHandler.calculateChunkSize(invalidTableSizeInfo, pair), 1_000_000L);
  }

  @Test
  void testTableSizeInfo() {
    final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair("table_name", "schema_name");
    assertEquals(MssqlInitialLoadHandler.calculateChunkSize(new TableSizeInfo(ONE_GB, 2 * ONE_MB), pair), 512L);
    assertEquals(MssqlInitialLoadHandler.calculateChunkSize(new TableSizeInfo(ONE_GB, 200L), pair), 5368709L);
  }

}
