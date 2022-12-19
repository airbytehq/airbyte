/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.spec_modification;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.util.function.Consumer;

public abstract class SpecModifyingDestination implements Destination {

  private final Destination destination;

  public SpecModifyingDestination(final Destination destination) {
    this.destination = destination;
  }

  public abstract ConnectorSpecification modifySpec(ConnectorSpecification originalSpec) throws Exception;

  @Override
  public ConnectorSpecification spec() throws Exception {
    return modifySpec(destination.spec());
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) throws Exception {
    return destination.check(config);
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector)
      throws Exception {
    return destination.getConsumer(config, catalog, outputRecordCollector);
  }

}
