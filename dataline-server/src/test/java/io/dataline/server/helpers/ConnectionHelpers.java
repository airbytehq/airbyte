/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.server.helpers;

import com.google.common.collect.Lists;
import io.dataline.api.model.ConnectionRead;
import io.dataline.api.model.ConnectionSchedule;
import io.dataline.api.model.ConnectionStatus;
import io.dataline.api.model.SourceSchema;
import io.dataline.api.model.SourceSchemaColumn;
import io.dataline.api.model.SourceSchemaTable;
import io.dataline.config.Column;
import io.dataline.config.DataType;
import io.dataline.config.Schedule;
import io.dataline.config.Schema;
import io.dataline.config.StandardSync;
import io.dataline.config.StandardSyncSchedule;
import io.dataline.config.Table;
import java.util.UUID;

public class ConnectionHelpers {

  public static StandardSync generateSync(UUID sourceImplementationId) {
    final UUID connectionId = UUID.randomUUID();

    final StandardSync standardSync = new StandardSync();
    standardSync.setConnectionId(connectionId);
    standardSync.setName("presto to hudi");
    standardSync.setStatus(StandardSync.Status.ACTIVE);
    standardSync.setSchema(generateBasicPersistenceSchema());
    standardSync.setSourceImplementationId(sourceImplementationId);
    standardSync.setDestinationImplementationId(UUID.randomUUID());
    standardSync.setSyncMode(StandardSync.SyncMode.APPEND);

    return standardSync;
  }

  public static Schema generateBasicPersistenceSchema() {
    final Column column = new Column();
    column.setDataType(DataType.STRING);
    column.setName("id");
    column.setSelected(true);

    final Table table = new Table();
    table.setName("users");
    table.setColumns(Lists.newArrayList(column));
    table.setSelected(true);

    final Schema schema = new Schema();
    schema.setTables(Lists.newArrayList(table));

    return schema;
  }

  public static SourceSchema generateBasicApiSchema() {
    final SourceSchemaColumn column = new SourceSchemaColumn();
    column.setDataType(io.dataline.api.model.DataType.STRING);
    column.setName("id");
    column.setSelected(true);

    final SourceSchemaTable table = new SourceSchemaTable();
    table.setName("users");
    table.setColumns(Lists.newArrayList(column));

    final SourceSchema schema = new SourceSchema();
    schema.setTables(Lists.newArrayList(table));

    return schema;
  }

  public static ConnectionSchedule generateBasicSchedule() {
    final ConnectionSchedule connectionSchedule = new ConnectionSchedule();
    connectionSchedule.setTimeUnit(ConnectionSchedule.TimeUnitEnum.DAYS);
    connectionSchedule.setUnits(1L);

    return connectionSchedule;
  }

  public static ConnectionRead generateExpectedConnectionRead(
                                                              UUID connectionId,
                                                              UUID sourceImplementationId,
                                                              UUID destinationImplementationId) {
    final ConnectionRead expectedConnectionRead = new ConnectionRead();
    expectedConnectionRead.setConnectionId(connectionId);
    expectedConnectionRead.setSourceImplementationId(sourceImplementationId);
    expectedConnectionRead.setDestinationImplementationId(destinationImplementationId);
    expectedConnectionRead.setName("presto to hudi");
    expectedConnectionRead.setStatus(ConnectionStatus.ACTIVE);
    expectedConnectionRead.setSyncMode(ConnectionRead.SyncModeEnum.APPEND);
    expectedConnectionRead.setSchedule(generateBasicSchedule());
    expectedConnectionRead.setSyncSchema(ConnectionHelpers.generateBasicApiSchema());

    return expectedConnectionRead;
  }

  public static ConnectionRead generateExpectedConnectionRead(StandardSync standardSync) {
    return generateExpectedConnectionRead(
        standardSync.getConnectionId(),
        standardSync.getSourceImplementationId(),
        standardSync.getDestinationImplementationId());
  }

  public static StandardSyncSchedule generateSchedule(UUID connectionId) {
    final Schedule schedule = new Schedule();
    schedule.setTimeUnit(Schedule.TimeUnit.DAYS);
    schedule.setUnits(1L);

    final StandardSyncSchedule standardSchedule = new StandardSyncSchedule();
    standardSchedule.setConnectionId(connectionId);
    standardSchedule.setSchedule(schedule);
    standardSchedule.setManual(false);

    return standardSchedule;
  }

}
