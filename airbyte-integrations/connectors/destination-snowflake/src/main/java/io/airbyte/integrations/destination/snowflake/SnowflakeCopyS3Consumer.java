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

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.snowflake.client.jdbc.internal.amazonaws.services.s3.AmazonS3;

public class SnowflakeCopyS3Consumer extends FailureTrackingAirbyteMessageConsumer {

  private static final SnowflakeSQLNameTransformer nameTransformer = new SnowflakeSQLNameTransformer();

  private final ConfiguredAirbyteCatalog catalog;
  private final String defaultSchema;
  private final JdbcDatabase db;
  private final S3Config s3Config;
  private final AmazonS3 s3Client;
  private final Map<String, SnowflakeCopier> streamNameToCopier;

  public SnowflakeCopyS3Consumer(JsonNode config, ConfiguredAirbyteCatalog catalog) {
    this.catalog = catalog;
    this.db = SnowflakeDatabase.getDatabase(config);
    this.defaultSchema = config.get("schema").asText();
    this.s3Config = new S3Config(config);
    this.s3Client = SnowflakeCopyS3Destination.getAmazonS3(s3Config);
    this.streamNameToCopier = new HashMap<>();
  }

  @Override
  protected void startTracked() throws Exception {
    var stagingFolder = UUID.randomUUID().toString();
    for (var configuredStream : catalog.getStreams()) {
      if (configuredStream.getDestinationSyncMode() == null) {
        throw new IllegalStateException("Undefined destination sync mode.");
      }
      var stream = configuredStream.getStream();
      var streamName = stream.getName();
      var syncMode = configuredStream.getDestinationSyncMode();
      var schema =
          stream.getNamespace() != null ? nameTransformer.convertStreamName(stream.getNamespace()) : nameTransformer.convertStreamName(defaultSchema);
      var copier = new SnowflakeCopier(s3Config.bucketName, stagingFolder, syncMode, schema, streamName, s3Client, db, s3Config);
      streamNameToCopier.put(streamName, copier);
    }
  }

  @Override
  protected void acceptTracked(AirbyteRecordMessage msg) throws Exception {
    var streamName = msg.getStream();
    if (!streamNameToCopier.containsKey(streamName)) {
      throw new IllegalArgumentException(
          String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
              Jsons.serialize(catalog), Jsons.serialize(msg)));
    }

    streamNameToCopier.get(streamName).uploadToS3(msg);
  }

  /**
   * Although 'close' suggests a focus on clean up, this method also loads S3 files into Redshift.
   * First, move the files into temporary table, then merge the temporary tables with the final
   * destination tables. Lastly, do actual clean up and best-effort remove the S3 files and temporary
   * tables.
   */
  @Override
  protected void close(boolean hasFailed) throws Exception {
    SnowflakeCopier.closeAsOneTransaction(new ArrayList<>(streamNameToCopier.values()), hasFailed, db);
  }

}
