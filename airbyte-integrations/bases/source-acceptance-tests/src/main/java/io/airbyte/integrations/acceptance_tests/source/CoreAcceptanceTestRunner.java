package io.airbyte.integrations.acceptance_tests.source;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;

public class CoreAcceptanceTestRunner extends CoreAcceptanceTest {

  public static JsonNode VALID_CONFIG;
  public static ConfiguredAirbyteCatalog CONFIGURED_CATALOG;
  public static JsonNode EXPECTED_SPEC;
  public static String CONNECTOR_IMAGE;
  
  @Override
  protected JsonNode getValidConfig(){
    return VALID_CONFIG;
  }
  
  @Override
  protected JsonNode getExpectedSpec(){
     return EXPECTED_SPEC;
  }
  
  @Override
  protected String getConnectorImage(){
    return CONNECTOR_IMAGE;
  }
  
  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog(){
    return CONFIGURED_CATALOG;
  }
}
