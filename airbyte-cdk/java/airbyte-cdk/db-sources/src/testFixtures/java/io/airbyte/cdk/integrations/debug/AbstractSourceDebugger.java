/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.debug;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.cdk.integrations.source.relationaldb.AbstractDbSource;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlagsWrapper;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.Collections;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Base class defined to create a debugger for a source. This class can be used for internal
 * testing, by : 1. Extending this class for the desired connector. 2. Implementing the given
 * abstract methods. 3. Copying over any relevant configurations, catalogs & state in the
 * resources/debug_resources directory.
 */
public abstract class AbstractSourceDebugger {

  private final AbstractDbSource source;
  private final JsonNode deserializeConfig;

  protected AbstractSourceDebugger() throws Exception {
    this.source = getSource();
    this.deserializeConfig = getUserConfig();
  }

  protected abstract AbstractDbSource getSource();

  // Flag to determine whether per-stream mode is enabled.
  protected abstract boolean perStreamEnabled();

  /*
   * Modify the configuration by setting any debug level parameters to make sure that state is not
   * mutated in the source DB. This includes checking whether the configuration will inadvertently
   * modify any state (e.g. ack LSN for Postgres) on the source DB side, and to appropriately set any
   * debug parameters or throw exceptions.
   */
  protected abstract JsonNode convertToDebugConfig(JsonNode originalConfig) throws Exception;

  @SuppressWarnings({"unchecked", "deprecation", "resource"})
  public void read() throws Exception {
    final JsonNode debugConfig = convertToDebugConfig(deserializeConfig);
    final String catalog = MoreResources.readResource("debug_resources/configured_catalog.json");
    if (perStreamEnabled()) {
      source.setFeatureFlags(FeatureFlagsWrapper.overridingUseStreamCapableState(new EnvVariableFeatureFlags(), true));
    }
    final ConfiguredAirbyteCatalog configuredAirbyteCatalog = Jsons.deserialize(catalog, ConfiguredAirbyteCatalog.class);
    final AirbyteStateMessage message = Jsons.deserialize(MoreResources.readResource("debug_resources/state.json"), AirbyteStateMessage.class);
    System.out.println();
    final AtomicInteger d = new AtomicInteger(0);
    final JsonNode state = Jsons.jsonNode(Collections.singletonList(message));
    final AutoCloseableIterator<AirbyteMessage> messageIterator = source.read(debugConfig, configuredAirbyteCatalog, state);
    messageIterator.forEachRemaining(c -> d.incrementAndGet());
  }

  @SuppressWarnings({"unchecked", "deprecation", "resource"})
  public void discover() throws Exception {
    source.discover(deserializeConfig);
  }

  @SuppressWarnings({"unchecked", "deprecation", "resource"})
  public void check() throws Exception {
    source.check(this.deserializeConfig);
  }

  private static JsonNode getUserConfig() throws Exception {
    final String config = MoreResources.readResource("debug_resources/config.json");
    final ObjectMapper mapper = new ObjectMapper();
    final JsonNode jsonNode = mapper.readTree(config);
    return jsonNode;
  }

}
