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
import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;

// NOTE: we suppress this warning because PMD thinks it can be a foreach loop in toApiReads but the
// compiler disagrees.
@SuppressWarnings("PMD.ForLoopCanBeForeach")
public class WorkspaceWebhookConfigsConverter {

  public static JsonNode toPersistenceWrite(List<WebhookConfigWrite> apiWebhookConfigs, Supplier<UUID> uuidSupplier) {
    if (apiWebhookConfigs == null) {
      return Jsons.emptyObject();
    }

    final WebhookOperationConfigs configs = new WebhookOperationConfigs()
        .withWebhookConfigs(apiWebhookConfigs.stream().map((item) -> toPersistenceConfig(uuidSupplier, item)).collect(Collectors.toList()));

    return Jsons.jsonNode(configs);
  }

  public static List<WebhookConfigRead> toApiReads(final JsonNode persistenceConfig) {
    if (persistenceConfig == null) {
      return Collections.emptyList();
    }

    // NOTE: we deserialize it "by hand" because the secrets aren't hydrated, so we can't deserialize it
    // into the usual shape.
    // TODO(mfsiega-airbyte): find a cleaner way to handle this situation.
    List<WebhookConfigRead> configReads = new ArrayList<>();
    final JsonNode configArray = persistenceConfig.findPath("webhookConfigs");
    for (Iterator<JsonNode> it = configArray.elements(); it.hasNext();) {
      JsonNode webhookConfig = it.next();
      configReads.add(toApiRead(webhookConfig));
    }
    return configReads;
  }

  private static WebhookConfig toPersistenceConfig(final Supplier<UUID> uuidSupplier, final WebhookConfigWrite input) {
    return new WebhookConfig()
        .withId(uuidSupplier.get())
        .withName(input.getName())
        .withAuthToken(input.getAuthToken());
  }

  private static WebhookConfigRead toApiRead(final JsonNode configJson) {
    final var read = new WebhookConfigRead();
    read.setId(UUID.fromString(configJson.findValue("id").asText()));
    read.setName(configJson.findValue("name").asText());
    return read;
  }

}
