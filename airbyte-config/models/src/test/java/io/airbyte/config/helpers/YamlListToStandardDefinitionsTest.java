/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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

public class YamlListToStandardDefinitionsTest {

  private static final String goodDesDefYaml =
      "- destinationDefinitionId: a625d593-bba5-4a1c-a53d-2d246268a816\n"
          + "  name: Local JSON\n"
          + "  dockerRepository: airbyte/destination-local-json\n"
          + "  dockerImageTag: 0.1.4\n"
          + "  documentationUrl: https://docs.airbyte.io/integrations/destinations/local-json";
  private static final String duplicateId =
      "- destinationDefinitionId: a625d593-bba5-4a1c-a53d-2d246268a816\n"
          + "  name: Local JSON\n"
          + "  dockerRepository: airbyte/destination-local-json\n"
          + "  dockerImageTag: 0.1.4\n"
          + "  documentationUrl: https://docs.airbyte.io/integrations/destinations/local-json"
          + "- destinationDefinitionId: a625d593-bba5-4a1c-a53d-2d246268a816\n"
          + "  name: JSON 2\n"
          + "  dockerRepository: airbyte/destination-local-json\n"
          + "  dockerImageTag: 0.1.4\n"
          + "  documentationUrl: https://docs.airbyte.io/integrations/destinations/local-json";
  private static final String duplicateName =
      "- destinationDefinitionId: a625d593-bba5-4a1c-a53d-2d246268a816\n"
          + "  name: Local JSON\n"
          + "  dockerRepository: airbyte/destination-local-json\n"
          + "  dockerImageTag: 0.1.4\n"
          + "  documentationUrl: https://docs.airbyte.io/integrations/destinations/local-json\n"
          + "- destinationDefinitionId: 8be1cf83-fde1-477f-a4ad-318d23c9f3c6\n"
          + "  name: Local JSON\n"
          + "  dockerRepository: airbyte/destination-csv\n"
          + "  dockerImageTag: 0.1.8\n"
          + "  documentationUrl: https://docs.airbyte.io/integrations/destinations/local-csv";
  private static final String badData =
      "- destinationDefinitionId: a625d593-bba5-4a1c-a53d-2d246268a816\n"
          + "  name: Local JSON\n"
          + "  dockerRepository: airbyte/destination-local-json\n"
          + "  dockerImageTag: 0.1.8\n"
          + "  documentationUrl";

  @Nested
  @DisplayName("vertifyAndConvertToJsonNode")
  public class VerifyAndConvertToJsonNode {

    private static final String ID_NAME = "destinationDefinitionId";

    private final ObjectMapper mapper = MoreMappers.initMapper();

    @Test
    @DisplayName("should correctly read yaml file")
    public void correctlyReadTest() throws JsonProcessingException {
      var jsonDefs = YamlListToStandardDefinitions.verifyAndConvertToJsonNode(ID_NAME, goodDesDefYaml);
      var defList = mapper.treeToValue(jsonDefs, StandardDestinationDefinition[].class);
      assertEquals(1, defList.length);
      assertEquals("Local JSON", defList[0].getName());
    }

    @Test
    @DisplayName("should error out on duplicate id")
    public void duplicateIdTest() {
      assertThrows(RuntimeException.class, () -> YamlListToStandardDefinitions.verifyAndConvertToJsonNode(ID_NAME, duplicateId));
    }

    @Test
    @DisplayName("should error out on duplicate name")
    public void duplicateNameTest() {
      assertThrows(RuntimeException.class, () -> YamlListToStandardDefinitions.verifyAndConvertToJsonNode(ID_NAME, duplicateName));
    }

    @Test
    @DisplayName("should error out on empty file")
    public void emptyFileTest() {
      assertThrows(RuntimeException.class, () -> YamlListToStandardDefinitions.verifyAndConvertToJsonNode(ID_NAME, ""));
    }

    @Test
    @DisplayName("should error out on bad data")
    public void badDataTest() {
      assertThrows(RuntimeException.class, () -> YamlListToStandardDefinitions.verifyAndConvertToJsonNode(ID_NAME, badData));
    }

  }

  @Nested
  @DisplayName("verifyAndConvertToModelList")
  public class VerifyAndConvertToModelList {

    @Test
    @DisplayName("should correctly read yaml file")
    public void correctlyReadTest() {
      var defs = YamlListToStandardDefinitions
          .verifyAndConvertToModelList(StandardDestinationDefinition.class, goodDesDefYaml);
      assertEquals(1, defs.size());
      assertEquals("Local JSON", defs.get(0).getName());
    }

    @Test
    @DisplayName("should error out on duplicate id")
    public void duplicateIdTest() {
      assertThrows(RuntimeException.class,
          () -> YamlListToStandardDefinitions.verifyAndConvertToModelList(StandardDestinationDefinition.class, duplicateId));
    }

    @Test
    @DisplayName("should error out on duplicate name")
    public void duplicateNameTest() {
      assertThrows(RuntimeException.class,
          () -> YamlListToStandardDefinitions.verifyAndConvertToModelList(StandardDestinationDefinition.class, duplicateName));
    }

    @Test
    @DisplayName("should error out on empty file")
    public void emptyFileTest() {
      assertThrows(RuntimeException.class,
          () -> YamlListToStandardDefinitions.verifyAndConvertToModelList(StandardDestinationDefinition.class, ""));
    }

    @Test
    @DisplayName("should error out on bad data")
    public void badDataTest() {
      assertThrows(RuntimeException.class,
          () -> YamlListToStandardDefinitions.verifyAndConvertToModelList(StandardDestinationDefinition.class, badData));
    }

  }

}
