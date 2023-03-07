/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.persistence.job;

import java.util.UUID;

public class WebUrlHelper {

  private final String webAppUrl;

  public WebUrlHelper(final String webAppUrl) {
    this.webAppUrl = webAppUrl;
  }

  public String getBaseUrl() {
    if (webAppUrl.endsWith("/")) {
      return webAppUrl.substring(0, webAppUrl.length() - 1);
    }

    return webAppUrl;
  }

  public String getWorkspaceUrl(final UUID workspaceId) {
    return String.format("%s/workspaces/%s", getBaseUrl(), workspaceId);
  }

  public String getConnectionUrl(final UUID workspaceId, final UUID connectionId) {
    return String.format("%s/connections/%s", getWorkspaceUrl(workspaceId), connectionId);
  }

}
