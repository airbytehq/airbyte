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

  public static StandardSync generateSyncWithSourceImplId(UUID sourceImplementationId) {
    final UUID connectionId = UUID.randomUUID();

    return new StandardSync()
        .withConnectionId(connectionId)
        .withName("presto to hudi")
        .withStatus(StandardSync.Status.ACTIVE)
        .withSchema(generateBasicPersistenceSchema())
        .withSourceImplementationId(sourceImplementationId)
        .withDestinationImplementationId(UUID.randomUUID())
        .withSyncMode(StandardSync.SyncMode.FULL_REFRESH);
  }

  public static StandardSync generateSyncWithDestinationImplId(UUID destinationImplementationId) {
    final UUID connectionId = UUID.randomUUID();

    return new StandardSync()
        .withConnectionId(connectionId)
        .withName("presto to hudi")
        .withStatus(StandardSync.Status.ACTIVE)
        .withSchema(generateBasicPersistenceSchema())
        .withSourceImplementationId(UUID.randomUUID())
        .withDestinationImplementationId(destinationImplementationId)
        .withSyncMode(StandardSync.SyncMode.FULL_REFRESH);
  }

  public static Schema generateBasicPersistenceSchema() {
    final Column column = new Column()
        .withDataType(DataType.STRING)
        .withName("id")
        .withSelected(true);

    final Table table = new Table()
        .withName("users")
        .withColumns(Lists.newArrayList(column))
        .withSelected(true);

    return new Schema()
        .withTables(Lists.newArrayList(table));
  }

  public static SourceSchema generateBasicApiSchema() {
    final SourceSchemaColumn column = new SourceSchemaColumn()
        .dataType(io.dataline.api.model.DataType.STRING)
        .name("id")
        .selected(true);

    final SourceSchemaTable table = new SourceSchemaTable()
        .name("users")
        .columns(Lists.newArrayList(column));

    return new SourceSchema().tables(Lists.newArrayList(table));
  }

  public static ConnectionSchedule generateBasicSchedule() {
    return new ConnectionSchedule()
        .timeUnit(ConnectionSchedule.TimeUnitEnum.DAYS)
        .units(1L);
  }

  public static ConnectionRead generateExpectedConnectionRead(UUID connectionId,
                                                              UUID sourceImplementationId,
                                                              UUID destinationImplementationId) {

    return new ConnectionRead()
        .connectionId(connectionId)
        .sourceImplementationId(sourceImplementationId)
        .destinationImplementationId(destinationImplementationId)
        .name("presto to hudi")
        .status(ConnectionStatus.ACTIVE)
        .syncMode(ConnectionRead.SyncModeEnum.FULL_REFRESH)
        .schedule(generateBasicSchedule())
        .syncSchema(ConnectionHelpers.generateBasicApiSchema());
  }

  public static ConnectionRead generateExpectedConnectionRead(StandardSync standardSync) {
    return generateExpectedConnectionRead(
        standardSync.getConnectionId(),
        standardSync.getSourceImplementationId(),
        standardSync.getDestinationImplementationId());
  }

  public static StandardSyncSchedule generateSchedule(UUID connectionId) {
    final Schedule schedule = new Schedule()
        .withTimeUnit(Schedule.TimeUnit.DAYS)
        .withUnits(1L);

    return new StandardSyncSchedule()
        .withConnectionId(connectionId)
        .withSchedule(schedule)
        .withManual(false);
  }

}
