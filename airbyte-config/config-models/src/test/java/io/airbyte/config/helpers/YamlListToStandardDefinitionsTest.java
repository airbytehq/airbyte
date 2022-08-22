/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.helpers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.config.StandardDestinationDefinition;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

class YamlListToStandardDefinitionsTest {

  private static final String DESTINATION_DEFINITION_ID = "- destinationDefinitionId: a625d593-bba5-4a1c-a53d-2d246268a816\n";
  private static final String DESTINATION_NAME = "  name: Local JSON\n";
  private static final String DOCKER_REPO = "  dockerRepository: airbyte/destination-local-json\n";
  private static final String DOCKER_IMAGE_TAG = "  dockerImageTag: 0.1.4\n";
  private static final String GOOD_DES_DEF_YAML =
      DESTINATION_DEFINITION_ID
          + DESTINATION_NAME
          + DOCKER_REPO
          + DOCKER_IMAGE_TAG
          + "  documentationUrl: https://docs.airbyte.io/integrations/destinations/local-json";
  private static final String DUPLICATE_ID =
      DESTINATION_DEFINITION_ID
          + DESTINATION_NAME
          + DOCKER_REPO
          + DOCKER_IMAGE_TAG
          + "  documentationUrl: https://docs.airbyte.io/integrations/destinations/local-json"
          + DESTINATION_DEFINITION_ID
          + "  name: JSON 2\n"
          + DOCKER_REPO
          + DOCKER_IMAGE_TAG
          + "  documentationUrl: https://docs.airbyte.io/integrations/destinations/local-json";
  private static final String DUPLICATE_NAME =
      DESTINATION_DEFINITION_ID
          + DESTINATION_NAME
          + DOCKER_REPO
          + DOCKER_IMAGE_TAG
          + "  documentationUrl: https://docs.airbyte.io/integrations/destinations/local-json\n"
          + "- destinationDefinitionId: 8be1cf83-fde1-477f-a4ad-318d23c9f3c6\n"
          + DESTINATION_NAME
          + "  dockerRepository: airbyte/destination-csv\n"
          + "  dockerImageTag: 0.1.8\n"
          + "  documentationUrl: https://docs.airbyte.io/integrations/destinations/local-csv";
  private static final String BAD_DATA =
      DESTINATION_DEFINITION_ID
          + DESTINATION_NAME
          + DOCKER_REPO
          + "  dockerImageTag: 0.1.8\n"
          + "  documentationUrl";

  @Nested
  @DisplayName("vertifyAndConvertToJsonNode")
  class VerifyAndConvertToJsonNode {

    private static final String ID_NAME = "destinationDefinitionId";

    private final ObjectMapper mapper = MoreMappers.initMapper();

    @Test
    @DisplayName("should correctly read yaml file")
    void correctlyReadTest() throws JsonProcessingException {
      final var jsonDefs = YamlListToStandardDefinitions.verifyAndConvertToJsonNode(ID_NAME, GOOD_DES_DEF_YAML);
      final var defList = mapper.treeToValue(jsonDefs, StandardDestinationDefinition[].class);
      assertEquals(1, defList.length);
      assertEquals("Local JSON", defList[0].getName());
    }

    @Test
    @DisplayName("should error out on duplicate id")
    void duplicateIdTest() {
      assertThrows(RuntimeException.class, () -> YamlListToStandardDefinitions.verifyAndConvertToJsonNode(ID_NAME, DUPLICATE_ID));
    }

    @Test
    @DisplayName("should error out on duplicate name")
    void duplicateNameTest() {
      assertThrows(RuntimeException.class, () -> YamlListToStandardDefinitions.verifyAndConvertToJsonNode(ID_NAME, DUPLICATE_NAME));
    }

    @Test
    @DisplayName("should error out on empty file")
    void emptyFileTest() {
      assertThrows(RuntimeException.class, () -> YamlListToStandardDefinitions.verifyAndConvertToJsonNode(ID_NAME, ""));
    }

    @Test
    @DisplayName("should error out on bad data")
    void badDataTest() {
      assertThrows(RuntimeException.class, () -> YamlListToStandardDefinitions.verifyAndConvertToJsonNode(ID_NAME, BAD_DATA));
    }

  }

  @Nested
  @DisplayName("verifyAndConvertToModelList")
  class VerifyAndConvertToModelList {

    @Test
    @DisplayName("should correctly read yaml file")
    void correctlyReadTest() {
      final var defs = YamlListToStandardDefinitions
          .verifyAndConvertToModelList(StandardDestinationDefinition.class, GOOD_DES_DEF_YAML);
      assertEquals(1, defs.size());
      assertEquals("Local JSON", defs.get(0).getName());
    }

    @Test
    @DisplayName("should error out on duplicate id")
    void duplicateIdTest() {
      assertThrows(RuntimeException.class,
          () -> YamlListToStandardDefinitions.verifyAndConvertToModelList(StandardDestinationDefinition.class, DUPLICATE_ID));
    }

    @Test
    @DisplayName("should error out on duplicate name")
    void duplicateNameTest() {
      assertThrows(RuntimeException.class,
          () -> YamlListToStandardDefinitions.verifyAndConvertToModelList(StandardDestinationDefinition.class, DUPLICATE_NAME));
    }

    @Test
    @DisplayName("should error out on empty file")
    void emptyFileTest() {
      assertThrows(RuntimeException.class,
          () -> YamlListToStandardDefinitions.verifyAndConvertToModelList(StandardDestinationDefinition.class, ""));
    }

    @Test
    @DisplayName("should error out on bad data")
    void badDataTest() {
      assertThrows(RuntimeException.class,
          () -> YamlListToStandardDefinitions.verifyAndConvertToModelList(StandardDestinationDefinition.class, BAD_DATA));
    }

  }

}
