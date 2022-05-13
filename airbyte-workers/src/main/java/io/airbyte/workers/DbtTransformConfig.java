/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.yaml.Yamls;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Collections;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class DbtTransformConfig {

  private static final String exampleConfig =
      "{\"ssl\":false,\"host\":\"parker-database-1.cuczxc1ksccg.us-east-2.rds.amazonaws.com\",\"port\":5432,\"schema\":\"public\",\"database\":\"postgres\",\"password\":\"airbyte-data-1\",\"username\":\"postgres\",\"tunnel_method\":{\"tunnel_method\":\"NO_TUNNEL\"}}";

  public static void main(final String[] args) throws IOException {

    transformConfig(Jsons.deserialize(exampleConfig));

    // final String baseProfileString =
    // MoreResources.readResource("dbt_transform_config_profile_base.yml");
    // final var jsonNode = Yamls.deserialize(baseProfileString);
    // log.info(String.valueOf(jsonNode));
    //
    // final var postgresNode = transformPostgres(Jsons.deserialize(exampleConfig));
    // log.info(String.valueOf(postgresNode));
    // final int i = 0;

  }

  public static void transformConfigToProfile(final JsonNode config, final Path profilePath) {
    final JsonNode transformedConfig = transformConfig(config);
    writeTransformedConfig(transformedConfig, profilePath);
  }

  public static JsonNode transformConfig(final JsonNode config) {
    try {
      final String baseProfileString = MoreResources.readResource("dbt_transform_config_profile_base.yml");
      final JsonNode profile = Yamls.deserialize(baseProfileString);
      final JsonNode transformed = transformPostgres(config);

      // merge transformed config into base profile
      ((ObjectNode) profile.get("normalize").get("outputs")).replace("prod", transformed);
      log.info("merged profile: {}", profile);
      return profile;
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  private static void writeTransformedConfig(final JsonNode config, final Path writeDestination) {
    final String transformedYaml = Yamls.serializeWithoutQuotes(config);
    log.info("writing:\n{}", transformedYaml);
    final Path profilePath = IOs.writeFile(writeDestination, transformedYaml);
    log.info("wrote to {}", profilePath.toString());
  }

  private static JsonNode transformPostgres(final JsonNode config) {
    final JsonNode transformed = Jsons.jsonNode(Collections.emptyMap());
    ((ObjectNode) transformed).put("type", "postgres");
    ((ObjectNode) transformed).put("host", config.get("host").textValue());
    ((ObjectNode) transformed).put("user", config.get("username").textValue());
    ((ObjectNode) transformed).put("pass", config.get("password").textValue()); // TODO test what happens if password missing
    ((ObjectNode) transformed).put("port", config.get("port").intValue());
    ((ObjectNode) transformed).put("dbname", config.get("database").textValue());
    ((ObjectNode) transformed).put("schema", config.get("schema").textValue());
    ((ObjectNode) transformed).put("threads", "8");

    return transformed;
  }

}
