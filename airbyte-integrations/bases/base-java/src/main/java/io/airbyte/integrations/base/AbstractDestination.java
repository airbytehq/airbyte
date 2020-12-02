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

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.SyncMode;
import java.util.HashSet;
import java.util.Set;

/**
 * Resolve adequate names of destination identifiers, create necessary schemas and tables, prepare
 * the proper stream consumer that will accumulate and insert data into final destinations using a
 * temporary staging area if stream is completed successfully.
 */
public abstract class AbstractDestination implements Destination {

  @Override
  public DestinationConsumer<AirbyteMessage> write(JsonNode config, ConfiguredAirbyteCatalog catalog) throws Exception {
    connectDatabase(config);
    final Set<String> schemaSet = new HashSet<>();
    final String schemaName = getNamingResolver().getIdentifier(getDefaultSchemaName(config));
    final DestinationConsumer<AirbyteMessage> result = createConsumer(catalog);
    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      final String streamName = stream.getStream().getName();
      final String tableName = getNamingResolver().getRawTableName(streamName);
      final String tmpTableName = getNamingResolver().getTmpTableName(streamName);
      // get a schemaName override from stream?
      if (!schemaSet.contains(schemaName)) {
        createSchema(schemaName);
        schemaSet.add(schemaName);
      }
      // create tmp tables if not exist
      createTable(schemaName, tmpTableName);
      final SyncMode syncMode = stream.getSyncMode() == null ? SyncMode.FULL_REFRESH : stream.getSyncMode();
      result.addStream(streamName, schemaName, tableName, tmpTableName, syncMode);
    }
    result.start();
    return result;
  }

  protected abstract DestinationConsumer<AirbyteMessage> createConsumer(ConfiguredAirbyteCatalog catalog);

  protected abstract void connectDatabase(JsonNode config);

  protected abstract String getDefaultSchemaName(JsonNode config);

  public abstract void createSchema(String schemaName) throws Exception;

  public abstract void createTable(String schemaName, String tableName) throws Exception;

}
