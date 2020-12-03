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

import io.airbyte.commons.text.Names;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.SyncMode;
import java.time.Instant;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This consumer will delegate actual Record Consumer tasks to Consumers provided in the
 * constructors.
 *
 * However this class will actually dispatch such records towards a temporary consumer first to
 * accumulate data in a staging location.
 *
 * If this temporary operation ends successfully without errors, then the second consumer to
 * finalize a copy from temporary location to final destination will be invoked by this consumer.
 */
public class TmpDestinationConsumer extends FailureTrackingConsumer<AirbyteMessage> implements DestinationConsumerStrategy {

  private static final Logger LOGGER = LoggerFactory.getLogger(TmpDestinationConsumer.class);

  private final TableCreationOperations destination;
  private final DestinationConsumerStrategy tmpDestinationConsumer;
  private final TmpToFinalTable finalDestinationConsumer;
  private Map<String, DestinationWriteContext> tmpConfigs;

  public TmpDestinationConsumer(TableCreationOperations destination,
                                DestinationConsumerStrategy tmpDestinationConsumer,
                                TmpToFinalTable finalDestinationConsumer) {
    this.destination = destination;
    this.tmpDestinationConsumer = tmpDestinationConsumer;
    this.finalDestinationConsumer = finalDestinationConsumer;
    tmpConfigs = new HashMap<>();
  }

  @Override
  public void setContext(Map<String, DestinationWriteContext> configs) throws Exception {
    final Set<String> schemaSet = new HashSet<>();
    tmpConfigs = new HashMap<>();
    final Map<String, DestinationCopyContext> copyConfigs = new HashMap<>();
    for (Entry<String, DestinationWriteContext> entry : configs.entrySet()) {
      DestinationWriteContext config = entry.getValue();

      final String schemaName = config.getOutputNamespaceName();
      final String tableName = config.getOutputTableName();
      final String tmpTableName = Names.concatQuotedNames(tableName, "_" + Instant.now().toEpochMilli());

      DestinationWriteContext tmpConfig = new DestinationWriteContext(schemaName, tmpTableName, SyncMode.FULL_REFRESH);
      tmpConfigs.put(entry.getKey(), tmpConfig);

      DestinationCopyContext copyConfig = new DestinationCopyContext(schemaName, tmpTableName, tableName, config.getSyncMode());
      copyConfigs.put(entry.getKey(), copyConfig);

      if (!schemaSet.contains(schemaName)) {
        destination.createSchema(schemaName);
        schemaSet.add(schemaName);
      }
      destination.createDestinationTable(schemaName, tmpTableName);
    }
    tmpDestinationConsumer.setContext(tmpConfigs);
    finalDestinationConsumer.setContext(copyConfigs);
  }

  @Override
  protected void acceptTracked(AirbyteMessage airbyteMessage) throws Exception {
    tmpDestinationConsumer.accept(airbyteMessage);
  }

  @Override
  protected void close(boolean hasFailed) throws Exception {
    tmpDestinationConsumer.close();
    if (!hasFailed) {
      LOGGER.info("executing on success close procedure.");
      finalDestinationConsumer.execute();
    }
    for (Entry<String, DestinationWriteContext> entry : tmpConfigs.entrySet()) {
      final String schemaName = entry.getValue().getOutputNamespaceName();
      final String tmpTableName = entry.getValue().getOutputTableName();
      destination.dropDestinationTable(schemaName, tmpTableName);
    }
  }

}
