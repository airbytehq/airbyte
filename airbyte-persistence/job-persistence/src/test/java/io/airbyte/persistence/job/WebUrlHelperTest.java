/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.persistence.job;

import java.util.UUID;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class WebUrlHelperTest {

  private static final UUID WORKSPACE_ID = UUID.randomUUID();
  private static final UUID CONNECTION_ID = UUID.randomUUID();
  private static final String LOCALHOST_8000 = "http://localhost:8000";

  @Test
  void testGetBaseUrl() {
    final WebUrlHelper webUrlHelper = new WebUrlHelper(LOCALHOST_8000);
    Assertions.assertEquals(LOCALHOST_8000, webUrlHelper.getBaseUrl());
  }

  @Test
  void testGetBaseUrlTrailingSlash() {
    final WebUrlHelper webUrlHelper = new WebUrlHelper("http://localhost:8001/");
    Assertions.assertEquals("http://localhost:8001", webUrlHelper.getBaseUrl());
  }

  @Test
  void testGetWorkspaceUrl() {
    final WebUrlHelper webUrlHelper = new WebUrlHelper(LOCALHOST_8000);
    final String workspaceUrl = webUrlHelper.getWorkspaceUrl(WORKSPACE_ID);
    final String expectedUrl = String.format("http://localhost:8000/workspaces/%s", WORKSPACE_ID);
    Assertions.assertEquals(expectedUrl, workspaceUrl);
  }

  @Test
  void testGetConnectionUrl() {
    final WebUrlHelper webUrlHelper = new WebUrlHelper(LOCALHOST_8000);
    final String connectionUrl = webUrlHelper.getConnectionUrl(WORKSPACE_ID, CONNECTION_ID);
    final String expectedUrl = String.format("http://localhost:8000/workspaces/%s/connections/%s", WORKSPACE_ID, CONNECTION_ID);
    Assertions.assertEquals(expectedUrl, connectionUrl);
  }

}
