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

import static com.fasterxml.jackson.databind.node.JsonNodeType.OBJECT;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Strings;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.MoreOAuthParameters;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
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
      // TODO there will be cases where we shouldn't write oauth params. See
      // https://github.com/airbytehq/airbyte/issues/5989
      MoreOAuthParameters.getSourceOAuthParameter(configRepository.listSourceOAuthParam().stream(), workspaceId, sourceDefinitionId)
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
      MoreOAuthParameters.getDestinationOAuthParameter(configRepository.listDestinationOAuthParam().stream(), workspaceId, destinationDefinitionId)
          .ifPresent(destinationOAuthParameter -> injectJsonNode((ObjectNode) destinationConnectorConfig,
              (ObjectNode) destinationOAuthParameter.getConfiguration()));
      return destinationConnectorConfig;
    } catch (JsonValidationException e) {
      throw new IOException(e);
    }
  }

  @VisibleForTesting
  void injectJsonNode(ObjectNode mainConfig, ObjectNode fromConfig) {
    // TODO this method might make sense to have as a general utility in Jsons
    for (String key : Jsons.keys(fromConfig)) {
      if (fromConfig.get(key).getNodeType() == OBJECT) {
        // nested objects are merged rather than overwrite the contents of the equivalent object in config
        if (mainConfig.get(key) == null) {
          injectJsonNode(mainConfig.putObject(key), (ObjectNode) fromConfig.get(key));
        } else if (mainConfig.get(key).getNodeType() == OBJECT) {
          injectJsonNode((ObjectNode) mainConfig.get(key), (ObjectNode) fromConfig.get(key));
        } else {
          throw new IllegalStateException("Can't merge an object node into a non-object node!");
        }
      } else {
        if (maskSecrets) {
          // TODO secrets should be masked with the correct type
          // https://github.com/airbytehq/airbyte/issues/5990
          // In the short-term this is not world-ending as all secret fields are currently strings
          mainConfig.set(key, Jsons.jsonNode(SECRET_MASK));
        } else {
          if (!mainConfig.has(key) || isSecretMask(mainConfig.get(key).asText())) {
            mainConfig.set(key, fromConfig.get(key));
          }
        }
      }

    }
  }

  private static boolean isSecretMask(String input) {
    return Strings.isNullOrEmpty(input.replaceAll("\\*", ""));
  }

}
