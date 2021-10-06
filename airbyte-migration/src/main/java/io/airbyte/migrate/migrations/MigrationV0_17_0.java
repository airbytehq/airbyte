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

package io.airbyte.migrate.migrations;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.migrate.Migration;
import io.airbyte.migrate.ResourceId;
import io.airbyte.migrate.ResourceType;
import java.util.Map;
import java.util.Set;
import java.util.function.Consumer;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This migration forces upgrading all sources and destinations connectors to be at least equal to
 * or greater than 0.2.0
 *
 * This is because as part of Airbyte V0.17.0-alpha, we made changes to the JSON validation
 * parsers/serializers/deserializers from all connectors to allow for unknown properties, thus
 * bumping their versions to v0.2.0 as part of that release.
 *
 * This is required in case we want to perform modifications to the Airbyte protocol in the future
 * by adding new properties. Connectors that are not using these additional properties yet, should
 * ignore them but keep working as usual instead of throwing json validation errors.
 */
public class MigrationV0_17_0 extends BaseMigration implements Migration {

  private static final Logger LOGGER = LoggerFactory.getLogger(MigrationV0_17_0.class);

  private static final String MIGRATION_VERSION = "0.17.0-alpha";

  protected static final ResourceId STANDARD_SOURCE_DEFINITION_RESOURCE_ID =
      ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_SOURCE_DEFINITION");
  protected static final ResourceId STANDARD_DESTINATION_DEFINITION_RESOURCE_ID =
      ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_DESTINATION_DEFINITION");

  private static final Set<String> DESTINATION_DOCKER_IMAGES = Set.of(
      "airbyte/destination-local-json",
      "airbyte/destination-csv",
      "airbyte/destination-postgres",
      "airbyte/destination-bigquery",
      "airbyte/destination-snowflake",
      "airbyte/destination-redshift",
      "airbyte/destination-meilisearch");
  private static final Set<String> SOURCE_DOCKER_IMAGES = Set.of(
      "airbyte/source-exchangeratesapi-singer",
      "airbyte/source-file",
      "airbyte/source-google-adwords-singer",
      "airbyte/source-github-singer",
      "airbyte/source-mssql",
      "airbyte/source-postgres",
      "airbyte/source-recurly",
      "airbyte/source-sendgrid",
      "airbyte/source-marketo-singer",
      "airbyte/source-google-sheets",
      "airbyte/source-mysql",
      "airbyte/source-salesforce-singer",
      "airbyte/source-stripe-singer",
      "airbyte/source-mailchimp",
      "airbyte/source-googleanalytics-singer",
      "airbyte/source-facebook-marketing",
      "airbyte/source-hubspot-singer",
      "airbyte/source-shopify-singer",
      "airbyte/source-redshift",
      "airbyte/source-twilio-singer",
      "airbyte/source-freshdesk",
      "airbyte/source-braintree-singer",
      "airbyte/source-slack-singer",
      "airbyte/source-greenhouse",
      "airbyte/source-zendesk-support-singer",
      "airbyte/source-intercom-singer",
      "airbyte/source-jira",
      "airbyte/source-mixpanel-singer",
      "airbyte/source-zoom-singer",
      "airbyte/source-microsoft-teams",
      "airbyte/source-drift",
      "airbyte/source-looker",
      "airbyte/source-plaid",
      "airbyte/source-appstore-singer",
      "airbyte/source-mongodb");

  private final Migration previousMigration;

  public MigrationV0_17_0(Migration previousMigration) {
    super(previousMigration);
    this.previousMigration = previousMigration;
  }

  @Override
  public String getVersion() {
    return MIGRATION_VERSION;
  }

  @Override
  public Map<ResourceId, JsonNode> getOutputSchema() {
    return previousMigration.getOutputSchema();
  }

  @Override
  public void migrate(Map<ResourceId, Stream<JsonNode>> inputData, Map<ResourceId, Consumer<JsonNode>> outputData) {
    for (final Map.Entry<ResourceId, Stream<JsonNode>> entry : inputData.entrySet()) {
      final Consumer<JsonNode> recordConsumer = outputData.get(entry.getKey());

      entry.getValue().forEach(r -> {
        if (r.get("dockerImageTag") != null) {
          if (entry.getKey().equals(STANDARD_SOURCE_DEFINITION_RESOURCE_ID)) {
            ((ObjectNode) r).set("dockerImageTag", getDockerImageTag(SOURCE_DOCKER_IMAGES, r));
          } else if (entry.getKey().equals(STANDARD_DESTINATION_DEFINITION_RESOURCE_ID)) {
            ((ObjectNode) r).set("dockerImageTag", getDockerImageTag(DESTINATION_DOCKER_IMAGES, r));
          }
        }
        recordConsumer.accept(r);
      });
    }
  }

  private JsonNode getDockerImageTag(final Set<String> airbyteConnectors, final JsonNode node) {
    final JsonNode dockerImageTag = node.get("dockerImageTag");
    final JsonNode dockerRepository = node.get("dockerRepository");
    if (dockerRepository != null && !dockerRepository.isNull() && airbyteConnectors.contains(dockerRepository.asText())) {
      try {
        final AirbyteVersion connectorVersion = new AirbyteVersion(dockerImageTag.asText());
        final JsonNode requiredDockerTag = Jsons.jsonNode("0.2.0");
        final AirbyteVersion requiredVersion = new AirbyteVersion(requiredDockerTag.asText());
        if (connectorVersion.patchVersionCompareTo(requiredVersion) >= 0) {
          return dockerImageTag;
        } else {
          LOGGER.debug(String.format("Bump connector %s version from %s to %s", dockerRepository, dockerImageTag, requiredDockerTag));
          return requiredDockerTag;
        }
      } catch (IllegalArgumentException e) {
        LOGGER.error(String.format("Failed to recognize connector version %s", node), e);
      }
    }
    return dockerImageTag;
  }

}
