/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.output;

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import javax.annotation.concurrent.ThreadSafe;

/**
 * Implementation of the {@link OutputRecordConsumer} interface that uses
 * {@link System#out#println()} to publish serialized {@link AirbyteMessage} objects.
 */
@ThreadSafe
public class SystemOutputRecordConsumer implements OutputRecordConsumer {

  @Override
  public void close() throws Exception {
    System.out.flush();
  }

  @Override
  public void accept(final AirbyteMessage airbyteMessage) {
    System.out.println(Jsons.serialize(airbyteMessage));
  }

}
