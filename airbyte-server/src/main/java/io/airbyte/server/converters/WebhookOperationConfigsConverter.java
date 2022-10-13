/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.converters;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.api.model.generated.WebhookConfigRead;
import io.airbyte.api.model.generated.WebhookConfigWrite;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.WebhookConfig;
import io.airbyte.config.WebhookOperationConfigs;
import java.util.Collections;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

public class WebhookOperationConfigsConverter {

  public static JsonNode toPersistenceWrite(List<WebhookConfigWrite> apiWebhookConfigs) {
    if (apiWebhookConfigs == null) {
      return Jsons.emptyObject();
    }

    final WebhookOperationConfigs configs = new WebhookOperationConfigs()
        .withWebhookConfigs(apiWebhookConfigs.stream().map(WebhookOperationConfigsConverter::toPersistenceConfig).collect(Collectors.toList()));

    return Jsons.jsonNode(configs);
  }

  public static List<WebhookConfigRead> toApiReads(List<WebhookConfig> persistenceConfig) {
    if (persistenceConfig.isEmpty()) {
      return Collections.emptyList();
    }
    return persistenceConfig.stream().map(WebhookOperationConfigsConverter::toApiRead).collect(Collectors.toList());
  }

  private static WebhookConfig toPersistenceConfig(final WebhookConfigWrite input) {
    return new WebhookConfig()
        .withId(UUID.randomUUID())
        .withName(input.getName())
        .withAuthToken(input.getAuthToken());
  }

  private static WebhookConfigRead toApiRead(final WebhookConfig persistenceConfig) {
    final var read = new WebhookConfigRead();
    read.setId(persistenceConfig.getId());
    read.setName(persistenceConfig.getName());
    return read;
  }

}
