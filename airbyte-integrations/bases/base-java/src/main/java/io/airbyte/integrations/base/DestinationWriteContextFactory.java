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
import io.airbyte.commons.text.Names;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.SyncMode;
import java.util.HashMap;
import java.util.Map;

/**
 * Factory class to convert from config and catalog objects into DestinationWriterContext
 * configuration object. This configuration is then used by the RecordConsumers configure their
 * behavior on where to apply their task and data operations
 */
public class DestinationWriteContextFactory {

  private final SQLNamingResolvable namingResolver;

  public DestinationWriteContextFactory(SQLNamingResolvable namingResolver) {
    this.namingResolver = namingResolver;
  }

  public Map<String, DestinationWriteContext> build(JsonNode config, ConfiguredAirbyteCatalog catalog) {
    Map<String, DestinationWriteContext> result = new HashMap<>();
    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      final String streamName = stream.getStream().getName();
      final String schemaName = getNamingResolver().getIdentifier(getSchemaName(config, stream));
      final String tableName = Names.concatQuotedNames(getNamingResolver().getIdentifier(streamName), "_raw");
      final SyncMode syncMode = stream.getSyncMode() != null ? stream.getSyncMode() : SyncMode.FULL_REFRESH;
      result.put(streamName, new DestinationWriteContext(schemaName, tableName, syncMode));
    }
    return result;
  }

  protected String getSchemaName(JsonNode config, ConfiguredAirbyteStream stream) {
    // do we need to retrieve another more specific schema from this stream?

    if (config.has("schema")) {
      return config.get("schema").asText();
    } else {
      return "public";
    }
  }

  public SQLNamingResolvable getNamingResolver() {
    return namingResolver;
  }

}
