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

import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;

/**
 * Implementation of TmpToFinalTable in order to move data from a tmp destination to a final target.
 *
 * This implementation is geared towards databases using queries based on Truncate table & Insert
 * Into SQL statements. (The truncate operation is performed depending on the sync mode incremental
 * or not, in which case data is appended to the table when inserting)
 */
public class TruncateInsertIntoConsumer implements TmpToFinalTable {

  private final InsertTableOperations destination;
  private Map<String, DestinationCopyContext> copyConfigs;

  public TruncateInsertIntoConsumer(InsertTableOperations destination) {
    this.destination = destination;
    this.copyConfigs = new HashMap<>();
  }

  @Override
  public void setContext(Map<String, DestinationCopyContext> configs) {
    copyConfigs = configs;
  }

  @Override
  public void execute() throws Exception {
    if (copyConfigs.isEmpty()) {
      throw new RuntimeException("copyConfigs is empty, did you setContext() beforehand?");
    }
    for (Entry<String, DestinationCopyContext> entry : copyConfigs.entrySet()) {
      final DestinationCopyContext config = entry.getValue();
      final String schemaName = config.getOutputNamespaceName();
      final String srcTableName = config.getInputTableName();
      final String dstTableName = config.getOutputTableName();

      destination.createDestinationTable(schemaName, dstTableName);
      switch (config.getSyncMode()) {
        case FULL_REFRESH -> destination.truncateTable(schemaName, dstTableName);
        case INCREMENTAL -> {}
        default -> throw new IllegalStateException("Unrecognized sync mode: " + config.getSyncMode());
      }
      destination.insertIntoFromSelect(schemaName, srcTableName, dstTableName);
    }
  }

}
