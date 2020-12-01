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

import io.airbyte.commons.lang.CloseableQueue;
import io.airbyte.protocol.models.SyncMode;

/**
 * Associate a Stream Buffer with informations on where and how this data should be written while
 * buffering or when reaching end of streams.
 */
public class BufferedWriteConfig {

  private final String schemaName;
  private final String tableName;
  private final String tmpTableName;
  private final CloseableQueue<byte[]> writeBuffer;
  private final SyncMode syncMode;

  public BufferedWriteConfig(String schemaName, String tableName, String tmpTableName, CloseableQueue<byte[]> writeBuffer, SyncMode syncMode) {
    this.schemaName = schemaName;
    this.tableName = tableName;
    this.tmpTableName = tmpTableName;
    this.writeBuffer = writeBuffer;
    this.syncMode = syncMode;
  }

  public String getSchemaName() {
    return schemaName;
  }

  public String getTableName() {
    return tableName;
  }

  public String getTmpTableName() {
    return tmpTableName;
  }

  public CloseableQueue<byte[]> getWriteBuffer() {
    return writeBuffer;
  }

  public SyncMode getSyncMode() {
    return syncMode;
  }

}
