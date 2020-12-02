package io.airbyte.integrations.base;

import io.airbyte.commons.text.Names;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.SyncMode;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;

public class TmpDestinationConsumer extends FailureTrackingConsumer<AirbyteMessage> implements DestinationConsumerStrategy {

  private final DestinationConsumerStrategy tmpDestinationConsumer;
  private final CopyToDestination finalDestinationConsumer;

  public TmpDestinationConsumer(DestinationConsumerStrategy tmpDestinationConsumer, CopyToDestination finalDestinationConsumer) {
    this.tmpDestinationConsumer = tmpDestinationConsumer;
    this.finalDestinationConsumer = finalDestinationConsumer;
  }

  @Override
  public void setContext(Map<String, DestinationWriteContext> configs) {
    final Map<String, DestinationWriteContext> tmpConfigs = new HashMap<>();
    final Map<String, DestinationCopyContext> copyConfigs = new HashMap<>();
    for (Entry<String, DestinationWriteContext> entry : configs.entrySet()) {
      DestinationWriteContext config = entry.getValue();

      String tmpTableName = Names.concatNames(config.getOutputTableName(),"_" + Instant.now().toEpochMilli());
      DestinationWriteContext tmpConfig = new DestinationWriteContext(config.getOutputNamespaceName(), tmpTableName, SyncMode.FULL_REFRESH);
      tmpConfigs.put(entry.getKey(), tmpConfig);

      DestinationCopyContext copyConfig = new DestinationCopyContext(config.getOutputNamespaceName(), tmpTableName, config.getOutputTableName(), config.getSyncMode());
      copyConfigs.put(entry.getKey(), copyConfig);
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
      finalDestinationConsumer.execute();
    }
  }
}
