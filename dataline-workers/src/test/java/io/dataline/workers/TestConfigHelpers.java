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

import com.fasterxml.jackson.databind.JsonNode;
import io.dataline.commons.json.Jsons;
import io.dataline.config.Column;
import io.dataline.config.DataType;
import io.dataline.config.DestinationConnectionImplementation;
import io.dataline.config.Schema;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.StandardSync;
import io.dataline.config.StandardSyncInput;
import io.dataline.config.State;
import io.dataline.config.Table;
import java.util.Collections;
import java.util.Map;
import java.util.UUID;
import org.apache.commons.lang3.tuple.ImmutablePair;

public class TestConfigHelpers {

  private static final String CONNECTION_NAME = "favorite_color_pipe";
  private static final String TABLE_NAME = "user_preferences";
  private static final String COLUMN_NAME = "favorite_color";
  private static final long LAST_SYNC_TIME = 1598565106;

  public static ImmutablePair<StandardSync, StandardSyncInput> createSyncConfig() {
    final UUID workspaceId = UUID.randomUUID();
    final UUID sourceSpecificationId = UUID.randomUUID();
    final UUID sourceImplementationId = UUID.randomUUID();
    final UUID destinationSpecificationId = UUID.randomUUID();
    final UUID destinationImplementationId = UUID.randomUUID();
    final UUID connectionId = UUID.randomUUID();

    final JsonNode sourceConnection =
        Jsons.jsonNode(
            Map.of(
                "apiKey", "123",
                "region", "us-east"));

    final JsonNode destinationConnection =
        Jsons.jsonNode(
            Map.of(
                "username", "dataline",
                "token", "anau81b"));

    final SourceConnectionImplementation sourceConnectionConfig = new SourceConnectionImplementation()
        .withConfiguration(sourceConnection)
        .withWorkspaceId(workspaceId)
        .withSourceSpecificationId(sourceSpecificationId)
        .withSourceImplementationId(sourceImplementationId)
        .withTombstone(false);

    final DestinationConnectionImplementation destinationConnectionConfig = new DestinationConnectionImplementation()
        .withConfiguration(destinationConnection)
        .withWorkspaceId(workspaceId)
        .withDestinationSpecificationId(destinationSpecificationId)
        .withDestinationImplementationId(destinationImplementationId);

    final Column column = new Column()
        .withName(COLUMN_NAME)
        .withDataType(DataType.STRING)
        .withSelected(true);

    final Table table = new Table()
        .withName(TABLE_NAME)
        .withSelected(true)
        .withColumns(Collections.singletonList(column));

    final Schema schema = new Schema().withTables(Collections.singletonList(table));

    StandardSync standardSync = new StandardSync()
        .withConnectionId(connectionId)
        .withDestinationImplementationId(destinationImplementationId)
        .withSourceImplementationId(sourceImplementationId)
        .withStatus(StandardSync.Status.ACTIVE)
        .withSyncMode(StandardSync.SyncMode.APPEND)
        .withName(CONNECTION_NAME)
        .withSchema(schema);

    final String stateValue = Jsons.serialize(Map.of("lastSync", String.valueOf(LAST_SYNC_TIME)));

    State state = new State()
        .withConnectionId(connectionId)
        .withState(Jsons.jsonNode(stateValue));

    StandardSyncInput syncInput = new StandardSyncInput()
        .withDestinationConnectionImplementation(destinationConnectionConfig)
        .withStandardSync(standardSync)
        .withSourceConnectionImplementation(sourceConnectionConfig)
        .withState(state);

    return new ImmutablePair<>(standardSync, syncInput);
  }

}
