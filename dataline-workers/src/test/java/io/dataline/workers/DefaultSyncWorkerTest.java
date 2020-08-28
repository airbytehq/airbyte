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

package io.dataline.workers;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.dataline.commons.functional.CloseableConsumer;
import io.dataline.commons.json.JsonUtils;
import io.dataline.config.Column;
import io.dataline.config.DataType;
import io.dataline.config.DestinationConnectionImplementation;
import io.dataline.config.Schema;
import io.dataline.config.SingerMessage;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.StandardSync;
import io.dataline.config.StandardSyncInput;
import io.dataline.config.StandardSyncSummary;
import io.dataline.config.StandardTapConfig;
import io.dataline.config.StandardTargetConfig;
import io.dataline.config.State;
import io.dataline.config.Table;
import io.dataline.workers.protocol.singer.MessageUtils;
import java.nio.file.Path;
import java.util.Collections;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;

class DefaultSyncWorkerTest extends BaseWorkerTestCase {
  private static final Path WORKSPACE_ROOT = Path.of("/workspaces/10");
  private static final String TABLE_NAME = "user_preferences";
  private static final String COLUMN_NAME = "favorite_color";
  private static final long LAST_SYNC_TIME = 1598565106;
  private static final UUID WORKSPACE_ID = UUID.randomUUID();
  private static final UUID SOURCE_SPECIFICATION_ID = UUID.randomUUID();
  private static final UUID SOURCE_IMPLEMENTATION_ID = UUID.randomUUID();
  private static final UUID DESTINATION_SPECIFICATION_ID = UUID.randomUUID();
  private static final UUID DESTINATION_IMPLEMENTATION_ID = UUID.randomUUID();

  @SuppressWarnings("unchecked")
  @Test
  public void test() throws Exception {
    final String sourceConnection =
        JsonUtils.toJson(
            Map.of(
                "apiKey", "123",
                "region", "us-east"));

    final String destinationConnection =
        JsonUtils.toJson(
            Map.of(
                "username", "dataline",
                "token", "anau81b"));

    final SourceConnectionImplementation sourceConnectionConfig =
        new SourceConnectionImplementation();
    sourceConnectionConfig.setConfiguration(sourceConnection);
    sourceConnectionConfig.setWorkspaceId(WORKSPACE_ID);
    sourceConnectionConfig.setSourceSpecificationId(SOURCE_SPECIFICATION_ID);
    sourceConnectionConfig.setSourceImplementationId(SOURCE_IMPLEMENTATION_ID);
    sourceConnectionConfig.setTombstone(false);

    final DestinationConnectionImplementation destinationConnectionConfig =
        new DestinationConnectionImplementation();
    destinationConnectionConfig.setConfiguration(destinationConnection);
    destinationConnectionConfig.setWorkspaceId(WORKSPACE_ID);
    destinationConnectionConfig.setDestinationSpecificationId(DESTINATION_SPECIFICATION_ID);
    destinationConnectionConfig.setDestinationImplementationId(DESTINATION_IMPLEMENTATION_ID);

    final Column column = new Column();
    column.setName(COLUMN_NAME);
    column.setDataType(DataType.STRING);
    column.setSelected(true);

    final Table table = new Table();
    table.setName(TABLE_NAME);
    table.setSelected(true);
    table.setColumns(Collections.singletonList(column));

    final Schema schema = new Schema();
    schema.setTables(Collections.singletonList(table));

    final UUID connectionId = UUID.randomUUID();
    StandardSync standardSync = new StandardSync();
    standardSync.setConnectionId(connectionId);
    standardSync.setDestinationImplementationId(DESTINATION_IMPLEMENTATION_ID);
    standardSync.setSourceImplementationId(SOURCE_IMPLEMENTATION_ID);
    standardSync.setStatus(StandardSync.Status.ACTIVE);
    standardSync.setSyncMode(StandardSync.SyncMode.APPEND);
    standardSync.setName("favorite_color_pipe");
    standardSync.setSchema(schema);

    final String stateValue = JsonUtils.toJson(Map.of("lastSync", String.valueOf(LAST_SYNC_TIME)));

    State state = new State();
    state.setConnectionId(connectionId);
    state.setState(stateValue);

    final StandardSyncSummary syncSummary = new StandardSyncSummary();
    syncSummary.setStatus(StandardSyncSummary.Status.COMPLETED);
    syncSummary.setRecordsSynced(10L);
    syncSummary.setStartTime(LAST_SYNC_TIME);
    syncSummary.setEndTime(LAST_SYNC_TIME);

    final StandardTapConfig tapConfig = new StandardTapConfig();
    tapConfig.setStandardSync(standardSync);
    tapConfig.setSourceConnectionImplementation(sourceConnectionConfig);
    tapConfig.setState(state);

    final StandardTargetConfig targetConfig = new StandardTargetConfig();
    targetConfig.setStandardSync(standardSync);
    targetConfig.setDestinationConnectionImplementation(destinationConnectionConfig);

    StandardSyncInput syncInput = new StandardSyncInput();
    syncInput.setDestinationConnectionImplementation(destinationConnectionConfig);
    syncInput.setStandardSync(standardSync);
    syncInput.setSourceConnectionImplementation(sourceConnectionConfig);
    syncInput.setState(state);

    final TapFactory<SingerMessage> tapFactory = (TapFactory<SingerMessage>) mock(TapFactory.class);
    final TargetFactory<SingerMessage> targetFactory =
        (TargetFactory<SingerMessage>) mock(TargetFactory.class);
    final CloseableConsumer<SingerMessage> consumer =
        (CloseableConsumer<SingerMessage>) mock(CloseableConsumer.class);

    SingerMessage recordMessage1 =
        MessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "blue");
    SingerMessage recordMessage2 =
        MessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "yellow");
    final Stream<SingerMessage> tapStream = Stream.of(recordMessage1, recordMessage2);

    when(tapFactory.create(tapConfig, WORKSPACE_ROOT)).thenReturn(tapStream);
    when(targetFactory.create(targetConfig, WORKSPACE_ROOT)).thenReturn(consumer);
    final DefaultSyncWorker defaultSyncWorker = new DefaultSyncWorker(tapFactory, targetFactory);

    defaultSyncWorker.run(syncInput, WORKSPACE_ROOT);

    verify(tapFactory).create(tapConfig, WORKSPACE_ROOT);
    verify(targetFactory).create(targetConfig, WORKSPACE_ROOT);
    verify(consumer).accept(recordMessage1);
    verify(consumer).accept(recordMessage2);
    verify(consumer).close();
  }
}
