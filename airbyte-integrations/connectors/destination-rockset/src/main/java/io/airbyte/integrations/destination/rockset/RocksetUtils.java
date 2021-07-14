package io.airbyte.integrations.destination.rockset;

import com.fasterxml.jackson.databind.JsonNode;
import com.rockset.client.ApiException;
import com.rockset.client.RocksetClient;
import com.rockset.client.model.CreateWorkspaceRequest;
import com.rockset.client.model.CreateWorkspaceResponse;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RocksetUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(RocksetUtils.class);

  public static final String WORKSPACE_ID = "workspace";
  public static final String API_KEY_ID = "api_key";
  public static final String APISERVER_URL = "api.rs2.usw2.rockset.com";

  public static RocksetClient clientFromConfig(JsonNode config) {
    String apiKey = config.get(API_KEY_ID).asText();
    return new RocksetClient(apiKey, APISERVER_URL);
  }

  public static void createWorkspaceIfNotExists(RocksetClient client, String workspace) throws Exception {
    CreateWorkspaceRequest request = new CreateWorkspaceRequest()
        .name(workspace);

    try {
      CreateWorkspaceResponse response = client.createWorkspace(request);
      LOGGER.info(String.format("Created workspace %s", workspace));
    } catch (ApiException e) {
      if (e.getCode() == 400) {
        LOGGER.info(String.format("Workspace %s already exists", workspace));
        return;
      }

      throw e;
    }
  }
}
