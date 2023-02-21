/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.config.ActorDefinitionConfigInjection;
import java.io.IOException;
import java.util.List;
import java.util.UUID;

public class ConfigInjector {

  private final ConfigRepository configRepository;

  public ConfigInjector(final ConfigRepository configRepository) {
    this.configRepository = configRepository;
  }

  public JsonNode injectConfig(final JsonNode configuration, final UUID actorDefinitionId) throws IOException {
    final List<ActorDefinitionConfigInjection> configInjections = configRepository.getActorDefinitionConfigInjections(actorDefinitionId).toList();
    configInjections.forEach(injection -> {
      ((ObjectNode) configuration).set(injection.getInjectionPath(), injection.getJsonToInject());
    });
    return configuration;
  }

}
