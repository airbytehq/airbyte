/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import static org.junit.jupiter.api.Assertions.*;
import static org.junit.jupiter.params.provider.Arguments.arguments;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import java.util.stream.Stream;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

public class DatabricksDestinationResolverTest {

  private static final ObjectMapper mapper = MoreMappers.initMapper();

  @Test
  @DisplayName("Storage credentials required")
  public void storageCredentialsRequiredTest() {
    final var stubLoadingMethod = mapper.createObjectNode();
    final var stubConfig = mapper.createObjectNode();
    stubConfig.set("data_source", stubLoadingMethod);
    assertThrows(IllegalArgumentException.class, () -> DatabricksDestinationResolver.getTypeFromConfig(stubConfig));
  }

  @ParameterizedTest
  @MethodSource("destinationTypeToConfig")
  public void testS3ConfigType(final String configFileName, final DatabricksStorageType expectedDestinationType) throws Exception {
    final JsonNode config = Jsons.deserialize(MoreResources.readResource(configFileName), JsonNode.class);
    final DatabricksStorageType typeFromConfig = DatabricksDestinationResolver.getTypeFromConfig(config);
    assertEquals(expectedDestinationType, typeFromConfig);
  }

  private static Stream<Arguments> destinationTypeToConfig() {
    return Stream.of(
        arguments("config.json", DatabricksStorageType.S3_STORAGE),
        arguments("azure_config.json", DatabricksStorageType.AZURE_BLOB_STORAGE));
  }

}
