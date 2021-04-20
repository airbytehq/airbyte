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

import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3Config;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

public class CopyConsumer extends FailureTrackingAirbyteMessageConsumer {

  private final String configuredSchema;
  private final S3Config s3Config;
  private final ConfiguredAirbyteCatalog catalog;
  private final JdbcDatabase db;
  private final CopierSupplier copierSupplier;
  private final SqlOperations sqlOperations;
  private final ExtendedNameTransformer nameTransformer;
  private final Map<AirbyteStreamNameNamespacePair, Copier> pairToCopier;

  public CopyConsumer(String configuredSchema,
                      S3Config s3Config,
                      ConfiguredAirbyteCatalog catalog,
                      JdbcDatabase db,
                      CopierSupplier copierSupplier,
                      SqlOperations sqlOperations,
                      ExtendedNameTransformer nameTransformer) {
    this.configuredSchema = configuredSchema;
    this.s3Config = s3Config;
    this.catalog = catalog;
    this.db = db;
    this.copierSupplier = copierSupplier;
    this.sqlOperations = sqlOperations;
    this.nameTransformer = nameTransformer;
    this.pairToCopier = new HashMap<>();
  }

  @Override
  protected void startTracked() {
    var stagingFolder = UUID.randomUUID().toString();
    for (var configuredStream : catalog.getStreams()) {
      if (configuredStream.getDestinationSyncMode() == null) {
        throw new IllegalStateException("Undefined destination sync mode.");
      }
      var stream = configuredStream.getStream();
      var pair = AirbyteStreamNameNamespacePair.fromAirbyteSteam(stream);
      var syncMode = configuredStream.getDestinationSyncMode();
      var copier = copierSupplier.get(configuredSchema, s3Config, stagingFolder, syncMode, stream, nameTransformer, db, sqlOperations);

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

  public void closeAsOneTransaction(List<Copier> copiers, boolean hasFailed, JdbcDatabase db) throws Exception {
    try {
      StringBuilder mergeCopiersToFinalTableQuery = new StringBuilder();
      for (var copier : copiers) {
        var mergeQuery = copier.copyToTmpTableAndPrepMergeToFinalTable(hasFailed);
        mergeCopiersToFinalTableQuery.append(mergeQuery);
      }
      sqlOperations.executeTransaction(db, mergeCopiersToFinalTableQuery.toString());
    } finally {
      for (var copier : copiers) {
        copier.removeFileAndDropTmpTable();
      }
    }
  }

}
