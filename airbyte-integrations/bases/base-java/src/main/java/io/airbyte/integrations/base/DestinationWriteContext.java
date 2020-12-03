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

import io.airbyte.protocol.models.SyncMode;

/**
 * This configuration is used by the RecordConsumers to adapt their behavior at runtime such as
 * where to apply their task and the kind of data operations
 */
public class DestinationWriteContext {

  private final String outputNamespaceName;
  private final String outputTableName;
  private final SyncMode syncMode;

  DestinationWriteContext(String outputNamespaceName, String outputTableName, SyncMode syncMode) {
    this.outputNamespaceName = outputNamespaceName;
    this.outputTableName = outputTableName;
    this.syncMode = syncMode;
  }

  public String getOutputNamespaceName() {
    return outputNamespaceName;
  }

  public String getOutputTableName() {
    return outputTableName;
  }

  public SyncMode getSyncMode() {
    return syncMode;
  }

}
