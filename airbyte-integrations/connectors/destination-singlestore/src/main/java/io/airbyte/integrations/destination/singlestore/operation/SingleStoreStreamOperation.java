/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.singlestore.operation;

import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage;
import io.airbyte.cdk.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.operation.AbstractStreamOperation;
import io.airbyte.integrations.base.destination.operation.StorageOperation;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState;
import io.airbyte.integrations.destination.singlestore.staging.SingleStoreCsvSerializedBuffer;
import java.util.stream.Stream;
import org.jetbrains.annotations.NotNull;

public class SingleStoreStreamOperation extends AbstractStreamOperation<MinimumDestinationState.Impl, SerializableBuffer> {

  private final StorageOperation<SerializableBuffer> storageOperation;

  public SingleStoreStreamOperation(@NotNull StorageOperation<SerializableBuffer> storageOperation,
                                    @NotNull DestinationInitialStatus<MinimumDestinationState.Impl> destinationInitialStatus,
                                    boolean disableTypeDedupe) {
    super(storageOperation, destinationInitialStatus, disableTypeDedupe);
    this.storageOperation = storageOperation;
  }

  @SuppressWarnings("try")
  @Override
  public void writeRecords(@NotNull StreamConfig streamConfig, @NotNull Stream<PartialAirbyteMessage> stream) {
    try (var writeBuffer = new SingleStoreCsvSerializedBuffer(new FileBuffer(".csv"))) {
      for (PartialAirbyteMessage r : stream.toList()) {
        var jsonData = r.getSerialized();
        var escapedJsonData = jsonData == null ? "" : jsonData.replace("\\", "\\\\");
        var record = r.getRecord();
        var airbyteMeta = record == null ? "" : Jsons.serialize(record.getMeta()).replace("\\", "\\\\");
        var emittedAt = record == null ? 0L : record.getEmittedAt();
        writeBuffer.accept(escapedJsonData, airbyteMeta, streamConfig.getGenerationId(), emittedAt);
      }
      writeBuffer.flush();
      storageOperation.writeToStage(streamConfig, writeBuffer);
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

}
