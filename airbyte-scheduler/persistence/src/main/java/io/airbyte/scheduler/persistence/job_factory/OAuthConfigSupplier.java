/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.scheduler.persistence.job_factory;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.base.Strings;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Comparator;
import java.util.UUID;

public class OAuthConfigSupplier {

  public static final String SECRET_MASK = "******";
  final private ConfigRepository configRepository;
  private final boolean maskSecrets;

  public OAuthConfigSupplier(ConfigRepository configRepository, boolean maskSecrets) {
    this.configRepository = configRepository;
    this.maskSecrets = maskSecrets;
  }

  public JsonNode injectSourceOAuthParameters(UUID sourceDefinitionId, UUID workspaceId, JsonNode sourceConnectorConfig)
      throws IOException {
    try {
      configRepository.listSourceOAuthParam().stream()
          .filter(p -> sourceDefinitionId.equals(p.getSourceDefinitionId()))
          .filter(p -> p.getWorkspaceId() == null || workspaceId.equals(p.getWorkspaceId()))
          // we prefer params specific to a workspace before global ones (ie workspace is null)
          .min(Comparator.comparing(SourceOAuthParameter::getWorkspaceId, Comparator.nullsLast(Comparator.naturalOrder()))
              .thenComparing(SourceOAuthParameter::getOauthParameterId))
          .ifPresent(
              sourceOAuthParameter -> injectJsonNode((ObjectNode) sourceConnectorConfig, (ObjectNode) sourceOAuthParameter.getConfiguration()));
      return sourceConnectorConfig;
    } catch (JsonValidationException e) {
      throw new IOException(e);
    }
  }

  public JsonNode injectDestinationOAuthParameters(UUID destinationDefinitionId, UUID workspaceId, JsonNode destinationConnectorConfig)
      throws IOException {
    try {
      configRepository.listDestinationOAuthParam().stream()
          .filter(p -> destinationDefinitionId.equals(p.getDestinationDefinitionId()))
          .filter(p -> p.getWorkspaceId() == null || workspaceId.equals(p.getWorkspaceId()))
          // we prefer params specific to a workspace before global ones (ie workspace is null)
          .min(Comparator.comparing(DestinationOAuthParameter::getWorkspaceId, Comparator.nullsLast(Comparator.naturalOrder()))
              .thenComparing(DestinationOAuthParameter::getOauthParameterId))
          .ifPresent(destinationOAuthParameter -> injectJsonNode((ObjectNode) destinationConnectorConfig,
              (ObjectNode) destinationOAuthParameter.getConfiguration()));
      return destinationConnectorConfig;
    } catch (JsonValidationException e) {
      throw new IOException(e);
    }
  }

  private void injectJsonNode(ObjectNode config, ObjectNode fromConfig) {
    for (String key : Jsons.keys(fromConfig)) {
      if (maskSecrets) {
        config.set(key, Jsons.jsonNode(SECRET_MASK));
      } else {
        if (!config.has(key) || isSecretMask(config.get(key).asText())) {
          config.set(key, fromConfig.get(key));
        }
      }
    }
  }

  private static boolean isSecretMask(String input) {
    return Strings.isNullOrEmpty(input.replaceAll("\\*", ""));
  }

}
