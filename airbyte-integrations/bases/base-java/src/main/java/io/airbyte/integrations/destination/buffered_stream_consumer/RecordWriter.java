/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.buffered_stream_consumer;

import io.airbyte.commons.functional.CheckedBiConsumer;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.util.List;

public interface RecordWriter extends CheckedBiConsumer<AirbyteStreamNameNamespacePair, List<AirbyteRecordMessage>, Exception> {

  @Override
  void accept(AirbyteStreamNameNamespacePair pair, List<AirbyteRecordMessage> records) throws Exception;

}
