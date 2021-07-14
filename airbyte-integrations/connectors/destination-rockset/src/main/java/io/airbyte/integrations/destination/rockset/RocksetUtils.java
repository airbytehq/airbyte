package io.airbyte.integrations.destination.rockset;

import com.fasterxml.jackson.databind.JsonNode;
import com.rockset.client.ApiException;
import com.rockset.client.RocksetClient;
import com.rockset.client.model.Collection;
import com.rockset.client.model.CreateCollectionRequest;
import com.rockset.client.model.CreateCollectionResponse;
import com.rockset.client.model.CreateWorkspaceRequest;
import com.rockset.client.model.CreateWorkspaceResponse;

import com.rockset.client.model.ErrorModel;
import com.rockset.client.model.GetCollectionResponse;
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
      client.createWorkspace(request);
      LOGGER.info(String.format("Created workspace %s", workspace));
    } catch (ApiException e) {
      if (e.getCode() == 400 && e.getErrorModel().getType() == ErrorModel.TypeEnum.ALREADYEXISTS) {
        LOGGER.info(String.format("Workspace %s already exists", workspace));
        return;
      }

      throw e;
    }
  }

  // Assumes the workspace exists
  public static void createCollectionIfNotExists(RocksetClient client, String workspace, String cname) throws Exception {
    CreateCollectionRequest request = new CreateCollectionRequest().name(cname);
    try {
      client.createCollection(workspace, request);
      LOGGER.info(String.format("Created collection %s.%s", workspace, cname));
    } catch (ApiException e) {
      if (e.getCode() == 400 && e.getErrorModel().getType() == ErrorModel.TypeEnum.ALREADYEXISTS) {
        LOGGER.info(String.format("Collection %s.%s already exists", workspace, cname));
        return;
      }

      throw e;
    }
  }

  // Assumes the collection exists
  public static void waitUntilCollectionReady(RocksetClient client, String workspace, String cname) throws Exception {
    while (true) {
      GetCollectionResponse resp = client.getCollection(workspace, cname);
      Collection.StatusEnum status = resp.getData().getStatus();
      if (status == Collection.StatusEnum.READY) {
        LOGGER.info(String.format("Collection %s.%s is READY", workspace, cname));
        break;
      } else {
        LOGGER.info(String.format("Waiting until %s.%s is READY, it is %s", workspace, cname, status.toString()));
        Thread.sleep(5000);
      }
    }
  }
}
