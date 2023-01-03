/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.function.Consumer;
import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Multiple configs may allow you to sync data to the destination in multiple ways.
 *
 * One primary example is that the default behavior for some DB-based destinations may use
 * INSERT-based destinations while (given additional credentials) it may be able to sync data using
 * a file copied to a staging location.
 *
 * This class exists to make it easy to define a destination in terms of multiple other destination
 * implementations, switching between them based on the config provided.
 */
public class SwitchingDestination<T extends Enum<T>> extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(SwitchingDestination.class);

  private final Function<JsonNode, T> configToType;
  private final Map<T, Destination> typeToDestination;

  public SwitchingDestination(final Class<T> enumClass, final Function<JsonNode, T> configToType, final Map<T, Destination> typeToDestination) {
    final Set<T> allEnumConstants = new HashSet<>(Arrays.asList(enumClass.getEnumConstants()));
    final Set<T> supportedEnumConstants = typeToDestination.keySet();

    // check that it isn't possible for configToType to produce something we can't handle
    Preconditions.checkArgument(allEnumConstants.equals(supportedEnumConstants));

    this.configToType = configToType;
    this.typeToDestination = typeToDestination;
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) throws Exception {
    final T destinationType = configToType.apply(config);
    LOGGER.info("Using destination type: " + destinationType.name());
    return typeToDestination.get(destinationType).check(config);
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector)
      throws Exception {
    final T destinationType = configToType.apply(config);
    LOGGER.info("Using destination type: " + destinationType.name());
    return typeToDestination.get(destinationType).getConsumer(config, catalog, outputRecordCollector);
  }

}
