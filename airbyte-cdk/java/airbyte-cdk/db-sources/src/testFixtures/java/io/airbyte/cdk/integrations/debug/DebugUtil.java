/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.debug;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.AirbyteSourceConfig;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Collections;

/**
 * Utility class defined to debug a source. Copy over any relevant configurations, catalogs & state
 * in the resources/debug_resources directory.
 */
public class DebugUtil {

  @SuppressWarnings({"unchecked", "deprecation", "resource"})
  public static void debug(final Source debugSource) throws Exception {
    final AirbyteSourceConfig debugConfig = DebugUtil.getConfig();
    final ConfiguredAirbyteCatalog configuredAirbyteCatalog = DebugUtil.getCatalog();
    final JsonNode state = DebugUtil.getState();

    debugSource.check(debugConfig);
    debugSource.discover(debugConfig);

    final AutoCloseableIterator<AirbyteMessage> messageIterator = debugSource.read(debugConfig, configuredAirbyteCatalog, state);
    messageIterator.forEachRemaining(message -> {});
  }

  private static AirbyteSourceConfig getConfig() throws Exception {
    final AirbyteSourceConfig originalConfig = AirbyteSourceConfig.fromPath(Path.of("debug_resources/config.json"));
    final AirbyteSourceConfig debugConfig = originalConfig.cloneBuilder().with("debug_mode", true).build();
    return debugConfig;
  }

  private static ConfiguredAirbyteCatalog getCatalog() throws Exception {
    final String catalog = MoreResources.readResource("debug_resources/configured_catalog.json");
    return Jsons.deserialize(catalog, ConfiguredAirbyteCatalog.class);
  }

  private static JsonNode getState() throws Exception {
    final AirbyteStateMessage message = Jsons.deserialize(MoreResources.readResource("debug_resources/state.json"), AirbyteStateMessage.class);
    return Jsons.jsonNode(Collections.singletonList(message));
  }

}
