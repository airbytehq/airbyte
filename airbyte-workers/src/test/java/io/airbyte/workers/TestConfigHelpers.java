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

package io.airbyte.workers;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AirbyteProtocolConverters;
import io.airbyte.config.DataType;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.Field;
import io.airbyte.config.Schema;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.SyncMode;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.State;
import io.airbyte.config.Stream;
import java.util.Collections;
import java.util.Map;
import java.util.UUID;
import org.apache.commons.lang3.tuple.ImmutablePair;

public class TestConfigHelpers {

  private static final String CONNECTION_NAME = "favorite_color_pipe";
  private static final String STREAM_NAME = "user_preferences";
  private static final String FIELD_NAME = "favorite_color";
  private static final long LAST_SYNC_TIME = 1598565106;

  public static ImmutablePair<StandardSync, StandardSyncInput> createSyncConfig() {
    final UUID workspaceId = UUID.randomUUID();
    final UUID sourceDefinitionId = UUID.randomUUID();
    final UUID sourceId = UUID.randomUUID();
    final UUID destinationDefinitionId = UUID.randomUUID();
    final UUID destinationId = UUID.randomUUID();
    final UUID connectionId = UUID.randomUUID();

    final JsonNode sourceConnection =
        Jsons.jsonNode(
            Map.of(
                "apiKey", "123",
                "region", "us-east"));

    final JsonNode destinationConnection =
        Jsons.jsonNode(
            Map.of(
                "username", "airbyte",
                "token", "anau81b"));

    final SourceConnection sourceConnectionConfig = new SourceConnection()
        .withConfiguration(sourceConnection)
        .withWorkspaceId(workspaceId)
        .withSourceDefinitionId(sourceDefinitionId)
        .withSourceId(sourceId)
        .withTombstone(false);

    final DestinationConnection destinationConnectionConfig = new DestinationConnection()
        .withConfiguration(destinationConnection)
        .withWorkspaceId(workspaceId)
        .withDestinationDefinitionId(destinationDefinitionId)
        .withDestinationId(destinationId)
        .withTombstone(false);

    final Field field = new Field()
        .withName(FIELD_NAME)
        .withDataType(DataType.STRING)
        .withSelected(true);

    final Stream stream = new Stream()
        .withName(STREAM_NAME)
        .withSelected(true)
        .withFields(Collections.singletonList(field));

    final Schema schema = new Schema().withStreams(Collections.singletonList(stream));

    final StandardSync standardSync = new StandardSync()
        .withConnectionId(connectionId)
        .withDestinationId(destinationId)
        .withSourceId(sourceId)
        .withStatus(StandardSync.Status.ACTIVE)
        .withSyncMode(SyncMode.FULL_REFRESH)
        .withName(CONNECTION_NAME)
        .withSchema(schema);

    final String stateValue = Jsons.serialize(Map.of("lastSync", String.valueOf(LAST_SYNC_TIME)));

    final State state = new State().withState(Jsons.jsonNode(stateValue));

    final StandardSyncInput syncInput = new StandardSyncInput()
        .withDestinationConfiguration(destinationConnectionConfig.getConfiguration())
        .withCatalog(AirbyteProtocolConverters.toConfiguredCatalog(standardSync.getSchema()))
        .withSourceConfiguration(sourceConnectionConfig.getConfiguration())
        .withState(state);

    return new ImmutablePair<>(standardSync, syncInput);
  }

}
