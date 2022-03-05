/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.wrapper;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.function.Consumer;

public class WrappedDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(WrappedDestination.class);

  private final Destination delegate;

  public WrappedDestination(final Destination delegate) {
    this.delegate = delegate;
  }

  @Override
  public ConnectorSpecification spec() throws Exception {
    return delegate.spec();
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) throws Exception {
    return delegate.check(config);
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector)
      throws Exception {
    return delegate.getConsumer(config, catalog, outputRecordCollector);
  }

}
