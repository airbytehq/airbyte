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

package io.airbyte.integrations.destination.jdbc;

import io.airbyte.protocol.models.DestinationSyncMode;

/**
 * Write configuration POJO for all destinations extending {@link AbstractJdbcDestination}.
 */
public class WriteConfig {

  private final String streamName;

  private final String namespace;

  private final String outputSchemaName;
  private final String tmpTableName;
  private final String outputTableName;
  private final DestinationSyncMode syncMode;

  public WriteConfig(String streamName,
                     String namespace,
                     String outputSchemaName,
                     String tmpTableName,
                     String outputTableName,
                     DestinationSyncMode syncMode) {
    this.streamName = streamName;
    this.namespace = namespace;
    this.outputSchemaName = outputSchemaName;
    this.tmpTableName = tmpTableName;
    this.outputTableName = outputTableName;
    this.syncMode = syncMode;
  }

  public String getStreamName() {
    return streamName;
  }

  public String getNamespace() {
    return namespace;
  }

  public String getTmpTableName() {
    return tmpTableName;
  }

  public String getOutputSchemaName() {
    return outputSchemaName;
  }

  public String getOutputTableName() {
    return outputTableName;
  }

  public DestinationSyncMode getSyncMode() {
    return syncMode;
  }

  @Override
  public String toString() {
    return "WriteConfig{" +
        "streamName=" + streamName +
        ", namespace=" + namespace +
        ", outputSchemaName=" + outputSchemaName +
        ", tmpTableName=" + tmpTableName +
        ", outputTableName=" + outputTableName +
        ", syncMode=" + syncMode +
        '}';
  }

}
