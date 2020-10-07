package io.airbyte.workers.protocols.airbyte;

import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.workers.OutputAndStatus;
import io.airbyte.workers.SyncWorker;
import java.nio.file.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AirbyteSyncWorker implements SyncWorker {

  private final static Logger LOGGER = LoggerFactory.getLogger(AirbyteSyncWorker.class);

  @Override public OutputAndStatus<StandardSyncOutput> run(StandardSyncInput standardSyncInput, Path jobRoot) {
    return null;
  }

  @Override public void cancel() {

  }
}
