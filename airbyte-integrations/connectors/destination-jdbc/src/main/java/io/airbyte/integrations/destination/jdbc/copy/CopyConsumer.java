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

package io.airbyte.integrations.destination.jdbc.copy;

import com.google.common.base.Preconditions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;

public class CopyConsumer<T> extends FailureTrackingAirbyteMessageConsumer {

  private final String configuredSchema;
  private final T config;
  private final ConfiguredAirbyteCatalog catalog;
  private final JdbcDatabase db;
  private final StreamCopierFactory<T> streamCopierFactory;
  private final SqlOperations sqlOperations;
  private final ExtendedNameTransformer nameTransformer;
  private final Map<AirbyteStreamNameNamespacePair, StreamCopier> pairToCopier;

  public CopyConsumer(String configuredSchema,
                      T config,
                      ConfiguredAirbyteCatalog catalog,
                      JdbcDatabase db,
                      StreamCopierFactory<T> streamCopierFactory,
                      SqlOperations sqlOperations,
                      ExtendedNameTransformer nameTransformer) {
    this.configuredSchema = configuredSchema;
    this.config = config;
    this.catalog = catalog;
    this.db = db;
    this.streamCopierFactory = streamCopierFactory;
    this.sqlOperations = sqlOperations;
    this.nameTransformer = nameTransformer;
    this.pairToCopier = new HashMap<>();

    var definedSyncModes = catalog.getStreams().stream()
        .map(ConfiguredAirbyteStream::getDestinationSyncMode)
        .noneMatch(Objects::isNull);
    Preconditions.checkState(definedSyncModes, "Undefined destination sync mode.");
  }

  @Override
  protected void startTracked() {
    var stagingFolder = UUID.randomUUID().toString();
    for (var configuredStream : catalog.getStreams()) {
      var stream = configuredStream.getStream();
      var pair = AirbyteStreamNameNamespacePair.fromAirbyteSteam(stream);
      var syncMode = configuredStream.getDestinationSyncMode();
      var copier = streamCopierFactory.create(configuredSchema, config, stagingFolder, syncMode, stream, nameTransformer, db, sqlOperations);

      pairToCopier.put(pair, copier);
    }
  }

  @Override
  protected void acceptTracked(AirbyteRecordMessage message) throws Exception {
    var pair = AirbyteStreamNameNamespacePair.fromRecordMessage(message);
    if (!pairToCopier.containsKey(pair)) {
      throw new IllegalArgumentException(
          String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
              Jsons.serialize(catalog), Jsons.serialize(message)));
    }

    var id = UUID.randomUUID();
    var data = Jsons.serialize(message.getData());
    var emittedAt = Timestamp.from(Instant.ofEpochMilli(message.getEmittedAt()));

    pairToCopier.get(pair).write(id, data, emittedAt);
  }

  /**
   * Although 'close' suggests a focus on clean up, this method also loads files into the warehouse.
   * First, move the files into temporary table, then merge the temporary tables with the final
   * destination tables. Lastly, do actual clean up and best-effort remove the files and temporary
   * tables.
   */
  public void close(boolean hasFailed) throws Exception {
    closeAsOneTransaction(new ArrayList<>(pairToCopier.values()), hasFailed, db);
  }

  public void closeAsOneTransaction(List<StreamCopier> streamCopiers, boolean hasFailed, JdbcDatabase db) throws Exception {
    try {
      StringBuilder mergeCopiersToFinalTableQuery = new StringBuilder();
      for (var copier : streamCopiers) {
        copier.closeStagingUploader(hasFailed);

        if (!hasFailed) {
          copier.createTemporaryTable();
          copier.copyStagingFileToTemporaryTable();
          copier.createDestinationSchema();
          var destTableName = copier.createDestinationTable();
          var mergeQuery = copier.generateMergeStatement(destTableName);
          mergeCopiersToFinalTableQuery.append(mergeQuery);
        }
      }

      if (!hasFailed) {
        sqlOperations.executeTransaction(db, mergeCopiersToFinalTableQuery.toString());
      }
    } finally {
      for (var copier : streamCopiers) {
        copier.removeFileAndDropTmpTable();
      }
    }
  }

}
