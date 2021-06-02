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

package io.airbyte.integrations.destination.bigquery;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.CopyJobConfiguration;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.JobInfo.CreateDisposition;
import com.google.cloud.bigquery.JobInfo.WriteDisposition;
import com.google.cloud.bigquery.QueryParameterValue;
import com.google.cloud.bigquery.TableId;
import com.google.common.base.Charsets;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryRecordConsumer extends FailureTrackingAirbyteMessageConsumer implements AirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryRecordConsumer.class);

  private final BigQuery bigquery;
  private final Map<AirbyteStreamNameNamespacePair, WriteConfig> writeConfigs;
  private final ConfiguredAirbyteCatalog catalog;
  private final Consumer<AirbyteMessage> outputRecordCollector;

  private AirbyteMessage lastStateMessage = null;

  public BigQueryRecordConsumer(BigQuery bigquery,
                                Map<AirbyteStreamNameNamespacePair, WriteConfig> writeConfigs,
                                ConfiguredAirbyteCatalog catalog,
                                Consumer<AirbyteMessage> outputRecordCollector) {
    this.bigquery = bigquery;
    this.writeConfigs = writeConfigs;
    this.catalog = catalog;
    this.outputRecordCollector = outputRecordCollector;
  }

  @Override
  protected void startTracked() {
    // todo (cgardens) - move contents of #write into this method.
  }

  @Override
  public void acceptTracked(AirbyteMessage message) {
    if (message.getType() == Type.STATE) {
      lastStateMessage = message;
    } else if (message.getType() == Type.RECORD) {
      final AirbyteRecordMessage recordMessage = message.getRecord();

      // ignore other message types.
      AirbyteStreamNameNamespacePair pair = AirbyteStreamNameNamespacePair.fromRecordMessage(recordMessage);
      if (!writeConfigs.containsKey(pair)) {
        throw new IllegalArgumentException(
            String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
                Jsons.serialize(catalog), Jsons.serialize(recordMessage)));
      }

      // Bigquery represents TIMESTAMP to the microsecond precision, so we convert to microseconds then
      // use BQ helpers to string-format correctly.
      long emittedAtMicroseconds = TimeUnit.MICROSECONDS.convert(recordMessage.getEmittedAt(), TimeUnit.MILLISECONDS);
      final String formattedEmittedAt = QueryParameterValue.timestamp(emittedAtMicroseconds).getValue();

      final JsonNode data = Jsons.jsonNode(ImmutableMap.of(
          JavaBaseConstants.COLUMN_NAME_AB_ID, UUID.randomUUID().toString(),
          JavaBaseConstants.COLUMN_NAME_DATA, Jsons.serialize(recordMessage.getData()),
          JavaBaseConstants.COLUMN_NAME_EMITTED_AT, formattedEmittedAt));
      try {
        writeConfigs.get(pair).getWriter()
            .write(ByteBuffer.wrap((Jsons.serialize(data) + "\n").getBytes(Charsets.UTF_8)));
      } catch (IOException e) {
        throw new RuntimeException(e);
      }
    } else {
      LOGGER.warn("Unexpected message: " + message.getType());
    }
  }

  @Override
  public void close(boolean hasFailed) {
    try {
      writeConfigs.values().parallelStream().forEach(writeConfig -> Exceptions.toRuntime(() -> writeConfig.getWriter().close()));
      writeConfigs.values().forEach(writeConfig -> Exceptions.toRuntime(() -> {
        if (writeConfig.getWriter().getJob() != null) {
          writeConfig.getWriter().getJob().waitFor();
        }
      }));
      if (!hasFailed) {
        LOGGER.info("executing on success close procedure.");
        writeConfigs.values()
            .forEach(
                writeConfig -> copyTable(bigquery, writeConfig.getTmpTable(), writeConfig.getTable(), writeConfig.getSyncMode()));
        // BQ is still all or nothing if a failure happens in the destination.
        outputRecordCollector.accept(lastStateMessage);
      }
    } finally {
      // clean up tmp tables;
      writeConfigs.values().forEach(writeConfig -> bigquery.delete(writeConfig.getTmpTable()));
    }
  }

  // https://cloud.google.com/bigquery/docs/managing-tables#copying_a_single_source_table
  private static void copyTable(
                                BigQuery bigquery,
                                TableId sourceTableId,
                                TableId destinationTableId,
                                WriteDisposition syncMode) {

    final CopyJobConfiguration configuration = CopyJobConfiguration.newBuilder(destinationTableId, sourceTableId)
        .setCreateDisposition(CreateDisposition.CREATE_IF_NEEDED)
        .setWriteDisposition(syncMode)
        .build();

    final Job job = bigquery.create(JobInfo.of(configuration));
    final ImmutablePair<Job, String> jobStringImmutablePair = BigQueryUtils.executeQuery(job);
    if (jobStringImmutablePair.getRight() != null) {
      throw new RuntimeException("BigQuery was unable to copy table due to an error: \n" + job.getStatus().getError());
    }
    LOGGER.info("successfully copied tmp table: {} to final table: {}", sourceTableId, destinationTableId);
  }

}
