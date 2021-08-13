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

package io.airbyte.integrations.destination.bigquery;

import com.google.cloud.bigquery.JobInfo.WriteDisposition;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.TableDataWriteChannel;
import com.google.cloud.bigquery.TableId;

class BigQueryWriteConfig {

  private final TableId table;
  private final TableId tmpTable;
  private final TableDataWriteChannel writer;
  private final WriteDisposition syncMode;
  private final Schema schema;

  BigQueryWriteConfig(TableId table, TableId tmpTable, TableDataWriteChannel writer, WriteDisposition syncMode, Schema schema) {
    this.table = table;
    this.tmpTable = tmpTable;
    this.writer = writer;
    this.syncMode = syncMode;
    this.schema = schema;
  }

  public TableId getTable() {
    return table;
  }

  public TableId getTmpTable() {
    return tmpTable;
  }

  public TableDataWriteChannel getWriter() {
    return writer;
  }

  public WriteDisposition getSyncMode() {
    return syncMode;
  }

  public Schema getSchema() {
    return schema;
  }

}
