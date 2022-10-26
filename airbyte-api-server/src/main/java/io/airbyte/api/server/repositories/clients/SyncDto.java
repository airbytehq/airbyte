/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.api.server.repositories.clients;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

public class SyncDto {

  String connectionId;

  @JsonProperty("connectionId")
  public String getConnectionId() {
    return connectionId;
  }

  @JsonCreator
  public SyncDto(@JsonProperty("connectionId") final String connectionId) {
    this.connectionId = connectionId;
  }

  public void setConnectionId(final String connectionId) {
    this.connectionId = connectionId;
  }

}
