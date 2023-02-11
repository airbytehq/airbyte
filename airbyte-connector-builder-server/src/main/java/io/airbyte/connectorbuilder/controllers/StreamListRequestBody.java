/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.connectorbuilder.controllers;

import java.util.Map;

public class StreamListRequestBody {

  public Map<String, Object> manifest;
  public Map<String, Object> config;

}
